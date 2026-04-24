/* car_detail.js */
(function ($) {
  "use strict";

  const PRICE_PER_DAY = parseFloat(window.JD_CAR_PRICE_PER_DAY) || 0;

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
    onChange: function (selectedDates) {
      pickupDate = selectedDates[0] || null;
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
    onChange: function (selectedDates) {
      returnDate = selectedDates[0] || null;
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

  /* ── Rental mode toggle — show/hide licence field ── */
  function updateLicenceField() {
    const mode = $('input[name="rental_mode"]:checked').val();
    if (mode === "self_drive") {
      $("#licence-field").show();
    } else {
      $("#licence-field").hide();
      $("#id_driver_licence_number").val("");
    }
  }

  $('input[name="rental_mode"]').on("change", updateLicenceField);

  /* Run on page load to handle prefilled state */
  updateLicenceField();

  /* ── Form submit validation ── */
  var $submitBtn = $(".booking-submit-btn");
  var originalBtnHtml = $submitBtn.html();

  $("#car-booking-form").on("submit", function (e) {
    let valid = true;

    const pickup = $("#id_pickup_location").val();
    if (!pickup) {
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

    const mode = $('input[name="rental_mode"]:checked').val();
    if (mode === "self_drive" && !$("#id_driver_licence_number").val().trim()) {
      JD.toast("Licence number is required for self-drive", "error");
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

  /* Restore button when browser navigates back */
  window.addEventListener("pageshow", function (e) {
    if (e.persisted) {
      $submitBtn.prop("disabled", false).html(originalBtnHtml);
    }
  });
})(jQuery);
