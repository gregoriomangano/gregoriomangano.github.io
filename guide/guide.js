(() => {
  const cards = [...document.querySelectorAll('[data-guide-card]')];
  const filters = [...document.querySelectorAll('[data-guide-filter]')];
  const more = document.querySelector('.guide-more');
  let active = 'Tutte';
  let visible = 12;
  const update = () => {
    const matching = cards.filter(card => active === 'Tutte' || card.dataset.category === active);
    cards.forEach(card => { card.hidden = !matching.includes(card) || matching.indexOf(card) >= visible; });
    if (more) more.hidden = matching.length <= visible;
  };
  filters.forEach(button => button.addEventListener('click', () => { active = button.dataset.guideFilter; visible = 12; filters.forEach(item => item.setAttribute('aria-pressed', String(item === button))); update(); }));
  if (filters[0]) filters[0].setAttribute('aria-pressed', 'true');
  if (more) more.addEventListener('click', () => { visible += 12; update(); });
  update();
})();
