/* booking_summary.js */
(function ($) {
  "use strict";

  /* Highlight selected payment option on radio change */
  $('input[name="payment_mode"]').on("change", function () {
    $(".payment-option").removeClass("selected");
    $(this).closest(".payment-option").addClass("selected");
  });

  /* Show loading state on confirm — prevents double submit */
  var $btn = $("#confirm-btn");
  var originalBtnHtml = $btn.html();

  $("#payment-mode-form").on("submit", function () {
    var mode = $('input[name="payment_mode"]:checked').val();
    var label =
      mode === "pay_on_arrival"
        ? "Confirming Reservation..."
        : "Proceeding to Payment...";
    $btn
      .prop("disabled", true)
      .html(
        '<span class="jd-spinner" style="width:18px;height:18px;border-width:2px;"></span> ' +
          label,
      );
  });

  /* Restore button on browser back */
  window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
      $btn.prop("disabled", false).html(originalBtnHtml);
    }
  });
})(jQuery);
