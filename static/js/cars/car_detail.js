/* car_detail.js */
(function ($) {
  "use strict";

  const PRICE_PER_DAY = parseFloat(window.JD_CAR_PRICE_PER_DAY) || 0;
  const CAR_CAPACITY = parseInt(window.JD_CAR_CAPACITY) || 20;
  const ALLOWS_PETS = window.JD_CAR_ALLOWS_PETS === true;
  const S = window.JD_STRINGS || {};

  let pickupDate = null;
  let returnDate = null;

  /* ── GLightbox ── */
  if (typeof GLightbox !== "undefined") {
    GLightbox({ selector: ".gallery-link", touchNavigation: true, loop: true });
  }

  /* ── Flatpickr ── */
  const fpPickup = flatpickr("#id_pickup_date", {
    minDate: "today",
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "D, d M Y",
    disableMobile: true,
    onChange: function (dates) {
      pickupDate = dates[0] || null;
      if (pickupDate) {
        const minReturn = new Date(pickupDate);
        minReturn.setDate(minReturn.getDate() + 1);
        fpReturn.set("minDate", minReturn);
        if (returnDate && returnDate <= pickupDate) {
          fpReturn.clear();
          returnDate = null;
        }
      }
      updateBreakdown();
    },
  });

  const fpReturn = flatpickr("#id_return_date", {
    minDate: new Date(Date.now() + 86400000),
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "D, d M Y",
    disableMobile: true,
    onChange: function (dates) {
      returnDate = dates[0] || null;
      updateBreakdown();
    },
  });

  /* ── Price breakdown ── */
  function updateBreakdown() {
    if (!pickupDate || !returnDate) {
      $("#price-breakdown").hide();
      return;
    }
    const days = Math.round((returnDate - pickupDate) / 86400000);
    if (days < 1) {
      $("#price-breakdown").hide();
      return;
    }
    const total = (PRICE_PER_DAY * days).toFixed(2);
    $("#breakdown-rate-label").text(
      "$" +
        PRICE_PER_DAY.toFixed(2) +
        " × " +
        days +
        (days === 1 ? " day" : " days"),
    );
    $("#breakdown-rate-amount").text("$" + total);
    $("#breakdown-total").text(
      "$" +
        parseFloat(total).toLocaleString(undefined, {
          minimumFractionDigits: 2,
        }),
    );
    $("#price-breakdown").show();
  }

  /* ── Rental mode toggle ── */
  function updateLicenceField() {
    if ($('input[name="rental_mode"]:checked').val() === "self_drive") {
      $("#licence-field").show();
    } else {
      $("#licence-field").hide();
      $("#id_driver_licence_number").val("");
    }
  }

  $('input[name="rental_mode"]').on("change", updateLicenceField);
  updateLicenceField();

  /* ── Passenger total ── */
  function getTotalPassengers() {
    return (
      (parseInt($("#id_num_adults").val()) || 0) +
      (parseInt($("#id_num_children").val()) || 0) +
      (parseInt($("#id_num_infants").val()) || 0)
    );
  }

  /* ── Generic counter factory ── */
  function makeCounter($minus, $plus, $input, getMin, getMax) {
    $minus.on("click", function () {
      const cur = parseInt($input.val()) || 0;
      if (cur > getMin()) $input.val(cur - 1);
    });
    $plus.on("click", function () {
      const cur = parseInt($input.val()) || 0;
      const max = getMax();
      if (cur < max) {
        $input.val(cur + 1);
      } else {
        var msg = (
          S.maxCapacity || "Maximum capacity is {cap} passengers."
        ).replace("{cap}", CAR_CAPACITY);
        JD.toast(msg, "error");
      }
    });
  }

  /* Adults — min 1; max: capacity minus other occupants */
  makeCounter(
    $("#btn-adults-minus"),
    $("#btn-adults-plus"),
    $("#id_num_adults"),
    function () {
      return 1;
    },
    function () {
      var others =
        (parseInt($("#id_num_children").val()) || 0) +
        (parseInt($("#id_num_infants").val()) || 0);
      return Math.max(1, CAR_CAPACITY - others);
    },
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
      var others =
        (parseInt($("#id_num_adults").val()) || 0) +
        (parseInt($("#id_num_infants").val()) || 0);
      return Math.max(0, CAR_CAPACITY - others);
    },
  );

  /* Infants */
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
  );

  /* Pets — only rendered in template when ALLOWS_PETS=true */
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
    );
  }

  /* ── Form submit validation ── */
  var $submitBtn = $(".booking-submit-btn");
  var originalBtnHtml = $submitBtn.html();

  $("#car-booking-form").on("submit", function (e) {
    var valid = true;

    if (!$("#id_pickup_location").val()) {
      JD.toast("Please select a pickup location", "error");
      valid = false;
    }
    if (!pickupDate) {
      JD.toast("Please select a pickup date", "error");
      valid = false;
    }
    if (!returnDate) {
      JD.toast("Please select a return date", "error");
      valid = false;
    }
    if (
      $('input[name="rental_mode"]:checked').val() === "self_drive" &&
      !$("#id_driver_licence_number").val().trim()
    ) {
      JD.toast("Licence number is required for self-drive", "error");
      valid = false;
    }
    if (getTotalPassengers() > CAR_CAPACITY) {
      var msg = (
        S.maxCapacity || "Maximum capacity is {cap} passengers."
      ).replace("{cap}", CAR_CAPACITY);
      JD.toast(msg, "error");
      valid = false;
    }

    if (!valid) {
      e.preventDefault();
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
