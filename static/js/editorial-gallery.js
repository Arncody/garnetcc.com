(() => {
  const dialog = document.getElementById('editorial-lightbox');
  if (!dialog?.showModal) return;

  const items = Array.from(document.querySelectorAll('[data-editorial-image]'));
  if (!items.length) return;

  const photo = dialog.querySelector('img');
  const caption = dialog.querySelector('p');
  const previous = dialog.querySelector('[data-gallery-prev]');
  const next = dialog.querySelector('[data-gallery-next]');
  const rtl = document.documentElement.dir === 'rtl';
  let trigger;
  let index = 0;

  const show = (position) => {
    index = (position + items.length) % items.length;
    const image = items[index].querySelector('img');
    photo.src = image.currentSrc || image.src;
    photo.alt = image.alt;
    caption.textContent = image.alt;
  };

  items.forEach((item, position) => {
    item.disabled = false;
    item.addEventListener('click', () => {
      trigger = item;
      show(position);
      dialog.showModal();
    });
  });

  if (items.length > 1) {
    previous.hidden = next.hidden = false;
    previous.addEventListener('click', () => show(index - 1));
    next.addEventListener('click', () => show(index + 1));
    dialog.addEventListener('keydown', (event) => {
      if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
      event.preventDefault();
      show(index + ((event.key === 'ArrowRight') !== rtl ? 1 : -1));
    });
  }

  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener('close', () => {
    photo.removeAttribute('src');
    trigger?.focus();
  });
})();
