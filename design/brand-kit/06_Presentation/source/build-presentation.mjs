import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const sourceDir=path.dirname(fileURLToPath(import.meta.url));
const kit=path.resolve(sourceDir,'../..');
const out=path.join(kit,'06_Presentation');
const draft=path.join(out,'source','build-output');
const FONT='Liberation Sans';
const C={green:'#28563B',graphite:'#23262B',ink:'#1E2023',warm:'#F8F5F0',white:'#FFFFFF',tint:'#EAF0EB',muted:'#666E68',line:'#DCE2DD'};
await fs.mkdir(draft,{recursive:true});
await fs.mkdir(path.join(out,'previews'),{recursive:true});
const p=Presentation.create({slideSize:{width:1280,height:720}});
const logoPath=path.join(kit,'07_References/KI-generiert.png');
const markPath=path.join(kit,'07_References/Gemini_Generated_Image_q1lwv6q1lwv6q1lw2.jpg');
const logoBytes=new Uint8Array(await fs.readFile(logoPath));
const markBytes=new Uint8Array(await fs.readFile(markPath));
const garageBytes=new Uint8Array(await fs.readFile(path.join(kit,'03_Images/voltoshare-charger-garage.jpg')));
const nfcBytes=new Uint8Array(await fs.readFile(path.join(kit,'03_Images/voltoshare-nfc-card.jpg')));

function text(slide,name,copy,x,y,w,h,size=28,color=C.ink,bold=false){
 const s=slide.shapes.add({name,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});
 s.text=copy;s.text.style={typeface:FONT,fontSize:size,color,bold,alignment:'left',verticalAlignment:'top',insets:0,wrap:'square',autoFit:'none'};return s;
}
function rule(slide,y,x=72,w=1136,color=C.line){slide.shapes.add({name:'rule-'+y,geometry:'rect',position:{left:x,top:y,width:w,height:1},fill:color,line:{style:'solid',fill:'none',width:0}});}
function logo(slide,x=72,y=39,w=230){return slide.images.add({blob:logoBytes,contentType:'image/png',alt:'Original VoltoShare logo with German tagline supplied by the project team',fit:'contain',position:{left:x,top:y,width:w,height:w/4.72},crop:{left:.141,top:.365,right:.14,bottom:.363}});}
function standard(title,n){const slide=p.slides.add();slide.background.fill=C.white;logo(slide);text(slide,'slide-number',String(n).padStart(2,'0'),1168,47,40,30,17,C.muted);text(slide,'title',title,72,128,1136,74,52,C.ink,true);return slide;}
function note(slide,s){slide.speakerNotes.text=s;}
function table(slide,values,x,y,w,h,widths,pad=14){
 const t=slide.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});
 t.styleOptions={headerRow:true,bandedRows:false};
 t.borders.assign({style:'solid',fill:C.line,width:1});
 const whole=t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length});
 whole.assign({fill:C.white,textStyle:{typeface:FONT,fontSize:24,color:C.ink},margins:{top:pad,bottom:pad,left:18,right:18},anchor:'center'});
 for(let r=0;r<values.length;r++)for(let col=0;col<values[0].length;col++){
  const cell=t.getCell(r,col);cell.text.style={typeface:FONT,fontSize:r===0?20:24,color:r===0?C.white:C.ink,bold:r===0,verticalAlignment:'middle',insets:pad};cell.fill=r===0?C.green:(r%2===0?C.warm:C.white);
 }
 return t;
}

// 1. Cover: original artwork and supplied concept photograph.
{
 const s=p.slides.add();s.background.fill=C.white;
 s.images.add({blob:garageBytes,contentType:'image/jpeg',alt:'VoltoShare charger in an apartment-building garage, supplied concept visual',fit:'cover',position:{left:605,top:0,width:675,height:720},crop:{left:.24,top:0,right:0,bottom:0}});
 logo(s,72,64,360);
 text(s,'cover-title','Shared charging\nfor apartment\nbuildings',72,244,495,238,62,C.ink,true);
 text(s,'course-name','Ökonomie der Elektromobilität',72,583,470,40,23,C.green,true);
 text(s,'cover-subtitle','VoltoShare project proposal',72,624,470,34,22,C.muted);
 note(s,'Source: supplied VoltoShare_Expose_DE(1).pdf, 15 October 2026, page 1, sections 1-3. The proposed service finances, installs and operates shared charging points for apartment buildings. Image: supplied Gemini_Generated_Image_q1lwv6q1lwv6q1lw6.jpg, concept visual rather than proof of an operational installation. Logo: supplied , KI-generiert.png, original artwork preserved. This six-slide file is an editable presentation starter.');
}

// 2. Service example with editable numbers and labels.
{
 const s=standard('Shared charging for one building',2);
 text(s,'service-description','VoltoShare finances, installs and operates shared charging points.',72,218,1080,70,29,C.muted);
 const data=[['20','apartments'],['5','shared charging points'],['20','subscriptions']];
 for(let i=0;i<3;i++){
  const x=72+i*386;
  text(s,'metric-'+i,data[i][0],x,333,320,126,112,C.green,true);
  text(s,'metric-label-'+i,data[i][1],x,469,330,48,29,C.ink,true);
 }
 rule(s,552);
 text(s,'example-caption','Proposal example at full occupancy',72,576,690,35,24,C.green,true);
 text(s,'billing-unit','Subscription billing is per apartment.',72,620,1000,32,23,C.muted);
 note(s,'Source: supplied VoltoShare_Expose_DE(1).pdf, page 1, section 1 and the highlighted 20 apartments / 5 shared charging points / 20 subscriptions example. The source describes full occupancy and states subscriptions apply per apartment, not per charging point. This example is neither an operating deployment nor a universal charger-sizing recommendation. All numbers and labels are editable.');
}

