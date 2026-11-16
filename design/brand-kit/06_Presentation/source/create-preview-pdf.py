from pathlib import Path
from reportlab.pdfgen import canvas

out = Path(__file__).resolve().parents[1]
pdf = out / 'VoltoShare_Presentation_Starter_Preview.pdf'
c = canvas.Canvas(str(pdf), pagesize=(960, 540), pageCompression=1)
c.setTitle('VoltoShare | Presentation Starter Preview')
c.setAuthor('VoltoShare project team')
c.setSubject('Six widescreen slides. Edit the accompanying PPTX.')
for i in range(1, 7):
    c.drawImage(str(out / f'previews/slide-{i:02d}.png'), 0, 0, width=960, height=540)
    c.showPage()
c.save()
print(pdf)
