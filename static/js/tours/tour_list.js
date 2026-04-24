/* tour_list.js */
(function ($) {
  "use strict";

  var Grid = $("#tours-grid");
  var Empty = $("#tours-empty");
  var Count = $("#results-count");
  var S = window.JD_STRINGS || {};

  function showSkeletons(n) {
    Grid.empty();
    for (var i = 0; i < n; i++) {
      Grid.append(
        '<div class="col-lg-4 col-md-6">' +
          '<div class="tour-skeleton">' +
          '<div class="skeleton-img"></div>' +
          '<div class="skeleton-body">' +
          '<div class="skeleton-line w-80 mb-3"></div>' +
          '<div class="skeleton-line w-60"></div>' +
          '<div class="skeleton-line w-40 mt-3"></div>' +
          "</div>" +
          "</div>" +
          "</div>",
      );
    }
  }

  function renderHighlights(highlights) {
    if (!highlights || !highlights.length) return "";
    var html = "";
    for (var i = 0; i < highlights.length; i++) {
      html +=
        '<li class="tour-card-highlight-item">' +
        escHtml(highlights[i]) +
        "</li>";
    }
    return html;
  }

  function renderCard(t) {
    var imgHtml = t.cover_image
      ? '<img src="' +
        t.cover_image +
        '" alt="' +
        escHtml(t.name) +
        '" class="tour-card-img" loading="lazy">'
      : '<div class="tour-card-img-placeholder"><i class="bi bi-map"></i></div>';

    var featuredBadge = t.is_featured
      ? '<span class="tour-card-featured-badge">' +
        (S.featured || "Featured") +
        "</span>"
      : "";

    var discountBadge = t.has_discount
      ? '<span class="jd-discount-badge" style="position:absolute;top:14px;right:14px;">' +
        t.discount_percent +
        "% " +
        (S.off || "off") +
        "</span>"
      : "";

    var ratingBadge = t.avg_rating
      ? '<span class="jd-rating-badge">' +
        '<i class="bi bi-star-fill"></i> ' +
        t.avg_rating +
        '<span class="jd-rating-count">(' +
        t.review_count +
        ")</span>" +
        "</span>"
      : "";

    var durationLabel =
      t.duration_days === 1
        ? "1 " + (S.day || "day")
        : t.duration_days + " " + (S.days || "days");

    var priceHtml = t.has_discount
      ? '<span class="jd-price-original">$' +
        parseFloat(t.price_per_person).toLocaleString() +
        "</span> " +
        '<span class="tour-card-price-amount">$' +
        parseFloat(t.display_price).toLocaleString() +
        "</span>"
      : '<span class="tour-card-price-amount">$' +
        parseFloat(t.price_per_person).toLocaleString() +
        "</span>";

    return (
      '<div class="col-lg-4 col-md-6 jd-reveal">' +
      '<div class="tour-card">' +
      '<a href="' +
      escHtml(t.url) +
      '" class="tour-card-img-wrap" style="position:relative;">' +
      imgHtml +
      featuredBadge +
      discountBadge +
      '<span class="tour-card-type-badge tour-card-type-badge--' +
      escHtml(t.tour_type) +
      '">' +
      escHtml(t.tour_type_display) +
      "</span>" +
      "</a>" +
      '<div class="tour-card-body">' +
      '<div class="d-flex align-items-center justify-content-between mb-1">' +
      '<h3 class="tour-card-name mb-0">' +
      escHtml(t.name) +
      "</h3>" +
      ratingBadge +
      "</div>" +
      '<div class="tour-card-meta">' +
      '<span class="tour-meta-pill"><i class="bi bi-clock"></i> ' +
      durationLabel +
      "</span>" +
      '<span class="tour-meta-pill"><i class="bi bi-people"></i> ' +
      (S.maxGroup || "Max") +
      " " +
      t.group_size_max +
      " " +
      (S.people || "people") +
      "</span>" +
      "</div>" +
      '<ul class="tour-card-highlights">' +
      renderHighlights(t.highlights) +
      "</ul>" +
      '<div class="tour-card-footer">' +
      "<div>" +
      priceHtml +
      '<div class="tour-card-price-label">' +
      (S.perPerson || "/ person") +
      "</div></div>" +
      '<a href="' +
      escHtml(t.url) +
      '" class="btn-accent-jd" style="padding:10px 22px;font-size:0.7rem;">' +
      (S.viewTour || "View Details") +
      "</a>" +
      "</div>" +
      "</div>" +
      "</div>" +
      "</div>"
    );
  }

  function fetchTours() {
    var params = {
      tour_type: $("#filter-tour-type").val(),
      max_duration: $("#filter-max-duration").val(),
      max_price: $("#filter-max-price").val(),
    };

    showSkeletons(6);
    Empty.hide();

    $.ajax({
      url: window.location.pathname,
      data: params,
      headers: { "X-Requested-With": "XMLHttpRequest" },
      success: function (data) {
        Grid.empty();
        var tours = data.tours || [];
        Count.text(tours.length);

        if (!tours.length) {
          Empty.show();
          return;
        }

        $.each(tours, function (i, t) {
          Grid.append(renderCard(t));
        });

        // Trigger scroll reveal on newly rendered cards
        if (window.JD && window.JD.initReveal) {
          window.JD.initReveal();
        } else {
          Grid.find(".jd-reveal").addClass("revealed");
        }
      },
      error: function () {
        Grid.empty();
        Count.text("—");
        JD.toast(
          S.toursError || "Failed to load tours. Please try again.",
          "error",
        );
      },
    });
  }

  var debounceTimer;
  function onFilterChange() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(fetchTours, 300);
  }

  $("#filter-tour-type, #filter-max-duration, #filter-max-price").on(
    "change",
    onFilterChange,
  );

  function clearFilters() {
    $("#filter-tour-type, #filter-max-duration, #filter-max-price").val("");
    fetchTours();
  }

  $("#btn-clear-filters, #btn-empty-clear").on("click", clearFilters);

  function escHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Initial load
  fetchTours();
})(jQuery);
