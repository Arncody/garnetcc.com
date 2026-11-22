(() => {
  const video = document.querySelector('.g-home-hero-video[data-video-src]');
  if (!video) return;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const updatePlayback = () => {
    if (reducedMotion.matches) {
      video.pause();
      if (video.hasAttribute('src')) {
        video.removeAttribute('src');
        video.load();
      }
      return;
    }

    video.src = video.dataset.videoSrc;
    // Leave the poster visible if loading fails or autoplay is blocked.
    video.play().catch(() => {});
  };

  reducedMotion.addEventListener('change', updatePlayback);
  updatePlayback();
})();
