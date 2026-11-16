import csv, hashlib, io, json, secrets
from contextlib import nullcontext
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from functools import wraps
from zoneinfo import ZoneInfo
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.core.validators import validate_email
from django.db import transaction, IntegrityError, OperationalError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .models import Property, Household, Membership, Invitation, Vehicle, Bay, Charger, Reservation, ChargingSession, Invoice
from .services import DomainError, book, cancel, archive_vehicle, current_tariff, active_session_until
User=get_user_model()

def success(**kwargs): return JsonResponse({'ok':True,**kwargs})
def error(message,status=400,fields=None): return JsonResponse({'ok':False,'error':str(message),'fields':fields or {}},status=status)
def username(user): return user.get_full_name() or user.username

def data(request):
    try:
        value=json.loads(request.body or b'{}')
        if not isinstance(value,dict): raise ValueError()
        return value
    except (ValueError,UnicodeDecodeError): raise DomainError('Please send a valid JSON object.')

def text(d,key,limit=120,required=True):
    v=d.get(key,'')
    if v is None: v=''
    if not isinstance(v,str): raise DomainError(f'{key.replace("_"," ").title()} must be text.')
    v=v.strip()
    if (required and not v) or len(v)>limit:raise DomainError(f'Please check {key.replace("_"," ")} (maximum {limit} characters).', {key:'Please enter a valid value.'})
    return v

def household_api(fn):
    @wraps(fn)
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:return error('Please sign in to continue.',401)
        try:
            with transaction.atomic() if request.method=='POST' else nullcontext():
                membership=Membership.objects.select_related('household__property').filter(user=request.user,active=True)
                selected=request.session.get('household_id')
                membership=membership.filter(household_id=selected).first() if selected else membership.first()
                if not membership:return error('Household access is no longer available. Sign out and contact the household owner.',403)
                request.member=membership;request.household=membership.household
                return fn(request,*args,**kwargs)
        except PermissionDenied as e:return error(str(e),403)
        except DomainError as e:return error(str(e),409,getattr(e,'fields',{}))
        except ObjectDoesNotExist:return error('This record is not available to your household.',404)
        except (ValidationError,ValueError,TypeError,InvalidOperation) as e:return error('Please check your input and try again.',400)
        except IntegrityError:return error('That operation conflicts with an existing record. Refresh and try again.',409)
        except OperationalError:return error('The service is busy. Please retry; your existing records are preserved.',503)
    return wrapper

def owner(request):
    if request.member.role!='owner':raise PermissionDenied('Only the household owner can manage membership or household details.')

def iso(d):return d.isoformat() if d else None

def vehicle_json(v):
    return {'id':v.id,'name':v.name,'plate':v.plate,'make_model':v.make_model,'driver_id':v.driver_id,'driver_name':username(v.driver) if v.driver else '', 'connector':v.connector,'battery_kwh':str(v.battery_kwh) if v.battery_kwh is not None else None,'archived':v.archived}

def reservation_json(r):return {'id':r.id,'charger_id':r.charger_id,'bay':r.charger.bay.label,'charger_name':r.charger.name,'vehicle_id':r.vehicle_id,'vehicle_name':r.vehicle.name,'creator_name':username(r.creator),'start':iso(r.start),'end':iso(r.end),'status':r.status}

def invoice_json(i,zone):
    lines=[{'id':l.id,'session_id':l.session_id,'date':iso(l.date),'vehicle':l.vehicle,'charger':l.charger,'bay':l.bay,'energy_kwh':str(l.energy_kwh),'tariff_chf':str(l.tariff_chf),'cost_cents':l.cost_cents} for l in i.lines.all()]
    return {'id':i.id,'household_name':i.household_name,'property_name':i.property_name,'apartment':i.apartment,'currency':i.currency,'number':i.number,'period':i.period,'issued_at':iso(i.issued_at),'due_date':iso(i.due_date),'total_cents':i.total_cents,'status':i.status,'paid_at':iso(i.paid_at),'overdue':i.status=='unpaid' and i.due_date<timezone.now().astimezone(ZoneInfo(zone)).date(),'lines':lines}

