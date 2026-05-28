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
  let selectedAllowsPets = firstRoom ? firstRoom.allows_pets : false;
  let checkInDate = null;
  let checkOutDate = null;

  /* ── DOM refs ── */
  const $displayPrice = $("#display-price");
  const $roomIdInput = $("#selected-room-type-id");
  const $breakdown = $("#price-breakdown");
  const $rateLabel = $("#breakdown-rate-label");
  const $rateAmount = $("#breakdown-rate-amount");
  const $totalAmount = $("#breakdown-total");
  const $guestMaxNote = $("#guest-max-note");

  /* ── GLightbox ── */
  var lightbox = null;
  var roomLightbox = null;

  function initLightbox() {
    if (typeof GLightbox === "undefined") return;
    if (lightbox) lightbox.destroy();
    lightbox = GLightbox({
      selector: ".hotel-gallery-link",
      touchNavigation: true,
      loop: true,
    });
  }

  function initRoomLightbox() {
    if (typeof GLightbox === "undefined") return;
    if (roomLightbox) roomLightbox.destroy();
    roomLightbox = GLightbox({
      selector: ".room-strip-link",
      touchNavigation: true,
      loop: true,
    });
  }

  initLightbox();

  /* ── Flatpickr ── */
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const fpCheckIn = flatpickr("#id_check_in_date", {
    minDate: "today",
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "D, d M Y",
    disableMobile: true,
    onChange: function (dates) {
      checkInDate = dates[0] || null;
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
    onChange: function (dates) {
      checkOutDate = dates[0] || null;
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
    const rooms = parseInt($("#id_num_rooms").val()) || 1;
    const total = (selectedPrice * nights * rooms).toFixed(2);
    $rateLabel.text(
      "$" +
        selectedPrice.toFixed(2) +
        " × " +
        nights +
        (nights === 1 ? " night" : " nights") +
        " × " +
        rooms +
        (rooms === 1 ? " room" : " rooms"),
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

  /* ── Update panel price header ── */
  function updatePanelPrice(room) {
    const display = parseFloat(room.display_price);
    const orig = parseFloat(room.price);
    if (room.has_discount && orig !== display) {
      $displayPrice.html(
        '<span class="jd-price-original" style="font-size:1rem;margin-right:4px;">$' +
          orig.toFixed(2) +
          "</span>$" +
          display.toFixed(2),
      );
    } else {
      $displayPrice.text("$" + display.toFixed(2));
    }
  }

  /* ── Room policy notices ── */
  function applyRoomPolicies(room) {
    $("#nonrefundable-notice").toggle(!room.is_refundable);
    if (!room.allows_pay_on_arrival) {
      $("#pay-now-only-notice").show();
      $("#poa-note").hide();
    } else {
      $("#pay-now-only-notice").hide();
      $("#poa-note").show();
    }
    // Pets row: show only if room allows pets
    if (room.allows_pets) {
      $("#pets-row").show();
    } else {
      $("#pets-row").hide();
      $("#id_num_pets").val(0);
    }
  }

  /* ── Guest capacity note ── */
  function updateGuestNote() {
    const rooms = parseInt($("#id_num_rooms").val()) || 1;
    const maxTotal = selectedMaxGuests * rooms;
    $guestMaxNote.text(
      "Max " +
        selectedMaxGuests +
        " guests per room × " +
        rooms +
        " room" +
        (rooms > 1 ? "s" : "") +
        " = " +
        maxTotal +
        " guests total",
    );
  }

  /* ── Capacity check: total occupants vs max allowed ── */
  function getTotalOccupants() {
    return (
      (parseInt($("#id_num_adults").val()) || 0) +
      (parseInt($("#id_num_children").val()) || 0) +
      (parseInt($("#id_num_infants").val()) || 0)
    );
  }

  function getMaxAllowed() {
    return selectedMaxGuests * (parseInt($("#id_num_rooms").val()) || 1);
  }

  /* ── Generic counter factory ── */
  function makeCounter($minusBtn, $plusBtn, $input, getMin, getMax, onChange) {
    $minusBtn.on("click", function () {
      const cur = parseInt($input.val()) || 0;
      const min = getMin();
      if (cur > min) {
        $input.val(cur - 1);
        if (onChange) onChange();
      }
    });
    $plusBtn.on("click", function () {
      const cur = parseInt($input.val()) || 0;
      const max = getMax();
      if (cur < max) {
        $input.val(cur + 1);
        if (onChange) onChange();
      } else {
        JD.toast(S.maxCapacityReached || "Maximum capacity reached", "error");
      }
    });
  }

  /* ── Rooms counter ── */
  makeCounter(
    $("#btn-rooms-minus"),
    $("#btn-rooms-plus"),
    $("#id_num_rooms"),
    function () {
      return 1;
    },
    function () {
      return 10;
    },
    function () {
      updateGuestNote();
      updatePriceBreakdown();
    },
  );

  /* ── Adults counter ── */
  makeCounter(
    $("#btn-adults-minus"),
    $("#btn-adults-plus"),
    $("#id_num_adults"),
    function () {
      return 1;
    },
    function () {
      return Math.max(
        1,
        getMaxAllowed() -
          getTotalOccupants() +
          (parseInt($("#id_num_adults").val()) || 0),
      );
    },
    null,
  );

  /* ── Children counter ── */
  makeCounter(
    $("#btn-children-minus"),
    $("#btn-children-plus"),
    $("#id_num_children"),
    function () {
      return 0;
    },
    function () {
      return Math.max(
        0,
        getMaxAllowed() -
          getTotalOccupants() +
          (parseInt($("#id_num_children").val()) || 0),
      );
    },
    null,
  );

  /* ── Infants counter ── */
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

  /* ── Pets counter ── */
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

  /* ── Room type card click ── */
  $(document).on("click", ".room-strip-link", function (e) {
    e.stopPropagation();
    // GLightbox handles the actual open — we just prevent card re-selection
  });

  $(document).on("click", ".room-type-card", function (e) {
    // If the click originated inside the photo strip, ignore it entirely
    if ($(e.target).closest(".room-photo-strip").length) return;

    $(".room-type-card").removeClass("selected");
    $(this).addClass("selected");

    selectedRoomId = parseInt($(this).data("room-id"));
    selectedMaxGuests = parseInt($(this).data("max-guests"));
    selectedAllowsPets =
      $(this).data("allows-pets") === true ||
      $(this).data("allows-pets") === "true";

    const room = ROOM_TYPES.find(function (r) {
      return r.id === selectedRoomId;
    });
    if (!room) return;

    selectedPrice = parseFloat(room.display_price);
    $roomIdInput.val(selectedRoomId);

    updatePanelPrice(room);
    applyRoomPolicies(room);
    updateGuestNote();
    updatePriceBreakdown();

    // Show this room's photo strip, hide all others
    $(".room-photo-strip").slideUp(150);
    if (room.photos && room.photos.length) {
      $("#room-strip-" + selectedRoomId).slideDown(200, function () {
        // Reinitialise only after the strip is fully visible
        initRoomLightbox();
      });
    }
  });

  /* ── Initialise with first room on page load ── */
  if (firstRoom) {
    updatePanelPrice(firstRoom);
    applyRoomPolicies(firstRoom);
    updateGuestNote();
    // Show first room's photos on load if it has any
    if (firstRoom.photos && firstRoom.photos.length) {
      $("#room-strip-" + firstRoom.id).show();
    }
  }

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

    // Client-side occupancy guard (server also enforces this)
    const rooms = parseInt($("#id_num_rooms").val()) || 1;
    const maxTotal = selectedMaxGuests * rooms;
    if (getTotalOccupants() > maxTotal) {
      JD.toast(
        "Too many guests: max " + maxTotal + " for " + rooms + " room(s)",
        "error",
      );
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
