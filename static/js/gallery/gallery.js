(function ($) {
  "use strict";

  // ── GLightbox init ────────────────────────────────────────────────────
  if (typeof GLightbox !== "undefined") {
    GLightbox({
      selector: ".glightbox",
      touchNavigation: true,
      loop: true,
      autoplayVideos: true,
      moreLength: 0,
      slideEffect: "fade",
      plyr: {
        config: {
          ratio: "16:9",
          youtube: { noCookie: true },
          vimeo: { byline: false, portrait: false, title: false },
        },
      },
    });
  }

  // ── Trigger reveal on items already in viewport on load ──────────────
  if (window.JD && typeof JD.initReveal === "function") {
    JD.initReveal();
  }
})(jQuery);
