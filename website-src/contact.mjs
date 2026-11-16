/** Local-only presentation enquiry. No storage, network request, or destination. */
export function initContact(root = document) {
  const form = root.getElementById('contact-form');
  if (!form) return;
  const submit = root.getElementById('contact-submit');
  const result = root.getElementById('contact-result');
  const summary = root.getElementById('contact-errors');
  const ids = ['name', 'email', 'role', 'organisation', 'location', 'apartments', 'message'];
  const fields = ids.map(id => root.getElementById(`contact-${id}`));
  function errorFor(field) {
    const value = field.value.trim();
    if (field.id === 'contact-name' && !value) return 'Bitte geben Sie einen fiktiven Namen ein.';
    if (field.id === 'contact-email' && (!value || field.validity.typeMismatch)) return 'Bitte geben Sie eine gültig formatierte Demo-E-Mail-Adresse ein.';
    if (field.id === 'contact-role' && !value) return 'Bitte wählen Sie Ihre Rolle aus.';
    if (field.id === 'contact-message' && !value) return 'Bitte ergänzen Sie eine kurze Beispielnachricht.';
    if (field.id === 'contact-apartments') {
      if (field.validity.badInput || (value && (!Number.isSafeInteger(Number(value)) || Number(value) < 1))) {
        return 'Bitte geben Sie eine ganze Wohnungszahl ab 1 ein oder lassen Sie das Feld leer.';
      }
    }
    if (field.maxLength > 0 && value.length > field.maxLength) return `Bitte verwenden Sie höchstens ${field.maxLength} Zeichen.`;
    return '';
  }
  function showError(field, message) {
    root.getElementById(`${field.id}-error`).textContent = message;
    field.setAttribute('aria-invalid', message ? 'true' : 'false');
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    result.hidden = true;
    const invalid = [];
    fields.forEach(field => {
      const error = errorFor(field);
      showError(field, error);
      if (error) invalid.push(field);
    });
    summary.hidden = invalid.length === 0;
    if (invalid.length) {
      summary.textContent = 'Bitte prüfen Sie die markierten Felder. Ihre Eingaben bleiben erhalten.';
      invalid[0].focus();
      return;
    }
    summary.textContent = '';
    result.hidden = false;
    result.focus();
  });
  fields.forEach(field => field.addEventListener('input', () => {
    result.hidden = true;
    if (field.getAttribute('aria-invalid') === 'true') showError(field, errorFor(field));
    if (!fields.some(input => input.getAttribute('aria-invalid') === 'true')) {
      summary.hidden = true;
      summary.textContent = '';
    }
  }));
  // Enable only after the preventDefault handler exists. Fields deliberately have
  // no name attributes, so accidental native form submissions contain no PII.
  submit.disabled = false;
}
if (typeof document !== 'undefined') initContact();
