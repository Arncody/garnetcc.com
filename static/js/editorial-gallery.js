(() => {
  const gallery = document.getElementById('project-gallery');
  const viewer = document.getElementById('project-gallery-viewer');
  if (!gallery || typeof viewer?.showModal !== 'function') return;

  const items = [...gallery.querySelectorAll('[data-gallery-image]')];
  if (!items.length) return;

  const stage = viewer.querySelector('[data-gallery-stage]');
  const photo = stage.querySelector('img');
  const caption = viewer.querySelector('[data-gallery-caption]');
  const note = viewer.querySelector('[data-gallery-note]');
  const position = viewer.querySelector('[data-gallery-position]');
  const rtl = document.documentElement.dir === 'rtl';
  const formatNumber = new Intl.NumberFormat(document.documentElement.lang);
  let index = 0;
  let opener;
  let backdropPress = false;
  let gesture;

  const show = (target) => {
    index = (target + items.length) % items.length;
    const item = items[index];
    const thumb = item.querySelector('img');
    const description = item.parentElement.querySelector('[data-gallery-description]');
    photo.src = thumb.currentSrc || thumb.src;
    photo.alt = thumb.alt;
    position.textContent = [formatNumber.format(index + 1), viewer.dataset.galleryTotalLabel,
      formatNumber.format(items.length)].join(' ');
    caption.textContent = thumb.alt;
    note.textContent = description?.textContent || '';
    note.hidden = !note.textContent;
  };

  items.forEach((item, itemIndex) => {
    item.setAttribute('aria-haspopup', 'dialog');
    item.addEventListener('click', (event) => {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = item;
      show(itemIndex);
      if (!viewer.open) viewer.showModal();
    });
  });

  const resetGesture = () => {
    gesture = undefined;
    stage.classList.remove('is-dragging');
    stage.style.removeProperty('--gallery-drag');
  };

  if (items.length > 1) {
    viewer.setAttribute('aria-describedby', 'gallery-navigation-help');
    position.hidden = false;
    stage.classList.add('is-interactive');

    viewer.addEventListener('keydown', (event) => {
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
      event.preventDefault();
      show(index + ((event.key === 'ArrowRight') !== rtl ? 1 : -1));
    });

    stage.addEventListener('pointerdown', (event) => {
      if (!event.isPrimary || event.button !== 0) return;
      gesture = { id: event.pointerId, x: event.clientX, y: event.clientY };
      stage.setPointerCapture(event.pointerId);
    });

    stage.addEventListener('pointermove', (event) => {
      if (!gesture || event.pointerId !== gesture.id) return;
      const dx = event.clientX - gesture.x;
      const dy = event.clientY - gesture.y;
      if (Math.abs(dx) < 8 || Math.abs(dx) <= Math.abs(dy)) {
        stage.classList.remove('is-dragging');
        stage.style.removeProperty('--gallery-drag');
        return;
      }
      stage.classList.add('is-dragging');
      stage.style.setProperty('--gallery-drag', `${dx * .32}px`);
    });

    stage.addEventListener('pointerup', (event) => {
      if (!gesture || event.pointerId !== gesture.id) return;
      const dx = event.clientX - gesture.x;
      const dy = event.clientY - gesture.y;
      resetGesture();
      if (Math.abs(dx) >= 40 && Math.abs(dx) > 1.25 * Math.abs(dy)) {
        show(index + ((dx < 0) !== rtl ? 1 : -1));
      } else if (Math.abs(dx) <= 8 && Math.abs(dy) <= 8) {
        const bounds = stage.getBoundingClientRect();
        const offset = (event.clientX - bounds.left) / bounds.width;
        if (offset >= 0 && offset <= .24) show(index + (rtl ? 1 : -1));
        else if (offset >= .76 && offset <= 1) show(index + (rtl ? -1 : 1));
      }
    });

    for (const type of ['pointercancel', 'lostpointercapture']) {
      stage.addEventListener(type, (event) => {
        if (event.pointerId === gesture?.id) resetGesture();
      });
    }
  }

  viewer.addEventListener('pointerdown', (event) => {
    backdropPress = event.target === viewer;
  });
  viewer.addEventListener('click', (event) => {
    if (backdropPress && event.target === viewer) viewer.close();
    backdropPress = false;
  });
  viewer.addEventListener('close', () => {
    resetGesture();
    photo.removeAttribute('src');
    opener?.focus({ preventScroll: true });
  });
})();
