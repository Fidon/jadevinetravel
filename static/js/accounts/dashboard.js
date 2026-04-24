(function ($) {
  "use strict";

  // Load favourite count asynchronously
  $.ajax({
    url: window.JD_URLS ? window.JD_URLS.favourites : "/accounts/favourites/",
    method: "GET",
    success: function (data) {
      // Count .fav-item elements in the favourites page — not available here.
      // Instead fetch count from a lightweight endpoint (we parse the page).
      // Simpler: just leave the stat as a link — count shown on the page itself.
    },
  });

  // Trigger load reveals
  if (typeof JD !== "undefined" && JD.initReveal) {
    JD.initReveal();
  }
})(jQuery);