// 3. Native editable table showing the two payers.
{
 const s=standard('Two distinct payment streams',3);
 table(s,[['Payer','Payment','What it covers'],['Landlord or\nproperty manager','Monthly subscription\nper billable apartment','Infrastructure\nand platform'],['Residents','Measured electricity\nat the dynamic tariff','Energy plus\nprovider markup']],72,236,1136,278,[360,430,346]);
 text(s,'operation-note','VoltoShare provides hardware, software and ongoing maintenance.',72,551,1090,60,27,C.ink);
 text(s,'vacancy-note','Vacancy billing remains open: subscriptions may continue or pause.',72,634,1136,35,22,C.muted);
 note(s,'Source: supplied VoltoShare_Expose_DE(1).pdf, page 1, section 2 for payer and revenue structure, section 3 for operating responsibility, and final vacancy note for the unresolved billing rule. Electricity revenue and electricity margin are different concepts. The landlord subscription is not automatically a line on resident electricity invoices. The table is a native editable PowerPoint table.');
}

// 4. Resident journey and supplied NFC card concept visual.
{
 const s=standard('Resident experience',4);
 const items=[['Find a charger','View availability and the parking plan.'],['Reserve a time','Choose a charger and household vehicle.'],['Access charging','Use the app or a supported NFC card.'],['Track costs','Review measured energy and invoices.']];
 for(let i=0;i<items.length;i++){
  const y=226+i*94;
  text(s,'step-number-'+i,String(i+1).padStart(2,'0'),72,y+4,52,38,22,C.green,true);
  text(s,'step-title-'+i,items[i][0],132,y,520,40,28,C.ink,true);
  text(s,'step-body-'+i,items[i][1],132,y+43,535,49,24,C.muted);
 }
 s.images.add({blob:nfcBytes,contentType:'image/jpeg',alt:'Supplied VoltoShare NFC access-card concept visual',fit:'contain',position:{left:721,top:237,width:487,height:355},crop:{left:.24,top:.20,right:.23,bottom:.18}});
 text(s,'concept-caption','NFC access-card concept',744,617,440,32,19,C.muted);
 note(s,'Sources: supplied VoltoShare_Expose_DE(1).pdf, page 1, section 3 for reservations and app/NFC access. The user brief adds household vehicles, map, consumption history and invoices. Image: supplied Gemini_Generated_Image_q1lwv6q1lwv6q1lw5.jpg, concept visual. Availability, reservation and physical parking occupancy need distinct states in the app.');
}

// 5. Native editable economic-input table with explicit unknowns.
{
 const s=standard('Economics to validate',5);
 text(s,'economic-intro','The commercial proposal leaves these inputs open.',72,212,1136,48,28,C.muted);
 table(s,[['Input','Unit or policy','Assumption'],['Apartment subscription','CHF / apartment / month','To be confirmed'],['Provider energy markup','CHF / kWh','To be confirmed'],['Hardware and installation','CHF, initial investment','To be confirmed'],['Operating costs','CHF / month','To be confirmed'],['Vacancy billing','Continue or pause','To be confirmed']],72,290,1136,334,[390,390,356],10);
 text(s,'economic-limit','Profitability depends on demand, utilisation and the full cost structure.',72,657,1136,30,22,C.muted);
 note(s,'Source: supplied VoltoShare_Expose_DE(1).pdf, page 1, sections 2 and 5 and final vacancy note. The proposal supplies no subscription price, energy markup, installed cost, operating cost, verified rent premium or return. Cells intentionally say To be confirmed so the team can insert its own substantiated assumptions. Units and assumptions are editable in a native PowerPoint table. No numeric return is implied.');
}

// 6. Closing with the supplied monochrome symbol.
{
 const s=p.slides.add();s.background.fill='#000000';
 text(s,'closing-title','Questions',72,246,600,100,78,C.white,true);
 text(s,'closing-subtitle','Shared charging for\napartment buildings',72,378,615,105,32,C.white);
 text(s,'closing-name','VoltoShare',72,618,600,40,25,C.white,true);
 s.images.add({blob:markBytes,contentType:'image/jpeg',alt:'Original white VoltoShare continuous V/loop mark on black',fit:'contain',position:{left:758,top:155,width:450,height:450},crop:{left:.155,top:.17,right:.15,bottom:.15}});
 note(s,'Original mark: supplied Gemini_Generated_Image_q1lwv6q1lwv6q1lw2.jpg. Monochrome black and white treatment follows the supplied reference. This closing slide is editable and can be used for discussion.');
}

const stem='VoltoShare_Presentation_Starter';
const finalPath=path.join(out,stem+'.pptx');
await (await PresentationFile.exportPptx(p)).save(finalPath);
for(let i=0;i<p.slides.items.length;i++){
 const png=await p.export({slide:p.slides.items[i],format:'png',scale:1.5});
 await fs.writeFile(path.join(out,'previews',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
try { const pdf=await p.export({format:'pdf'}); await fs.writeFile(path.join(out,stem+'_Vector_Preview.pdf'),new Uint8Array(await pdf.arrayBuffer())); } catch (err) { await fs.writeFile(path.join(draft,'pdf-export-error.txt'),String(err?.stack || err)); console.log('PDF_EXPORT_FAILED',String(err?.message || err).slice(0,500)); }
const montage=await p.export({format:'webp',montage:true,scale:.75});
await fs.writeFile(path.join(draft,'montage.webp'),new Uint8Array(await montage.arrayBuffer()));
await fs.writeFile(path.join(draft,'source.json'),JSON.stringify(p.toProto(),null,2));
console.log(JSON.stringify({finalPath,slides:p.slides.items.length}));
