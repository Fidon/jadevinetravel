(function ($) {
  "use strict";

  /* ----------------------------------------------------------
     1. Go Back button — uses browser history, homepage if no history exists
     ---------------------------------------------------------- */
  $(".jd-404-back-btn").on("click", function () {
    if (window.history.length > 1) {
      window.history.back();
    } else {
      window.location.href = "/";
    }
  });

  /* ----------------------------------------------------------
     2. Compass tilt
     ---------------------------------------------------------- */
  var $compass = $(".jd-404-compass i");

  if ($compass.length && window.matchMedia("(pointer: fine)").matches) {
    $(document).on("mousemove", function (e) {
      var centerX = $(window).width() / 2;
      var centerY = $(window).height() / 2;
      var deltaX = e.clientX - centerX;
      var deltaY = e.clientY - centerY;
      var angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);

      // Override the CSS spin animation temporarily on hover
      $compass.css("animation", "none");
      $compass.css("transform", "rotate(" + angle + "deg)");
    });

    // Resume spin when mouse leaves the window
    $(document).on("mouseleave", function () {
      $compass.css("animation", "");
      $compass.css("transform", "");
    });
  }
})(jQuery);
