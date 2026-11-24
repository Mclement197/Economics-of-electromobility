// Native PDF and browser slides now share the editable PPTX renderer.
// Set PRESENTATION_PYTHON to a python-pptx venv and LIBREOFFICE to Impress.
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const r=spawnSync(process.env.PRESENTATION_PYTHON||'python3',[fileURLToPath(new URL('./export-presentation.py',import.meta.url)),...process.argv.slice(2)],{stdio:'inherit',env:process.env});
if(r.error)throw r.error;process.exit(r.status??1);
