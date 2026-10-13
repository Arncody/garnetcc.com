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

  const modal = document.getElementById('consultModal');
  if (!modal) return;

  const openers = document.querySelectorAll('[data-consult-open]');
  const closer = modal.querySelector('[data-consult-close]');
  const form = modal.querySelector('[data-consult-form]');

  // iOS Safari: 100vh/svh are unreliable inside <dialog>; use the real visible height.
  const setAppVh = () => document.documentElement.style.setProperty('--app-vh', (window.innerHeight * 0.01) + 'px');
  window.addEventListener('resize', () => { if (modal.open) setAppVh(); });

  const openModal = () => {
    setAppVh();
    closeNav();
    document.body.classList.add('modal-open');
    if (typeof modal.showModal === 'function') {
      if (!modal.open) modal.showModal();
    } else {
      modal.setAttribute('open', '');
    }
    window.setTimeout(() => modal.querySelector('input:not([type="hidden"]):not([name="gender"])')?.focus(), 80);
  };

  const closeModal = () => {
    if (typeof modal.close === 'function' && modal.open) modal.close();
    else modal.removeAttribute('open');
    document.body.classList.remove('modal-open');
  };

  openers.forEach((button) => button.addEventListener('click', (event) => {
    event.preventDefault();
    openModal();
  }));
  closer?.addEventListener('click', closeModal);
  modal.addEventListener('click', (event) => { if (event.target === modal) closeModal(); });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && modal.open) closeModal(); });

  // Server-side validation errors keep the user inside the form.
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
