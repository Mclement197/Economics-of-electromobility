// Presentation model only. No prices, infrastructure costs or commercial defaults.
const keys = ['N', 'O', 'P', 'S', 'R'];
const labels = {N:'Wohnungen', O:'Belegte Wohnungen', P:'Ladepunkte', S:'Abonnement', R:'Mietaufschlag'};
const isBlank = value => value === undefined || value === null || String(value).trim() === '';
export function validateInputs(raw) {
  const values = {}, errors = {};
  for (const key of keys) {
    if (isBlank(raw[key])) {
      values[key] = null;
      if (['N', 'O', 'P'].includes(key)) errors[key] = 'Bitte eine ganze Anzahl eingeben.';
      continue;
    }
    const value = typeof raw[key] === 'number' ? raw[key] : Number(String(raw[key]).trim());
    values[key] = value;
    if (!Number.isFinite(value)) errors[key] = 'Bitte eine gültige Zahl eingeben.';
    else if (['N', 'O', 'P'].includes(key) && !Number.isSafeInteger(value)) errors[key] = 'Bitte eine ganze, darstellbare Anzahl eingeben.';
    else if (value < (key === 'N' || key === 'P' ? 1 : 0)) errors[key] = key === 'N' || key === 'P' ? 'Mindestens 1 erforderlich.' : 'Negative Eingaben sind nicht möglich.';
  }
  if (!errors.N && values.N !== null) {
    if (!errors.O && values.O !== null && values.O > values.N) errors.O = 'Belegte Wohnungen dürfen die Gesamtzahl nicht überschreiten. Bitte diesen Wert selbst anpassen.';
    if (!errors.P && values.P !== null && values.P > values.N) errors.P = 'Ladepunkte dürfen in diesem Beispiel die Wohnungszahl nicht überschreiten. Bitte selbst anpassen.';
  }
  const countsValid = ['N','O','P'].every(key => !errors[key] && values[key] !== null);
  const hasMoney = values.S !== null && values.R !== null;
  if (countsValid && hasMoney && Object.keys(errors).length === 0) {
    for (const [key, count] of [['S', values.N], ['R', values.O]]) {
      if (!Number.isFinite(values[key] * count) || Math.abs(values[key] * count) > Number.MAX_SAFE_INTEGER / 100) errors[key] = 'Dieser Betrag ist für eine verlässliche CHF-Darstellung zu gross.';
    }
  }
  return {values, errors, countsValid, hasMoney, valid:Object.keys(errors).length === 0};
}
export function computeScenario(raw) {
  const validation = validateInputs(raw);
  if (!validation.valid || !validation.hasMoney) return {...validation, results:null};
  const {N,O,S,R} = validation.values;
  const rentalIncome = O * R;
  const scenario = billable => ({billable, subscription:billable * S, contribution:rentalIncome - billable * S});
  return {...validation, results:{rentalIncome, continue:scenario(N), pause:scenario(O)}};
}
const chf = new Intl.NumberFormat('de-CH', {style:'currency', currency:'CHF', minimumFractionDigits:2, maximumFractionDigits:2});
const countFormat = new Intl.NumberFormat('de-CH');
export function mountCalculator(root = document) {
  const calculator = root.querySelector('#building-calculator');
  if (!calculator) return;
  const el = id => calculator.querySelector(`#${id}`);
  const controls = Object.fromEntries(keys.map(key => [key, el(`calc-${key}`)]));
  function drawDots(target, count, occupied) {
    const nodes = [];
    for (let i=0;i<Math.min(count,40);i++) {
      const dot = document.createElement('span');
      dot.className = occupied === undefined ? 'calc-charge' : i < occupied ? 'calc-apartment is-occupied' : 'calc-apartment';
      nodes.push(dot);
    }
    if (count > 40) {
      const more = document.createElement('span');
      more.className = 'calc-more'; more.textContent = `+${countFormat.format(count - 40)}`; nodes.push(more);
    }
    target.replaceChildren(...nodes);
  }
  function update() {
    const raw = Object.fromEntries(keys.map(key => [key, controls[key].value]));
    const state = computeScenario(raw);
    for (const key of keys) {
      // type=number can expose an empty value for a partial invalid entry.
      if (controls[key].validity.badInput) state.errors[key] = 'Bitte eine gültige Zahl eingeben.';
      const error = state.errors[key] || '';
      controls[key].setAttribute('aria-invalid', String(Boolean(error)));
      el(`calc-${key}-error`).textContent = error;
    }
    const errors = Object.entries(state.errors);
    if (state.countsValid && !['N','O','P'].some(key => state.errors[key])) {
      const {N,O,P} = state.values;
      el('calc-building-count').textContent = `${countFormat.format(N)} Wohnungen · ${countFormat.format(O)} belegt`;
      el('calc-vacant-count').textContent = `${countFormat.format(N-O)} leer`;
      drawDots(el('calc-apartments'), N, O);
      drawDots(el('calc-chargers'), P);
      el('calc-charger-count').textContent = `${countFormat.format(P)} geteilte Ladepunkte`;
      el('calc-count-note').textContent = O === N
        ? `Illustratives Beispiel bei Vollvermietung: ${countFormat.format(N)} Wohnungen, ${countFormat.format(P)} Ladepunkte, ${countFormat.format(N)} Abonnements. Abonnements gelten pro abrechnungspflichtiger Wohnung, nicht pro Ladepunkt.`
        : `Illustratives Beispiel: ${countFormat.format(N)} Wohnungen, ${countFormat.format(P)} Ladepunkte. Szenario A: ${countFormat.format(N)} Abonnements; Szenario B: ${countFormat.format(O)}. Das Abonnement gilt pro abrechnungspflichtiger Wohnung, nicht pro Ladepunkt.`;
    } else {
      el('calc-building-count').textContent = 'Gebäudeangaben prüfen';
      el('calc-vacant-count').textContent = '';
      el('calc-apartments').replaceChildren(); el('calc-chargers').replaceChildren();
      el('calc-charger-count').textContent = 'Darstellung nach Korrektur verfügbar';
      el('calc-count-note').textContent = 'Die Eingaben bleiben erhalten. Passen Sie belegte Wohnungen und Ladepunkte bei Bedarf selbst an die Gesamtzahl an.';
    }
    const show = errors.length === 0 && Boolean(state.results);
    el('calc-financials').hidden = !show;
    el('calc-status').textContent = errors.length ? `Bitte Eingaben korrigieren: ${errors.map(([key])=>labels[key]).join(', ')}. Die Berechnung ist bis dahin pausiert.` : !state.hasMoney ? 'Geben Sie beide Geldbeträge ein, um die monatlichen Ergebnisse zu sehen. Leere Felder zählen nicht als null.' : 'Beide Leerstandsregeln, mit denselben Annahmen berechnet.';
    if (show) {
      el('calc-rental-income').textContent = chf.format(state.results.rentalIncome);
      for (const scenario of ['continue','pause']) {
        const result = state.results[scenario];
        el(`calc-${scenario}-count`).textContent = `${countFormat.format(result.billable)} abrechnungspflichtige Wohnungen`;
        el(`calc-${scenario}-subscription`).textContent = chf.format(result.subscription);
        el(`calc-${scenario}-contribution`).textContent = chf.format(result.contribution);
        el(`calc-${scenario}-contribution`).classList.toggle('is-negative', result.contribution < 0);
      }
    }
  }
  Object.values(controls).forEach(input => input.addEventListener('input', update));
  update();
}
if (typeof document !== 'undefined') mountCalculator();