@ensure_csrf_cookie
@household_api
def state(request):
    if request.method!='GET':return error('Method not allowed.',405)
    h=request.household;p=h.property;now=timezone.now();z=ZoneInfo(p.timezone)
    tariff=current_tariff(p)
    vehicles=[vehicle_json(v) for v in Vehicle.objects.filter(household=h).select_related('driver')]
    reservations=[reservation_json(r) for r in Reservation.objects.filter(household=h).select_related('charger__bay','vehicle','creator').order_by('-start')]
    invoices=list(Invoice.objects.filter(household=h).prefetch_related('lines').order_by('-period'))
    session_invoices={l.session_id:i.id for i in invoices for l in i.lines.all()}
    sessions=[{'id':s.id,'charger_id':s.charger_id,'bay':s.charger.bay.label,'vehicle_id':s.vehicle_id,'vehicle_name':s.vehicle_name,'driver_name':s.driver_name,'start':iso(s.start),'end':iso(s.end),'energy_kwh':str(s.energy_kwh),'tariff_chf':str(s.tariff_chf),'cost_cents':s.cost_cents,'status':s.status,'invoice_id':session_invoices.get(s.id)} for s in ChargingSession.objects.filter(household=h).select_related('charger__bay').order_by('-end','-start')]
    chargers=[]
    for c in Charger.objects.filter(property=p).select_related('bay'):
        # Mock provider is explicitly simulated; each read is a fresh mock observation.
        observed=now if settings.DEMO_MODE else c.updated_at
        stale=not observed or (now-observed).total_seconds()>120
        chargers.append({'id':c.id,'name':c.name,'bay':c.bay.label,'connector':c.connector,'max_power_kw':str(c.max_power_kw),'status':'unknown' if stale else c.status,'updated_at':iso(observed),'tariff_chf':str(tariff.rate_chf),'occupancy':'unknown','stale':stale})
    bays=[{'id':b.id,'label':b.label,'row':b.row,'column':b.column,'charger_id':next((c['id'] for c in chargers if c['bay']==b.label),None)} for b in Bay.objects.filter(property=p).order_by('row','column')]
    occupancy=[{'charger_id':r.charger_id,'start':iso(r.start),'end':iso(r.end),'kind':'reservation','own':r.household_id==h.id} for r in Reservation.objects.filter(charger__property=p,status='active',end__gt=now,start__lt=now+timedelta(days=p.horizon_days+1))]
    for c in Charger.objects.filter(property=p):
        until=active_session_until(c,now)
        if until:
            occupancy.append({'charger_id':c.id,'start':iso(now),'end':iso(until),'kind':'session','own':ChargingSession.objects.filter(charger=c,household=h,status='active').exists(),'estimated':True})
    members=[{'id':m.id,'user_id':m.user_id,'name':username(m.user),'email':m.user.email,'role':m.role} for m in Membership.objects.filter(household=h,active=True).select_related('user')]
    invites=[{'id':i.id,'email':i.email,'expires_at':iso(i.expires_at),'used':bool(i.used_at),'revoked':i.revoked} for i in Invitation.objects.filter(household=h).order_by('-id')] if request.member.role=='owner' else []
    return success(user={'id':request.user.id,'name':username(request.user),'email':request.user.email},role=request.member.role,household={'id':h.id,'name':h.name,'apartment':h.apartment},property={'id':p.id,'name':p.name,'timezone':p.timezone,'currency':p.currency,'booking_increment':p.booking_increment,'min_minutes':p.min_minutes,'max_minutes':p.max_minutes,'horizon_days':p.horizon_days},demo=settings.DEMO_MODE,now=iso(now),vehicles=vehicles,members=members,reservations=reservations,sessions=sessions,invoices=[invoice_json(i,p.timezone) for i in invoices],chargers=chargers,bays=bays,occupancy=occupancy,invitations=invites)

@require_POST
@household_api
def reservations(request,reservation_id=None):
    r=book(request.household,request.user,data(request),reservation_id=reservation_id)
    return success(reservation_id=r.id)

@require_POST
@household_api
def cancel_reservation(request,reservation_id):
    cancel(request.household,reservation_id);return success()

