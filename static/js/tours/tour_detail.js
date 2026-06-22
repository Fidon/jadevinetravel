/* tour_detail.js */
(function ($) {
  "use strict";

  var PRICE_PER_PERSON = parseFloat(window.JD_TOUR_PRICE) || 0;
  var MAX_PARTICIPANTS = parseInt(window.JD_TOUR_MAX_PARTICIPANTS) || 50;
  var ALLOWS_PETS = window.JD_TOUR_ALLOWS_PETS === true;
  var S = window.JD_STRINGS || {};

  /* ── GLightbox ── */
  if (typeof GLightbox !== "undefined" && $(".gallery-link").length) {
    GLightbox({ selector: ".gallery-link", touchNavigation: true, loop: true });
  }

  /* ── Flatpickr ── */
  flatpickr("#id_preferred_date", {
    minDate: "today",
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "D, d M Y",
    disableMobile: true,
  });

  /* ── Price breakdown ── */
  function updateBreakdown() {
    // num_participants = adults + children (infants free)
    var adults = parseInt($("#id_num_adults").val()) || 0;
    var children = parseInt($("#id_num_children").val()) || 0;
    var participants = adults + children;
    var total = PRICE_PER_PERSON * participants;

    var personLabel =
      participants === 1 ? S.person || "person" : S.people || "people";

    $("#breakdown-rate-label").text(
      "$" +
        PRICE_PER_PERSON.toFixed(0) +
        " × " +
        participants +
        " " +
        personLabel,
    );
    $("#breakdown-rate-amount").text("$" + total.toFixed(0));
    $("#breakdown-total").text("$" + total.toFixed(0));
    $("#totalPriceDisplay").text("$" + total.toFixed(0));
  }

  /* ── Billable participant total ── */
  function getBillableCount() {
    return (
      (parseInt($("#id_num_adults").val()) || 0) +
      (parseInt($("#id_num_children").val()) || 0)
    );
  }

  /* ── Generic counter factory ── */
  function makeCounter($minus, $plus, $input, getMin, getMax, onChange) {
    $minus.on("click", function () {
      var cur = parseInt($input.val()) || 0;
      if (cur > getMin()) {
        $input.val(cur - 1);
        if (onChange) onChange();
      }
    });
    $plus.on("click", function () {
      var cur = parseInt($input.val()) || 0;
      var max = getMax();
      if (cur < max) {
        $input.val(cur + 1);
        if (onChange) onChange();
      } else {
        var msg = (
          S.maxParticipants || "Maximum {max} participants reached."
        ).replace("{max}", MAX_PARTICIPANTS);
        JD.toast(msg, "error");
      }
    });
  }

  /* Adults — min 1 */
  makeCounter(
    $("#btn-adults-minus"),
    $("#btn-adults-plus"),
    $("#id_num_adults"),
    function () {
      return 1;
    },
    function () {
      var children = parseInt($("#id_num_children").val()) || 0;
      return Math.max(1, MAX_PARTICIPANTS - children);
    },
    updateBreakdown,
  );

  /* Children */
  makeCounter(
    $("#btn-children-minus"),
    $("#btn-children-plus"),
    $("#id_num_children"),
    function () {
      return 0;
    },
    function () {
      var adults = parseInt($("#id_num_adults").val()) || 0;
      return Math.max(0, MAX_PARTICIPANTS - adults);
    },
    updateBreakdown,
  );

  /* Infants — free, no cap against MAX_PARTICIPANTS */
  makeCounter(
    $("#btn-infants-minus"),
    $("#btn-infants-plus"),
    $("#id_num_infants"),
    function () {
      return 0;
    },
    function () {
      return 10;
    },
    null,
  );

  /* Pets — only wired when tour allows pets */
  if (ALLOWS_PETS) {
    makeCounter(
      $("#btn-pets-minus"),
      $("#btn-pets-plus"),
      $("#id_num_pets"),
      function () {
        return 0;
      },
      function () {
        return 5;
      },
      null,
    );
  }

  /* ── Initialise breakdown ── */
  updateBreakdown();

  /* ── Form submit ── */
  var $submitBtn = $("#bookingSubmitBtn");
  var originalBtnHtml = $submitBtn.html();

  $("#tour-booking-form").on("submit", function (e) {
    var dateVal = $("#id_preferred_date").val();
    if (!dateVal) {
      e.preventDefault();
      JD.toast(
        S.selectPreferredDate || "Please select a preferred start date.",
        "error",
      );
      return false;
    }

    $submitBtn
      .prop("disabled", true)
      .html(
        '<span class="jd-spinner" style="width:18px;height:18px;border-width:2px;"></span>',
      );
  });

  window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
      $submitBtn.prop("disabled", false).html(originalBtnHtml);
    }
  });
})(jQuery);
