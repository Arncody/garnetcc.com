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

/* ---------- Garnet project rail: initialize after DOM is ready ---------- */
(function () {
  'use strict';

  function initProjectRails() {
    var rails = document.querySelectorAll('[data-rail]');
    if (!rails.length) return;

    rails.forEach(function (rail) {
      var track = rail.querySelector('[data-rail-track]');
      if (!track || rail.dataset.railInitialized === '1') return;

      var originals = Array.prototype.slice.call(track.children).filter(function (el) {
        return !el.hasAttribute('data-clone');
      });
      if (originals.length < 2) return;

      rail.dataset.railInitialized = '1';
      var speed = Math.max(10, Math.min(120, parseInt(rail.getAttribute('data-speed'), 10) || 32));
      var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      var setWidth = 0, offset = 0, lastTime = 0, raf = 0;
      var paused = false, dragging = false, moved = false;
      var startX = 0, startOffset = 0, pointerId = null, resumeTimer = 0;

      function measureAndClone() {
        Array.prototype.slice.call(track.querySelectorAll('[data-clone]')).forEach(function (el) { el.remove(); });
        track.style.transform = 'translate3d(0,0,0)';
        track.style.willChange = 'transform';

        var firstRect = originals[0].getBoundingClientRect();
        var lastRect = originals[originals.length - 1].getBoundingClientRect();
        setWidth = Math.max(0, lastRect.right - firstRect.left);
        if (!setWidth) {
          setWidth = originals.reduce(function (sum, el) {
            return sum + el.getBoundingClientRect().width;
          }, 0);
          var style = getComputedStyle(track);
          setWidth += (parseFloat(style.columnGap || style.gap) || 0) * (originals.length - 1);
        }
        if (!setWidth) return;

        var safety = 0;
        while (track.scrollWidth < rail.clientWidth + setWidth && safety < 12) {
          originals.forEach(function (original) {
            var clone = original.cloneNode(true);
            clone.setAttribute('data-clone', '1');
            clone.setAttribute('aria-hidden', 'true');
            clone.querySelectorAll('[id]').forEach(function (node) { node.removeAttribute('id'); });
            clone.querySelectorAll('a,button,input,select,textarea,[tabindex]').forEach(function (node) {
              node.setAttribute('tabindex', '-1');
            });
            track.appendChild(clone);
          });
          safety++;
        }
        offset = offset % setWidth;
        render();
      }

      function render() {
        track.style.transform = 'translate3d(' + (-offset) + 'px,0,0)';
      }

      function scheduleResume(delay) {
        window.clearTimeout(resumeTimer);
        resumeTimer = window.setTimeout(function () {
          if (!dragging && !reduced) paused = false;
        }, delay);
      }

      function tick(now) {
        if (!lastTime) lastTime = now;
        var delta = Math.min(50, now - lastTime);
        lastTime = now;
        if (!paused && !dragging && !reduced && !document.hidden && rail.getBoundingClientRect().width > 0) {
          offset += speed * delta / 1000;
          if (setWidth > 0 && offset >= setWidth) offset = offset % setWidth;
          render();
        }
        raf = window.requestAnimationFrame(tick);
      }

      function onPointerDown(e) {
        if (e.pointerType === 'mouse' && e.button !== 0) return;
        if (e.target.closest('a,button,input,select,textarea')) return;
        dragging = true;
        moved = false;
        paused = true;
        pointerId = e.pointerId;
        startX = e.clientX;
        startOffset = offset;
        rail.classList.add('is-dragging');
        try { rail.setPointerCapture(pointerId); } catch (_) {}
      }

      function onPointerMove(e) {
        if (!dragging || (pointerId !== null && e.pointerId !== pointerId)) return;
        var dx = e.clientX - startX;
        if (Math.abs(dx) > 4) moved = true;
        if (!moved) return;
        offset = startOffset - dx;
        if (setWidth > 0) {
          offset = ((offset % setWidth) + setWidth) % setWidth;
        }
        render();
        if (e.cancelable) e.preventDefault();
      }

      function onPointerUp() {
        if (!dragging) return;
        dragging = false;
        pointerId = null;
        rail.classList.remove('is-dragging');
        if (moved) {
          rail.dataset.railDragged = '1';
          window.setTimeout(function () { delete rail.dataset.railDragged; }, 100);
        }
        scheduleResume(1800);
      }

      rail.addEventListener('pointerdown', onPointerDown);
      rail.addEventListener('pointermove', onPointerMove, { passive: false });
      rail.addEventListener('pointerup', onPointerUp);
      rail.addEventListener('pointercancel', onPointerUp);
      rail.addEventListener('lostpointercapture', onPointerUp);
      rail.addEventListener('click', function (e) {
        if (rail.dataset.railDragged === '1') {
          e.preventDefault();
          e.stopPropagation();
        }
      }, true);
      rail.addEventListener('mouseenter', function () { paused = true; });
      rail.addEventListener('mouseleave', function () { scheduleResume(350); });
      rail.addEventListener('focusin', function () { paused = true; });
      rail.addEventListener('focusout', function () { scheduleResume(600); });
      rail.addEventListener('touchstart', function () { paused = true; }, { passive: true });
      rail.addEventListener('touchend', function () { scheduleResume(1800); }, { passive: true });

      if ('ResizeObserver' in window) {
        var observer = new ResizeObserver(function () { measureAndClone(); });
        observer.observe(rail);
        observer.observe(track);
      } else {
        window.addEventListener('resize', measureAndClone);
      }
      originals.forEach(function (imgCard) {
        imgCard.querySelectorAll('img').forEach(function (img) {
          if (!img.complete) img.addEventListener('load', measureAndClone, { once: true });
        });
      });

      measureAndClone();
      rail.dataset.railReady = '1';
      if (!reduced) raf = window.requestAnimationFrame(tick);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initProjectRails, { once: true });
  } else {
    initProjectRails();
  }
})();