@require_POST
@household_api
def vehicles(request,vehicle_id=None):
    d=data(request)
    with transaction.atomic():
        v=Vehicle.objects.get(id=vehicle_id,household=request.household,archived=False) if vehicle_id else Vehicle(household=request.household)
        v.name=text(d,'name',100);v.plate=text(d,'plate',30);v.make_model=text(d,'make_model',120,False)
        connector=text(d,'connector',40)
        if connector not in ['Type 2','CCS','CHAdeMO','Type 1']:raise DomainError('Choose a supported connector type.')
        if v.pk and connector!=v.connector and Reservation.objects.filter(vehicle=v,status='active',end__gt=timezone.now()).exists():raise DomainError('Cancel or reassign upcoming bookings before changing this vehicle’s connector.')
        v.connector=connector
        driver=d.get('driver_id')
        if driver:
            m=Membership.objects.get(household=request.household,user_id=driver,active=True);v.driver=m.user
        else:v.driver=None
        capacity=d.get('battery_kwh')
        if capacity not in [None,'']:
            try:capacity=Decimal(str(capacity))
            except InvalidOperation:raise DomainError('Battery capacity must be a number.')
            if not capacity.is_finite() or capacity<=0 or capacity>1000:raise DomainError('Battery capacity must be positive and at most 1000 kWh.')
            v.battery_kwh=capacity
        else:v.battery_kwh=None
        v.full_clean();v.save()
    return success(vehicle_id=v.id)

@require_POST
@household_api
def archive(request,vehicle_id):archive_vehicle(request.household,vehicle_id);return success()

@require_POST
@household_api
def household(request):
    owner(request)
    with transaction.atomic():
        h=Household.objects.get(id=request.household.id);h.name=text(data(request),'name');h.save(update_fields=['name'])
    return success()

@require_POST
@household_api
def invitation_create(request):
    owner(request);email=text(data(request),'email',254).lower();validate_email(email)
    with transaction.atomic():
        if Membership.objects.filter(household=request.household,active=True,user__email__iexact=email).exists():raise DomainError('That person already belongs to your household.')
        if Invitation.objects.filter(household=request.household,revoked=False,used_at=None,expires_at__gt=timezone.now()).count()>=20:raise DomainError('Revoke an unused invitation before creating another (limit 20).')
        token=secrets.token_urlsafe(32);expires=timezone.now()+timedelta(hours=48)
        Invitation.objects.create(household=request.household,email=email,token_hash=hashlib.sha256(token.encode()).hexdigest(),expires_at=expires,revoked=False)
    return success(url=settings.APP_URL+'/invite/'+token+'/',expires_at=iso(expires))

@require_POST
@household_api
def invitation_revoke(request,invitation_id):
    owner(request)
    with transaction.atomic():
        i=Invitation.objects.get(id=invitation_id,household=request.household);i.revoked=True;i.save(update_fields=['revoked'])
    return success()

@require_POST
@household_api
def member_remove(request,membership_id):
    owner(request)
    with transaction.atomic():
        m=Membership.objects.get(id=membership_id,household=request.household,active=True)
        if m.role=='owner' and Membership.objects.filter(household=request.household,role='owner',active=True).count()<=1:raise DomainError('The last owner cannot be removed. A trusted administrator must transfer ownership first.')
        m.active=False;m.save(update_fields=['active'])
        Invitation.objects.filter(household=request.household,email__iexact=m.user.email,used_at=None,revoked=False).update(revoked=True)
    return success()

@household_api
def history_csv(request):
    month=request.GET.get('month','');vehicle=request.GET.get('vehicle','')
    sessions=ChargingSession.objects.filter(household=request.household,status='completed').select_related('charger__bay')
    if vehicle:sessions=sessions.filter(vehicle_id=vehicle)
    out=io.StringIO();writer=csv.writer(out);writer.writerow(['End (Europe/Zurich)','Vehicle','Driver','Charger','Bay','Energy kWh','Tariff CHF/kWh','Cost CHF'])
    def safe(v):
        value=str(v)
        return "'"+value if value.startswith(('=','+','-','@','\t','\r')) else value
    for s in sessions.order_by('-end'):
        end=s.end.astimezone(ZoneInfo(request.household.property.timezone))
        if month and end.strftime('%Y-%m')!=month:continue
        writer.writerow([end.isoformat(),safe(s.vehicle_name),safe(s.driver_name),safe(s.charger.name),s.charger.bay.label,str(s.energy_kwh),str(s.tariff_chf),f'{s.cost_cents/100:.2f}'])
    r=HttpResponse(out.getvalue(),content_type='text/csv; charset=utf-8');r['Content-Disposition']='attachment; filename="voltoshare-charging-history.csv"';return r

