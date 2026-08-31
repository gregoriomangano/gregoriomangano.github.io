(() => {
  const button = document.querySelector('[data-copy-iban]');
  const status = document.querySelector('.copy-status');
  if (!button || !status) return;
  button.addEventListener('click', async () => {
    const iban = button.dataset.copyIban;
    try {
      await navigator.clipboard.writeText(iban);
      status.textContent = 'IBAN copiato.';
    } catch {
      const field = document.createElement('textarea');
      field.value = iban;
      field.setAttribute('readonly', '');
      field.style.position = 'fixed';
      field.style.opacity = '0';
      document.body.append(field);
      field.select();
      document.execCommand('copy');
      field.remove();
      status.textContent = 'IBAN copiato.';
    }
    window.setTimeout(() => { status.textContent = ''; }, 2600);
  });
})();
