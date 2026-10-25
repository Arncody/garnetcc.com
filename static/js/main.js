document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('main-nav');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const closeNav = () => {
    if (!nav || !navToggle) return;
    nav.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  };

  if (navToggle && nav) {
    navToggle.addEventListener('click', (event) => {
      event.stopPropagation();
      const open = nav.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
    nav.querySelectorAll('a').forEach((a) => a.addEventListener('click', closeNav));
    document.addEventListener('click', (event) => {
      if (nav.classList.contains('open') && !nav.contains(event.target) && !navToggle.contains(event.target)) closeNav();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeNav();
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (event) => {
      const id = a.getAttribute('href');
      if (!id || id.length <= 1) return;
      const target = document.querySelector(id);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
      closeNav();
    });
  });

  window.addEventListener('scroll', () => {
    document.querySelector('.g-header')?.classList.toggle('scrolled', window.scrollY > 16);
  }, { passive: true });

  document.querySelectorAll('.site-toast').forEach((toast) => {
    window.setTimeout(() => {
      toast.style.transition = 'opacity .25s ease, transform .25s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-6px)';
      window.setTimeout(() => toast.remove(), 280);
    }, 5200);
  });

  // Consultation modal: one authoritative state machine, no native dialog/open attribute.
  const modal = document.getElementById('consultModal');
  if (!modal) return;
  if (modal.parentElement !== document.body) document.body.appendChild(modal);
  const closer = modal.querySelector('[data-consult-close]');
  const form = modal.querySelector('[data-consult-form]');
  const panel = modal.querySelector('.consult-modal-inner');
  let previousFocus = null;
  let previousOverflow = '';
  let previousHtmlOverflow = '';
  let isOpen = false;

  const updateViewport = () => {
    if (!isOpen) return;
    const viewport = window.visualViewport;
    // visualViewport.height changes when iOS keyboard opens; offsetTop is not
    // added to the fixed overlay to avoid the double-offset Safari issue.
    const height = viewport ? viewport.height : window.innerHeight;
    modal.style.setProperty('--consult-vh', `${Math.max(240, height)}px`);
  };
  const setModalState = (open) => {
    isOpen = open;
    modal.hidden = !open;
    if (open) modal.removeAttribute('hidden');
    else modal.setAttribute('hidden', '');
    modal.classList.toggle('is-open', open);
    modal.setAttribute('aria-hidden', String(!open));
    modal.removeAttribute('open'); // DIV is not a native dialog.
    document.body.classList.toggle('modal-open', open);
  };
  const openModal = () => {
    if (isOpen) return;
    closeNav();
    previousFocus = document.activeElement;
    previousOverflow = document.body.style.overflow;
    previousHtmlOverflow = document.documentElement.style.overflow;
    setModalState(true);
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    updateViewport();
    if (panel) panel.scrollTop = 0;
    // Focus the dialog container, not a text input: don't trigger iOS keyboard.
    try { modal.focus({ preventScroll: true }); } catch (_) { modal.focus(); }
  };
  const closeModal = () => {
    if (!isOpen) return;
    if (modal.contains(document.activeElement) && document.activeElement.blur) document.activeElement.blur();
    setModalState(false);
    document.body.style.overflow = previousOverflow;
    document.documentElement.style.overflow = previousHtmlOverflow;
    if (previousFocus?.isConnected) {
      try { previousFocus.focus({ preventScroll: true }); } catch (_) { previousFocus.focus(); }
    }
  };
  // One delegated click handler for every consultation / pre-purchase trigger.
  document.addEventListener('click', (event) => {
    const target = event.target instanceof Element ? event.target : event.target?.parentElement;
    const trigger = target?.closest('[data-consult-open]');
    if (!trigger) return;
    event.preventDefault();
    openModal();
  });
  closer?.addEventListener('click', closeModal);
  modal.addEventListener('click', (event) => { if (event.target === modal) closeModal(); });
  document.addEventListener('keydown', (event) => {
    if (!isOpen) return;
    if (event.key === 'Escape') { event.preventDefault(); closeModal(); return; }
    if (event.key !== 'Tab') return;
    const focusable = [...modal.querySelectorAll('button:not([disabled]), input:not([disabled]):not([type="hidden"]), textarea:not([disabled]), select:not([disabled]), a[href]')].filter(el => el.getClientRects().length);
    if (!focusable.length) { event.preventDefault(); modal.focus(); return; }
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (event.shiftKey && (document.activeElement === first || document.activeElement === modal)) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  window.visualViewport?.addEventListener('resize', updateViewport);
  window.visualViewport?.addEventListener('scroll', updateViewport);
  window.addEventListener('resize', updateViewport);
  window.addEventListener('orientationchange', updateViewport);
  setModalState(false);
  // Preserve the user's inputs when server-side form validation fails.
  if (modal.dataset.autoOpen === 'true' || modal.classList.contains('has-form-errors')) openModal();

  // Friendly client-side validation: no page navigation and errors stay beside the field.
  if (form) {
    const clearInvalid = (field) => {
      field.classList.remove('is-invalid');
      const old = field.parentElement?.querySelector('.client-field-error');
      old?.remove();
    };
    const markInvalid = (field, message) => {
      clearInvalid(field);
      field.classList.add('is-invalid');
      const error = document.createElement('div');
      error.className = 'field-error client-field-error';
      error.textContent = message;
      field.parentElement?.appendChild(error);
    };

    form.querySelectorAll('input, textarea, select').forEach((field) => {
      field.addEventListener('input', () => clearInvalid(field));
      field.addEventListener('change', () => clearInvalid(field));
    });

    form.addEventListener('submit', (event) => {
      let firstInvalid = null;
      const langEn = document.documentElement.lang === 'en';
      const name = form.querySelector('[name="name"]');
      const phone = form.querySelector('[name="phone"]');
      const subject = form.querySelector('[name="subject"]');
      const gender = form.querySelector('input[name="gender"]:checked');
      const genderWrap = form.querySelector('.gender-options');

      const requireText = (field, message) => {
        if (!field || field.value.trim().length < 2) {
          if (field) markInvalid(field, message);
          if (!firstInvalid) firstInvalid = field;
        }
      };
      requireText(name, langEn ? 'Please enter your full name.' : 'لطفاً نام و نام‌خانوادگی را وارد کنید.');
      if (!phone || !/^(?:0?9\d{9}|\+?98\d{10})$/.test(phone.value.replace(/[\s-]/g, ''))) {
        if (phone) markInvalid(phone, langEn ? 'Please enter a valid phone number.' : 'لطفاً یک شماره تماس معتبر وارد کنید.');
        if (!firstInvalid) firstInvalid = phone;
      }
      if (!gender) {
        if (genderWrap) {
          genderWrap.classList.add('is-invalid');
          const old = genderWrap.parentElement?.querySelector('.client-field-error');
          old?.remove();
          const error = document.createElement('div');
          error.className = 'field-error client-field-error';
          error.textContent = langEn ? 'Please choose an option.' : 'لطفاً یکی از گزینه‌ها را انتخاب کنید.';
          genderWrap.parentElement?.appendChild(error);
        }
        if (!firstInvalid) firstInvalid = genderWrap;
      }
      requireText(subject, langEn ? 'Please enter the subject of your request.' : 'لطفاً موضوع درخواست را وارد کنید.');

      if (firstInvalid) {
        event.preventDefault();
        openModal();
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        if (typeof firstInvalid.focus === 'function') firstInvalid.focus({ preventScroll: true });
      }
    });
  }
});

/* حفاظت سمت‌مرورگر از عکس/ویدیو (کنار حفاظت سمت‌سرور در website/media_views.py) */
(function () {
  document.addEventListener('contextmenu', function (e) {
    var t = e.target;
    if (t && (t.tagName === 'IMG' || t.tagName === 'VIDEO')) e.preventDefault();
  });
  document.addEventListener('dragstart', function (e) {
    var t = e.target;
    if (t && (t.tagName === 'IMG' || t.tagName === 'VIDEO')) e.preventDefault();
  });
  document.querySelectorAll('video').forEach(function (v) {
    v.setAttribute('controlsList', 'nodownload noremoteplayback');
    v.setAttribute('disablePictureInPicture', '');
    v.disableRemotePlayback = true;
  });
})();

/* ---------- Garnet project rail: manual drag support ----------
   Manual interaction is intentionally implemented first. The rail remains
   stationary unless the user drags it; autoplay can be added after this is verified. */
(function () {
  'use strict';

  function initProjectRails() {
    document.querySelectorAll('[data-rail]').forEach(function (rail) {
      var track = rail.querySelector('[data-rail-track]');
      if (!track || rail.dataset.railDragReady === '1') return;
      rail.dataset.railDragReady = '1';

      var pointerDown = false;
      var startX = 0;
      var startTranslate = 0;
      var currentTranslate = 0;
      var maxTranslate = 0;
      var moved = false;
      var pointerId = null;

      function measure() {
        var railWidth = rail.getBoundingClientRect().width;
        var trackWidth = track.scrollWidth;
        maxTranslate = Math.max(0, trackWidth - railWidth);
        currentTranslate = Math.max(0, Math.min(currentTranslate, maxTranslate));
        render();
      }

      function render() {
        track.style.transform = 'translate3d(' + (-currentTranslate) + 'px,0,0)';
      }

      function onDown(e) {
        if (e.pointerType === 'mouse' && e.button !== 0) return;
        if (e.target.closest('a,button,input,select,textarea')) return;
        measure();
        if (maxTranslate <= 0) return;
        pointerDown = true;
        moved = false;
        pointerId = e.pointerId;
        startX = e.clientX;
        startTranslate = currentTranslate;
        rail.classList.add('is-dragging');
        try { rail.setPointerCapture(pointerId); } catch (_) {}
      }

      function onMove(e) {
        if (!pointerDown || (pointerId !== null && e.pointerId !== pointerId)) return;
        var dx = e.clientX - startX;
        if (Math.abs(dx) > 4) moved = true;
        if (moved) {
          currentTranslate = Math.max(0, Math.min(maxTranslate, startTranslate - dx));
          render();
          if (e.cancelable) e.preventDefault();
        }
      }

      function onUp(e) {
        if (!pointerDown) return;
        pointerDown = false;
        pointerId = null;
        rail.classList.remove('is-dragging');
        if (moved) {
          rail.dataset.dragged = '1';
          window.setTimeout(function () { delete rail.dataset.dragged; }, 80);
        }
      }

      rail.addEventListener('pointerdown', onDown);
      rail.addEventListener('pointermove', onMove, { passive: false });
      rail.addEventListener('pointerup', onUp);
      rail.addEventListener('pointercancel', onUp);
      rail.addEventListener('lostpointercapture', onUp);
      rail.addEventListener('click', function (e) {
        if (rail.dataset.dragged === '1') {
          e.preventDefault();
          e.stopPropagation();
        }
      }, true);

      window.addEventListener('resize', measure);
      if ('ResizeObserver' in window) {
        new ResizeObserver(measure).observe(rail);
        new ResizeObserver(measure).observe(track);
      }
      Array.prototype.forEach.call(track.querySelectorAll('img'), function (img) {
        if (!img.complete) {
          img.addEventListener('load', measure, { once: true });
          img.addEventListener('error', measure, { once: true });
        }
      });
      window.requestAnimationFrame(measure);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initProjectRails, { once: true });
  } else {
    initProjectRails();
  }
})();
