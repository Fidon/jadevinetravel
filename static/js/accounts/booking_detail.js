(function ($) {
  "use strict";

  // ── Cancellation modal ───────────────────────────────────────────────────

  var $modal = $("#cancelModal");
  var $openBtn = $("#cancelBookingBtn");
  var $close1 = $("#cancelModalClose");
  var $close2 = $("#cancelModalClose2");

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
    $close1.on("click", closeModal);
    $close2.on("click", closeModal);

    $modal.on("click", function (e) {
      if ($(e.target).is($modal)) closeModal();
    });

    $(document).on("keydown", function (e) {
      if (e.key === "Escape" && $modal.hasClass("open")) closeModal();
    });

    var $submitBtn = $('#cancelForm button[type="submit"]');
    var $confirmChk = $("#id_confirm");

    function updateSubmitState() {
      $submitBtn.prop("disabled", !$confirmChk.is(":checked"));
    }

    updateSubmitState();
    $confirmChk.on("change", updateSubmitState);

    $("#cancelForm").on("submit", function () {
      $submitBtn
        .prop("disabled", true)
        .text(
          window.JD_STRINGS && window.JD_STRINGS.processing
            ? window.JD_STRINGS.processing
            : "Processing…",
        );
    });
  }

  // ── Star rating picker ───────────────────────────────────────────────────

  var $picker = $("#starPicker");
  var $ratingInput = $("#id_rating");
  var $starLabel = $("#starLabel");
  var $reviewBtn = $("#reviewSubmitBtn");

  if ($picker.length) {
    var LABELS = {
      1:
        window.JD_STRINGS && window.JD_STRINGS.rating1
          ? window.JD_STRINGS.rating1
          : "Terrible",
      2:
        window.JD_STRINGS && window.JD_STRINGS.rating2
          ? window.JD_STRINGS.rating2
          : "Very Poor",
      3:
        window.JD_STRINGS && window.JD_STRINGS.rating3
          ? window.JD_STRINGS.rating3
          : "Poor",
      4:
        window.JD_STRINGS && window.JD_STRINGS.rating4
          ? window.JD_STRINGS.rating4
          : "Below Average",
      5:
        window.JD_STRINGS && window.JD_STRINGS.rating5
          ? window.JD_STRINGS.rating5
          : "Average",
      6:
        window.JD_STRINGS && window.JD_STRINGS.rating6
          ? window.JD_STRINGS.rating6
          : "Good",
      7:
        window.JD_STRINGS && window.JD_STRINGS.rating7
          ? window.JD_STRINGS.rating7
          : "Very Good",
      8:
        window.JD_STRINGS && window.JD_STRINGS.rating8
          ? window.JD_STRINGS.rating8
          : "Excellent",
      9:
        window.JD_STRINGS && window.JD_STRINGS.rating9
          ? window.JD_STRINGS.rating9
          : "Outstanding",
      10:
        window.JD_STRINGS && window.JD_STRINGS.rating10
          ? window.JD_STRINGS.rating10
          : "Perfect",
    };

    var currentRating = 0;

    function applyStars(value) {
      $picker.find(".dash-star-btn").each(function () {
        var n = parseInt($(this).data("value"), 10);
        $(this).toggleClass("dash-star-hover", n <= value);
      });
    }

    function commitStars(value) {
      currentRating = value;
      $ratingInput.val(value);
      $starLabel.text(value + "/10 — " + (LABELS[value] || ""));
      $reviewBtn.prop("disabled", false);

      $picker.find(".dash-star-btn").each(function () {
        var n = parseInt($(this).data("value"), 10);
        $(this)
          .toggleClass("dash-star-active", n <= value)
          .toggleClass("dash-star-hover", false);
      });
    }

    // Hover: preview stars
    $picker.on("mouseenter", ".dash-star-btn", function () {
      applyStars(parseInt($(this).data("value"), 10));
    });

    // Mouse leave: revert to committed rating
    $picker.on("mouseleave", function () {
      applyStars(currentRating);
      $picker.find(".dash-star-btn").each(function () {
        var n = parseInt($(this).data("value"), 10);
        $(this).toggleClass("dash-star-hover", false);
      });
    });

    // Click: commit rating
    $picker.on("click", ".dash-star-btn", function () {
      commitStars(parseInt($(this).data("value"), 10));
    });

    // Keyboard: space/enter on focused star button
    $picker.on("keydown", ".dash-star-btn", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        commitStars(parseInt($(this).data("value"), 10));
      }
    });

    // Guard: block submit if rating still 0 (JS bypass attempt)
    $("#reviewForm").on("submit", function (e) {
      if (!$ratingInput.val() || parseInt($ratingInput.val(), 10) < 1) {
        e.preventDefault();
        JD.toast(
          window.JD_STRINGS && window.JD_STRINGS.ratingRequired
            ? window.JD_STRINGS.ratingRequired
            : "Please select a rating before submitting.",
          "error",
        );
        return;
      }
      $reviewBtn
        .prop("disabled", true)
        .html(
          '<i class="bi bi-hourglass-split me-1"></i>' +
            (window.JD_STRINGS && window.JD_STRINGS.processing
              ? window.JD_STRINGS.processing
              : "Processing…"),
        );
    });
  }
})(jQuery);
