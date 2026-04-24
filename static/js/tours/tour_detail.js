/* tour_detail.js */
(function ($) {
  "use strict";

  var PRICE_PER_PERSON = parseFloat(window.JD_TOUR_PRICE) || 0;
  var MAX_PARTICIPANTS = parseInt(window.JD_TOUR_MAX_PARTICIPANTS) || 50;
  var S = window.JD_STRINGS || {};

  /* ── GLightbox ──────────────────────────────────────────── */
  if (typeof GLightbox !== "undefined" && $(".gallery-link").length) {
    GLightbox({ selector: ".gallery-link", touchNavigation: true, loop: true });
  }

  /* ── Flatpickr ──────────────────────────────────────────── */
  flatpickr("#id_preferred_date", {
    minDate: "today",
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "D, d M Y",
    disableMobile: true,
  });

  /* ── Participant Counter ─────────────────────────────────── */
  var $countInput = $("#id_num_participants");
  var $decreaseBtn = $("#decreaseParticipants");
  var $increaseBtn = $("#increaseParticipants");

  function getCount() {
    return parseInt($countInput.val()) || 1;
  }

  function setCount(val) {
    var n = Math.max(1, Math.min(MAX_PARTICIPANTS, val));
    $countInput.val(n);
    $decreaseBtn.prop("disabled", n <= 1);
    $increaseBtn.prop("disabled", n >= MAX_PARTICIPANTS);
    updateBreakdown(n);
  }

  $decreaseBtn.on("click", function () {
    setCount(getCount() - 1);
  });
  $increaseBtn.on("click", function () {
    setCount(getCount() + 1);
  });

  /* ── Price Breakdown ─────────────────────────────────────── */
  function updateBreakdown(n) {
    var total = PRICE_PER_PERSON * n;
    var personLabel = n === 1 ? S.person || "person" : S.people || "people";

    $("#breakdown-rate-label").text(
      "$" + PRICE_PER_PERSON.toFixed(0) + " × " + n + " " + personLabel,
    );
    $("#breakdown-rate-amount").text("$" + total.toFixed(0));
    $("#breakdown-total").text("$" + total.toFixed(0));
    $("#totalPriceDisplay").text("$" + total.toFixed(0));
  }

  // Initialise state
  setCount(parseInt($countInput.val()) || 1);

  /* ── Form Submit UX ──────────────────────────────────────── */
  var $submitBtn = $("#bookingSubmitBtn");
  var originalBtnHtml = $submitBtn.html();

  $("#tour-booking-form").on("submit", function (e) {
    var dateVal = $("#id_preferred_date").val();

    if (!dateVal) {
      e.preventDefault();
      JD.toast("Please select a preferred start date.", "error");
      return false;
    }

    $submitBtn
      .prop("disabled", true)
      .html(
        '<span class="jd-spinner" style="width:18px;height:18px;border-width:2px;"></span>',
      );
  });

  /* Restore button when browser navigates back */
  window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
      $submitBtn.prop("disabled", false).html(originalBtnHtml);
    }
  });
})(jQuery);
