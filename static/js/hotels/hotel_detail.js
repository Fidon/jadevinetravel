/* hotel_detail.js */
(function ($) {
  "use strict";

  const ROOM_TYPES = window.JD_ROOM_TYPES || [];
  const BASE_PRICE = parseFloat(window.JD_HOTEL_BASE_PRICE) || 0;
  const S = window.JD_STRINGS || {};

  /* ── Initial state from first room type ── */
  const firstRoom = ROOM_TYPES.length ? ROOM_TYPES[0] : null;
  let selectedRoomId = firstRoom ? firstRoom.id : null;
  let selectedPrice = firstRoom
    ? parseFloat(firstRoom.display_price)
    : BASE_PRICE;
  let selectedMaxGuests = firstRoom ? firstRoom.max_guests : 20;
  let checkInDate = null;
  let checkOutDate = null;

  /* ── DOM refs ── */
  const $displayPrice = $("#display-price");
  const $roomIdInput = $("#selected-room-type-id");
  const $guestsInput = $("#id_num_guests");
  const $guestMaxNote = $("#guest-max-note");
  const $breakdown = $("#price-breakdown");
  const $rateLabel = $("#breakdown-rate-label");
  const $rateAmount = $("#breakdown-rate-amount");
  const $totalAmount = $("#breakdown-total");

  /* ── GLightbox ── */
  if (typeof GLightbox !== "undefined") {
    GLightbox({ selector: ".gallery-link", touchNavigation: true, loop: true });
  }

  /* ── Flatpickr ── */
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const fpCheckIn = flatpickr("#id_check_in_date", {
    minDate: "today",
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "D, d M Y",
    disableMobile: true,
    onChange: function (selectedDates) {
      checkInDate = selectedDates[0] || null;
      if (checkInDate) {
        const minOut = new Date(checkInDate);
        minOut.setDate(minOut.getDate() + 1);
        fpCheckOut.set("minDate", minOut);
        if (checkOutDate && checkOutDate <= checkInDate) {
          fpCheckOut.clear();
          checkOutDate = null;
        }
      }
      updatePriceBreakdown();
    },
  });

  const fpCheckOut = flatpickr("#id_check_out_date", {
    minDate: new Date(today.getTime() + 86400000),
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "D, d M Y",
    disableMobile: true,
    onChange: function (selectedDates) {
      checkOutDate = selectedDates[0] || null;
      updatePriceBreakdown();
    },
  });

  /* ── Price breakdown ── */
  function updatePriceBreakdown() {
    if (!checkInDate || !checkOutDate) {
      $breakdown.hide();
      return;
    }
    const nights = Math.round((checkOutDate - checkInDate) / 86400000);
    if (nights < 1) {
      $breakdown.hide();
      return;
    }
    const total = (selectedPrice * nights).toFixed(2);
    $rateLabel.text(
      "$" +
        selectedPrice.toFixed(2) +
        " × " +
        nights +
        (nights === 1 ? " night" : " nights"),
    );
    $rateAmount.text("$" + total);
    $totalAmount.text(
      "$" +
        parseFloat(total).toLocaleString(undefined, {
          minimumFractionDigits: 2,
        }),
    );
    $breakdown.show();
  }

  /* ── Update price display in booking panel header ── */
  function updatePanelPrice(room) {
    const displayPrice = parseFloat(room.display_price);
    const origPrice = parseFloat(room.price);

    if (room.has_discount && origPrice !== displayPrice) {
      $displayPrice.html(
        '<span class="jd-price-original" style="font-size:1rem;margin-right:4px;">$' +
          origPrice.toFixed(2) +
          "</span>$" +
          displayPrice.toFixed(2),
      );
    } else {
      $displayPrice.text("$" + displayPrice.toFixed(2));
    }
  }

  /* ── Policy notices ── */
  function applyRoomPolicies(room) {
    // Non-refundable notice
    if (!room.is_refundable) {
      $("#nonrefundable-notice").show();
    } else {
      $("#nonrefundable-notice").hide();
    }

    // Pay Now only notice + Pay on Arrival footer note
    if (!room.allows_pay_on_arrival) {
      $("#pay-now-only-notice").show();
      $("#poa-note").hide();
    } else {
      $("#pay-now-only-notice").hide();
      $("#poa-note").show();
    }
  }

  /* ── Room type card click ── */
  $(document).on("click", ".room-type-card", function () {
    const $card = $(this);
    $(".room-type-card").removeClass("selected");
    $card.addClass("selected");

    selectedRoomId = parseInt($card.data("room-id"));
    selectedMaxGuests = parseInt($card.data("max-guests"));

    // Find full room object from JD_ROOM_TYPES
    const room = ROOM_TYPES.find(function (r) {
      return r.id === selectedRoomId;
    });
    if (!room) return;

    selectedPrice = parseFloat(room.display_price);
    $roomIdInput.val(selectedRoomId);

    updatePanelPrice(room);
    applyRoomPolicies(room);

    const currentGuests = parseInt($guestsInput.val()) || 1;
    if (currentGuests > selectedMaxGuests) {
      $guestsInput.val(selectedMaxGuests);
    }
    $guestMaxNote.text("Max " + selectedMaxGuests + " guests for this room");

    updatePriceBreakdown();
  });

  /* ── Initialise with first room on page load ── */
  if (firstRoom) {
    updatePanelPrice(firstRoom);
    applyRoomPolicies(firstRoom);
    $guestMaxNote.text("Max " + selectedMaxGuests + " guests for this room");
  }

  /* ── Guest counter ── */
  $("#btn-guests-plus").on("click", function () {
    const current = parseInt($guestsInput.val()) || 1;
    if (current < selectedMaxGuests) {
      $guestsInput.val(current + 1);
    } else {
      JD.toast(
        "Maximum " + selectedMaxGuests + " guests for this room type",
        "error",
      );
    }
  });

  $("#btn-guests-minus").on("click", function () {
    const current = parseInt($guestsInput.val()) || 1;
    if (current > 1) {
      $guestsInput.val(current - 1);
    }
  });

  /* ── Form submission ── */
  var $submitBtn = $(".booking-submit-btn");
  var originalBtnHtml = $submitBtn.html();

  $("#hotel-booking-form").on("submit", function (e) {
    var valid = true;
    if (!checkInDate) {
      JD.toast("Please select a check-in date", "error");
      valid = false;
    }
    if (!checkOutDate) {
      JD.toast("Please select a check-out date", "error");
      valid = false;
    }
    if (!selectedRoomId) {
      JD.toast("Please select a room type", "error");
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
