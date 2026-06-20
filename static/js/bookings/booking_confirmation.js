/**
 * booking_confirmation.js
 *
 * Handles the pending payment state: polls the server every 4 seconds
 * and reloads the page once payment_status transitions out of 'pending'.
 *
 * Only runs when the pending banner is present in the DOM — zero overhead
 * on confirmed or failed states.
 */
$(function () {
  "use strict";

  var $pendingBanner = $(".confirmation-banner-pending");
  if (!$pendingBanner.length) return;

  var pollInterval = null;
  var pollCount = 0;
  var MAX_POLLS = 30; // 30 × 4s = 2 minutes max polling window

  function pollPaymentStatus() {
    pollCount++;
    if (pollCount > MAX_POLLS) {
      clearInterval(pollInterval);
      // After 2 minutes still pending — stop polling, prompt user to check dashboard
      $pendingBanner
        .find(".confirmation-subtitle")
        .text(
          window.JD_STRINGS
            ? window.JD_STRINGS.payment_timeout_msg
            : "Payment confirmation is taking longer than expected. Please check your dashboard for the latest status.",
        );
      return;
    }

    $.ajax({
      url: window.location.href,
      method: "GET",
      headers: { "X-Requested-With": "XMLHttpRequest" },
      success: function (html) {
        // Parse the returned page to check if the pending banner is gone
        var $returnedDoc = $(html);
        var stillPending =
          $returnedDoc.find(".confirmation-banner-pending").length > 0;
        if (!stillPending) {
          clearInterval(pollInterval);
          window.location.reload();
        }
      },
      error: function () {
        // Network error — keep polling silently
      },
    });
  }

  // Start polling after a 3-second initial delay
  setTimeout(function () {
    pollInterval = setInterval(pollPaymentStatus, 4000);
  }, 3000);
});
