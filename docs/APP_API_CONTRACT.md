# Tenant app implementation contract

Latest user app brief overrides older kit logic: English, real database state, relative-date seed, flat illustrative tariff, shared household invoice visibility. UI uses existing brand design.

## API

All JSON responses use `{ok:true,...}` or `{ok:false,error:"Useful error",fields:{...}}`. CSRF cookie `csrftoken` must be sent as `X-CSRFToken` on every POST. Session-based Django authentication. Login page `/login/`, app `/`, invoice printable `/invoices/<id>/print/`, CSV `/api/history.csv?month=YYYY-MM&vehicle=ID`.

GET `/api/state/` response `{ok:true,user:{id,name,email},role:"owner"|"member",household:{id,name,apartment},property:{id,name,timezone,currency,booking_increment:30,min_minutes:30,max_minutes:480,horizon_days:30},demo:true,now:ISO,vehicles:[],members:[],reservations:[],sessions:[],invoices:[],chargers:[],bays:[],occupancy:[],invitations:[]}`.

- vehicle: `{id,name,plate,make_model,driver_id,driver_name,connector,battery_kwh,archived}`
- member: `{id,user_id,name,email,role}`; id = membership ID, active only
- reservation: `{id,charger_id,bay,charger_name,vehicle_id,vehicle_name,creator_name,start,end,status}`; stored status `active` or `cancelled`. Ended intervals are NOT charging sessions. Own household only.
- session: `{id,charger_id,bay,vehicle_id,vehicle_name,driver_name,start,end,energy_kwh,tariff_chf,cost_cents,status,invoice_id}` status `completed` or `active`; immutable historical vehicle name snapshots.
- invoice: `{id,number,period,issued_at,due_date,total_cents,status,paid_at,overdue,lines:[]}`; status stored `paid`|`unpaid`; lines `{id,session_id,date,vehicle,charger,bay,energy_kwh,tariff_chf,cost_cents}`; due_date YYYY-MM-DD.
- charger: `{id,name,bay,connector,max_power_kw,status,updated_at,tariff_chf,occupancy:"unknown",stale:false}` operational status `available`|`charging`|`offline`|`unknown`; reservation status separate.
- bay: `{id,label,row,column,charger_id}` row0 or1, column0..9.
- occupancy: `{charger_id,start,end,kind:"reservation"|"session",own:bool}` anonymous intervals across households; no foreign IDs/names/vehicles, session may have estimated/unconfirmed end; active charging must not block every future interval.
- invitation: `{id,email,expires_at,used,revoked}` owner only; raw token never returned again after creation.

POST `/api/reservations/` JSON `{charger_id,vehicle_id,start,end,request_id}`. Datetime inputs either local ISO `YYYY-MM-DDTHH:mm` interpreted in property zone (ambiguous/nonexistent local times rejected), or explicit offset ISO. Return `{ok:true,reservation_id}`. POST `/api/reservations/<id>/change/` same body including request_id; POST `.../cancel/` {}. Duplicate request IDs idempotent.
POST `/api/vehicles/` JSON `{name,plate,make_model,driver_id,connector,battery_kwh}` (driver_id is user ID); POST `/api/vehicles/<id>/change/` same; POST `.../archive/` {}. Return vehicle_id. Archive blocked if future reservations exist.
POST `/api/household/` JSON `{name}` owner only.
POST `/api/invitations/` JSON `{email}` owner only -> `{ok:true,url,expires_at}` copy link, NOT email sent. Existing account sign-in or invitation-only registration at returned server-rendered URL; email-bound, one-use expiring hashed tokens. POST `/api/invitations/<id>/revoke/` {}.
POST `/api/members/<membership_id>/remove/` {} owner only; cannot remove last owner.
POST `/logout/` form or fetch with CSRF; GET `/login/` renders established Django authentication plus explicit demo persona entry only in opted-in DEMO_MODE.

No tenant pay, reset, seed, invoice-generation, session-ingestion or hardware-control endpoints. Server CLI handles trusted setup, seeding/invoice generation. Frontend never uses local storage for records. Dates format in Europe/Zurich, daily totals by session END date. Dashboard counts non-cancelled reservations by START month, completed sessions independently. Outstanding all-period invoices irrespective of filter.
