/* booking_confirmation.js */
(function ($) {
  "use strict";

  /* Trigger confetti-style reveal on the check icon */
  setTimeout(function () {
    $(".confirmation-check").addClass("popped");
  }, 100);

  /* Mark all jd-reveal elements as revealed immediately on this page
     — no scroll needed, user should see everything at once */
  $(".jd-reveal").addClass("revealed");
})(jQuery);
