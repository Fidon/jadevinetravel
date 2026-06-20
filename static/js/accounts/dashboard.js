(function ($) {
  "use strict";

  // Favourite count is passed directly from the view via the template.
  // No AJAX needed — the value is already in the DOM on page load.
  var count = parseInt($("#favCount").data("count"), 10);
  $("#favCount").text(isNaN(count) ? "0" : count);

  // Trigger load reveals
  if (typeof JD !== "undefined" && JD.initReveal) {
    JD.initReveal();
  }
})(jQuery);
