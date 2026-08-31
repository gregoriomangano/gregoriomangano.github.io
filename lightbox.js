(() => {
  const toggle = document.querySelector('.menu-toggle');
  const menu = document.querySelector('.mobile-menu');
  const hasGuide = container => [...container.querySelectorAll('a')].some(link => link.getAttribute('href')?.endsWith('guide/'));
  const desktopNav = document.querySelector('.main-nav');
  if (desktopNav && !hasGuide(desktopNav)) {
    const contact = desktopNav.querySelector('a[href$="#contatti"]');
    contact?.insertAdjacentHTML('beforebegin', '<a href="guide/">Guide</a>');
  }
  if (menu && !hasGuide(menu)) {
    const contact = menu.querySelector('a[href$="#contatti"]');
    contact?.insertAdjacentHTML('beforebegin', '<a href="guide/">Guide</a>');
  }
  const explore = [...document.querySelectorAll('.footer-grid nav')].find(nav => nav.querySelector('b')?.textContent.trim() === 'Esplora');
  if (explore && !hasGuide(explore)) {
    const contact = explore.querySelector('a[href$="#contatti"]');
    contact?.insertAdjacentHTML('beforebegin', '<a href="guide/">Guide</a>');
  }
  if (toggle && menu) {
    const closeMenu = () => { toggle.setAttribute('aria-expanded', 'false'); menu.hidden = true; document.body.classList.remove('menu-open'); };
    toggle.addEventListener('click', () => { const open = toggle.getAttribute('aria-expanded') === 'true'; if (open) closeMenu(); else { toggle.setAttribute('aria-expanded', 'true'); menu.hidden = false; document.body.classList.add('menu-open'); } });
    menu.addEventListener('click', event => { if (event.target.tagName === 'A') closeMenu(); });
    document.addEventListener('click', event => { if (!menu.hidden && !menu.contains(event.target) && !toggle.contains(event.target)) closeMenu(); });
    document.addEventListener('keydown', event => { if (event.key === 'Escape' && !menu.hidden) { closeMenu(); toggle.focus(); } });
  }
  const dialog = document.createElement('div');
  dialog.className = 'lightbox';
  dialog.innerHTML = '<button class="lightbox-close" aria-label="Chiudi immagine">×</button><div class="lightbox-stage"></div>';
  document.body.append(dialog);
  const stage = dialog.querySelector('.lightbox-stage');
  const close = () => { dialog.classList.remove('open'); stage.replaceChildren(); };
  document.addEventListener('click', event => {
    const trigger = event.target.closest('[data-lightbox]');
    if (trigger) { event.preventDefault(); const source = trigger.querySelector('img'); const image = new Image(); image.src = source.src; image.alt = source.alt; stage.replaceChildren(image); dialog.classList.add('open'); }
    if (event.target === dialog || event.target.closest('.lightbox-close')) close();
  });
  document.addEventListener('keydown', event => { if (event.key === 'Escape') close(); });
})();