@household_api
def invoice_print(request,invoice_id):
    i=Invoice.objects.prefetch_related('lines').get(id=invoice_id,household=request.household)
    payload=invoice_json(i,request.household.property.timezone)
    for line in payload['lines']:line['amount']=f"{line['cost_cents']/100:.2f}"
    return render(request,'invoice.html',{'invoice':i,'details':payload,'total':f'{i.total_cents/100:.2f}','demo':settings.DEMO_MODE})

@ensure_csrf_cookie
def app(request):
    if not request.user.is_authenticated:return redirect('/login/')
    if not Membership.objects.filter(user=request.user,active=True).exists():return render(request,'no_access.html',{'demo':settings.DEMO_MODE},status=403)
    return render(request,'app.html',{'demo':settings.DEMO_MODE})

def next_url(request):
    value=request.GET.get('next') or request.POST.get('next') or '/'
    return value if url_has_allowed_host_and_scheme(value,{request.get_host()},require_https=request.is_secure()) else '/'

@ensure_csrf_cookie
def login_view(request):
    form=AuthenticationForm(request,data=request.POST if request.method=='POST' else None)
    if request.method=='POST' and form.is_valid():
        login(request,form.get_user());request.session.pop('household_id',None);return redirect(next_url(request))
    return render(request,'login.html',{'form':form,'demo':settings.DEMO_MODE,'next':next_url(request)})

@require_POST
def demo_login(request):
    if not settings.DEMO_MODE:return error('Demo sign-in is disabled.',404)
    persona=request.POST.get('persona')
    if persona not in ['alex','sam','jordan','taylor']:return error('Unknown demo persona.')
    user=User.objects.filter(username=persona,is_active=True).first()
    if not user:return error('Demo data has not been seeded.',503)
    # Seeded demos have unusable passwords; production disables this endpoint entirely.
    if user.has_usable_password():return error('This account is not a demo persona.',403)
    login(request,user,backend='django.contrib.auth.backends.ModelBackend');request.session.pop('household_id',None)
    return redirect(next_url(request))

@require_POST
def logout_view(request):logout(request);return redirect('/login/')

@ensure_csrf_cookie
def invite_accept(request,token):
    if len(token)>100:return render(request,'invite_invalid.html',status=404)
    digest=hashlib.sha256(token.encode()).hexdigest()
    invitation=Invitation.objects.filter(token_hash=digest).select_related('household').first()
    if not invitation or invitation.used_at or invitation.revoked or invitation.expires_at<=timezone.now():return render(request,'invite_invalid.html',status=410)
    form=UserCreationForm(request.POST if request.method=='POST' and not request.user.is_authenticated else None)
    message=''
    if request.method=='POST':
        with transaction.atomic():
            invitation=Invitation.objects.select_related('household').get(id=invitation.id)
            if invitation.used_at or invitation.revoked or invitation.expires_at<=timezone.now():return render(request,'invite_invalid.html',status=410)
            user=request.user if request.user.is_authenticated else None
            if user and user.email.casefold()!=invitation.email.casefold():message='Sign in with the account matching this invitation, or sign out to register it.'
            elif not user and User.objects.filter(email__iexact=invitation.email).exists():message='An account already uses this invited email. Sign in with that account first.'
            elif not user and not form.is_valid():message='Please check the registration fields below.'
            else:
                if not user:
                    user=form.save(commit=False);user.email=invitation.email;user.first_name=request.POST.get('name','').strip()[:150];user.save()
                Membership.objects.update_or_create(user=user,household=invitation.household,defaults={'role':'member','active':True})
                invitation.used_at=timezone.now();invitation.save(update_fields=['used_at'])
                login(request,user,backend='django.contrib.auth.backends.ModelBackend');request.session['household_id']=invitation.household_id
                return redirect('/')
    return render(request,'invite.html',{'invitation':invitation,'form':form,'error':message,'demo':settings.DEMO_MODE,'next':request.path})

def health(request):return success(status='ready',demo=settings.DEMO_MODE)


def csrf_failure(request,reason=''):
    import logging
    logging.getLogger('voltoshare.csrf').warning('CSRF rejected: %s',reason)
    if request.path.startswith('/api/'):
        return error('Security token expired. Reload the page before retrying.',403)
    return HttpResponse('Security token could not be verified. Reload the sign-in page and try again.',status=403,content_type='text/plain')
