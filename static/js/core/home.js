$(function () {
  "use strict";

  var S = window.JD_STRINGS || {};

  /* ----------------------------------------------------------
     1. HERO — Ken Burns effect on load
     ---------------------------------------------------------- */
  setTimeout(function () {
    $(".jd-hero-bg").addClass("loaded");
  }, 100);

  /* ----------------------------------------------------------
     2. BOOKING WIDGET TABS
     ---------------------------------------------------------- */
  $(document).on("click", ".jd-booking-tab", function () {
    if ($(this).hasClass("disabled-tab")) return;

    var target = $(this).data("target");

    $(".jd-booking-tab").removeClass("active");
    $(this).addClass("active");

    $(".jd-booking-panel").removeClass("active");
    $("#" + target).addClass("active");
  });

  /* ----------------------------------------------------------
     3. COUNTER ANIMATION for Why Choose Us stats
     ---------------------------------------------------------- */
  var countersAnimated = false;

  function animateCounters() {
    if (countersAnimated) return;
    countersAnimated = true;

    $(".jd-counter").each(function () {
      var $el = $(this);
      var target = parseInt($el.data("target"), 10);
      var duration = 1800;
      var start = 0;
      var step = Math.ceil(target / (duration / 16));

      var timer = setInterval(function () {
        start += step;
        if (start >= target) {
          start = target;
          clearInterval(timer);
        }
        $el.text(start.toLocaleString());
      }, 16);
    });
  }

  // Use IntersectionObserver to trigger counters
  if ("IntersectionObserver" in window) {
    var counterObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCounters();
            counterObserver.disconnect();
          }
        });
      },
      { threshold: 0.3 },
    );

    var $whySection = $(".jd-why-section")[0];
    if ($whySection) counterObserver.observe($whySection);
  }

  /* ----------------------------------------------------------
     4. BOOKING FORM SUBMIT — redirect to listing pages
        with search parameters
     ---------------------------------------------------------- */

  // Hotels booking form
  $("#booking-form-hotels").on("submit", function (e) {
    e.preventDefault();
    var location = $(this).find('[name="hotel_location"]').val();
    var guests = $(this).find('[name="guests"]').val();
    var price = $(this).find('[name="price"]').val();

    var params = new URLSearchParams();
    params.set("location", location);
    params.set("stars", "");
    params.set("max_price", price);
    params.set("guests", guests);

    window.location.href = "/hotels/?" + params.toString();
  });

  // Tours booking form
  $("#booking-form-tours").on("submit", function (e) {
    e.preventDefault();
    var type = $(this).find('[name="tour_type"]').val();
    var duration = $(this).find('[name="max_duration"]').val();
    var price = $(this).find('[name="max_price"]').val();

    var params = new URLSearchParams();
    params.set("tour_type", type);
    params.set("max_duration", duration);
    params.set("max_price", price);

    window.location.href = "/tours/?" + params.toString();
  });

  // Cars booking form
  $("#booking-form-cars").on("submit", function (e) {
    e.preventDefault();
    var vehicle = $(this).find('[name="vehicle_type"]').val();
    var rental_mode = $(this).find('[name="rental_mode"]').val();
    var max_price = $(this).find('[name="max_price"]').val();

    var params = new URLSearchParams();
    params.set("vehicle_type", vehicle);
    params.set("rental_mode", rental_mode);
    params.set("max_price", max_price);

    window.location.href = "/cars/?" + params.toString();
  });

  /* ----------------------------------------------------------
     5. GALLERY ITEMS — simple lightbox using Bootstrap modal
     ---------------------------------------------------------- */
  function openGalleryModal($item) {
    var imgSrc = $item.data("img");
    var caption = $item.data("caption") || "";

    // Inject or reuse modal
    if ($("#jd-gallery-modal").length === 0) {
      $("body").append(
        '<div class="modal fade" id="jd-gallery-modal" tabindex="-1"' +
          ' aria-label="' +
          (S.viewPhoto || "View photo") +
          '">' +
          '<div class="modal-dialog modal-xl modal-dialog-centered">' +
          '<div class="modal-content bg-dark border-0">' +
          '<div class="modal-body p-0 text-center position-relative">' +
          '<button type="button" class="btn-close btn-close-white position-absolute top-0 end-0 m-3"' +
          ' data-bs-dismiss="modal" aria-label="' +
          (S.close || "Close") +
          '"></button>' +
          '<img id="jd-gallery-modal-img" src="" alt="" style="max-height:85vh;width:100%;object-fit:contain;" />' +
          '<p id="jd-gallery-modal-caption" class="text-white-50 py-3 mb-0" style="font-size:0.85rem;"></p>' +
          "</div>" +
          "</div>" +
          "</div>" +
          "</div>",
      );
    }

    // Caption doubles as the image's accessible name; fall back to generic label.
    $("#jd-gallery-modal-img")
      .attr("src", imgSrc)
      .attr("alt", caption || S.viewPhoto || "View photo");
    $("#jd-gallery-modal-caption").text(caption);
    new bootstrap.Modal(document.getElementById("jd-gallery-modal")).show();
  }

  $(document).on("click", ".jd-gallery-item[data-img]", function () {
    openGalleryModal($(this));
  });

  // Keyboard activation (Enter / Space) — tiles expose role="button" tabindex="0"
  $(document).on("keydown", ".jd-gallery-item[data-img]", function (e) {
    if (e.key === "Enter" || e.key === " " || e.key === "Spacebar") {
      e.preventDefault();
      openGalleryModal($(this));
    }
  });

  /* ----------------------------------------------------------
     6. PACKAGE CARD — subtle tilt effect on hover
     ---------------------------------------------------------- */
  $(document).on("mousemove", ".jd-package-card", function (e) {
    var $card = $(this);
    var offset = $card.offset();
    var x = e.pageX - offset.left;
    var y = e.pageY - offset.top;
    var w = $card.outerWidth();
    var h = $card.outerHeight();

    var rotX = (y / h - 0.5) * 6;
    var rotY = (x / w - 0.5) * -6;

    $card.css(
      "transform",
      "translateY(-8px) perspective(600px) rotateX(" +
        rotX +
        "deg) rotateY(" +
        rotY +
        "deg)",
    );
  });

  $(document).on("mouseleave", ".jd-package-card", function () {
    $(this).css("transform", "");
  });
});
