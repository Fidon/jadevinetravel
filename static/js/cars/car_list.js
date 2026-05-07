/* car_list.js */
(function ($) {
  "use strict";

  const Grid = $("#cars-grid");
  const Empty = $("#cars-empty");
  const Count = $("#results-count");
  const S = window.JD_STRINGS || {};

  function showSkeletons(n) {
    Grid.empty();
    for (let i = 0; i < n; i++) {
      Grid.append(`
        <div class="col-lg-4 col-md-6">
          <div class="car-skeleton">
            <div class="skeleton-img"></div>
            <div class="skeleton-body">
              <div class="skeleton-line w-80 mb-3"></div>
              <div class="skeleton-line w-60"></div>
              <div class="skeleton-line w-40 mt-3"></div>
            </div>
          </div>
        </div>`);
    }
  }

  function renderModes(offersSelfDrive, offersDriver) {
    let html = "";
    if (offersDriver) {
      html += `<span class="car-mode-badge driver">
                 <i class="bi bi-person-fill"></i> ${S.withDriver || "With Driver"}
               </span>`;
    }
    if (offersSelfDrive) {
      html += `<span class="car-mode-badge self-drive">
                 <i class="bi bi-key-fill"></i> ${S.selfDrive || "Self Drive"}
               </span>`;
    }
    return html;
  }

  function renderCard(c) {
    var imgHtml = c.cover_photo
      ? '<img src="' +
        c.cover_photo +
        '" alt="' +
        c.name +
        '" class="car-card-img" loading="lazy">'
      : '<div class="car-card-img-placeholder"><i class="bi bi-car-front-fill"></i></div>';

    var discountBadge = c.has_discount
      ? '<span class="jd-discount-badge" style="position:absolute;top:14px;right:14px;">' +
        c.discount_percent +
        "% " +
        (S.off || "off") +
        "</span>"
      : "";

    var ratingBadge = c.avg_rating
      ? '<span class="jd-rating-badge">' +
        '<i class="bi bi-star-fill"></i> ' +
        c.avg_rating +
        '<span class="jd-rating-count">(' +
        c.review_count +
        ")</span>" +
        "</span>"
      : "";

    var priceHtml = c.has_discount
      ? '<span class="jd-price-original">$' +
        parseFloat(c.price_per_day).toLocaleString() +
        "</span>" +
        '<span class="car-card-price-amount">$' +
        parseFloat(c.display_price).toLocaleString() +
        "</span>"
      : '<span class="car-card-price-amount">$' +
        parseFloat(c.price_per_day).toLocaleString() +
        "</span>";

    return (
      '<div class="col-lg-4 col-md-6 jd-reveal">' +
      '<div class="car-card">' +
      '<div class="car-card-img-wrap" style="position:relative;">' +
      imgHtml +
      '<span class="car-card-type-badge">' +
      c.vehicle_type +
      "</span>" +
      discountBadge +
      "</div>" +
      '<div class="car-card-body">' +
      '<div class="d-flex align-items-center justify-content-between mb-1">' +
      '<h3 class="car-card-name mb-0">' +
      c.name +
      "</h3>" +
      ratingBadge +
      "</div>" +
      '<div class="car-card-specs">' +
      '<span class="car-spec-pill"><i class="bi bi-people-fill"></i> ' +
      c.capacity +
      " " +
      (S.capacity || "passengers") +
      "</span>" +
      '<span class="car-spec-pill"><i class="bi bi-gear-fill"></i> ' +
      c.transmission +
      "</span>" +
      '<span class="car-spec-pill"><i class="bi bi-droplet-fill"></i> ' +
      c.fuel_type +
      "</span>" +
      "</div>" +
      '<div class="car-card-modes">' +
      renderModes(c.offers_self_drive, c.offers_driver) +
      "</div>" +
      '<p class="car-card-desc">' +
      (c.description || "") +
      "</p>" +
      '<div class="car-card-footer">' +
      "<div>" +
      priceHtml +
      '<div class="car-card-price-label">' +
      (S.perDay || "/ day") +
      "</div></div>" +
      '<a href="' +
      c.url +
      '" class="btn-accent-jd" style="padding:10px 22px;font-size:0.7rem;">' +
      (S.viewCar || "View & Book") +
      "</a>" +
      "</div>" +
      "</div>" +
      "</div>" +
      "</div>"
    );
  }

  function fetchCars() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has("vehicle_type") && urlParams.get("vehicle_type") !== "")
      $("#filter-vehicle-type").val(urlParams.get("vehicle_type"));
    if (urlParams.has("max_price") && urlParams.get("max_price") !== "")
      $("#filter-max-price").val(urlParams.get("max_price"));
    if (urlParams.has("rental_mode") && urlParams.get("rental_mode") !== "")
      $("#filter-rental-mode").val(urlParams.get("rental_mode"));

    const params = {
      vehicle_type: $("#filter-vehicle-type").val(),
      rental_mode: $("#filter-rental-mode").val(),
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
        const cars = data.cars || [];
        Count.text(cars.length);

        if (cars.length === 0) {
          Empty.show();
          return;
        }

        cars.forEach(function (c) {
          Grid.append(renderCard(c));
        });

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
          S.carsNotFound || "Failed to load vehicles. Please try again.",
          "error",
        );
      },
    });
  }

  let debounceTimer;
  function onFilterChange() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(fetchCars, 300);
  }

  $("#filter-vehicle-type, #filter-rental-mode, #filter-max-price").on(
    "change",
    onFilterChange,
  );

  function clearFilters() {
    if (window.location.search.length > 1) {
      window.location.href = window.location.pathname;
    } else {
      $("#filter-vehicle-type, #filter-rental-mode, #filter-max-price").val("");
      fetchCars();
    }
  }

  $("#btn-clear-filters, #btn-empty-clear").on("click", clearFilters);

  fetchCars();
})(jQuery);
