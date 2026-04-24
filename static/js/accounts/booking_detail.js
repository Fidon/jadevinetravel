(function ($) {
  "use strict";

  var $modal = $("#cancelModal");
  var $openBtn = $("#cancelBookingBtn");
  var $closeBtn1 = $("#cancelModalClose");
  var $closeBtn2 = $("#cancelModalClose2");

  function openModal() {
    $modal.addClass("open");
    $("body").css("overflow", "hidden");
    $modal.find("#id_cancellation_reason").focus();
  }

  function closeModal() {
    $modal.removeClass("open");
    $("body").css("overflow", "");
  }

  if ($openBtn.length) {
    $openBtn.on("click", openModal);
    $closeBtn1.on("click", closeModal);
    $closeBtn2.on("click", closeModal);

    // Close on backdrop click
    $modal.on("click", function (e) {
      if ($(e.target).is($modal)) {
        closeModal();
      }
    });

    // ESC closes modal
    $(document).on("keydown", function (e) {
      if (e.key === "Escape" && $modal.hasClass("open")) {
        closeModal();
      }
    });

    // Disable submit until checkbox is checked
    var $submitBtn = $('#cancelForm button[type="submit"]');
    var $confirmChk = $("#id_confirm");

    function updateSubmitState() {
      $submitBtn.prop("disabled", !$confirmChk.is(":checked"));
    }

    updateSubmitState();
    $confirmChk.on("change", updateSubmitState);

    // Prevent double-submit
    $("#cancelForm").on("submit", function () {
      $submitBtn
        .prop("disabled", true)
        .text(
          window.JD_STRINGS && window.JD_STRINGS.processing
            ? window.JD_STRINGS.processing
            : "Processing...",
        );
    });
  }
})(jQuery);
