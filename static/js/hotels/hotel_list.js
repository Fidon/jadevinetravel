/* hotel_list.js */
(function ($) {
  "use strict";

  const Grid = $("#hotels-grid");
  const Loading = $("#hotels-loading");
  const Empty = $("#hotels-empty");
  const Count = $("#results-count");
  const S = window.JD_STRINGS || {};

  function showSkeletons(n) {
    Grid.empty();
    for (let i = 0; i < n; i++) {
      Grid.append(`
        <div class="col-lg-4 col-md-6">
          <div class="hotel-skeleton">
            <div class="skeleton-img"></div>
            <div class="skeleton-body">
              <div class="skeleton-line w-40 mb-3"></div>
              <div class="skeleton-line w-80"></div>
              <div class="skeleton-line w-60"></div>
              <div class="skeleton-line w-80 mt-3"></div>
            </div>
          </div>
        </div>`);
    }
  }

  function renderStars(count) {
    let html = "";
    for (let i = 1; i <= 5; i++) {
      html += `<i class="bi bi-star${i <= count ? "-fill" : ""}"></i>`;
    }
    return html;
  }

  function renderCard(h) {
    const imgHtml = h.cover_photo
      ? `<img src="${h.cover_photo}" alt="${h.name}" class="hotel-card-img" loading="lazy">`
      : `<div class="hotel-card-img-placeholder"><i class="bi bi-building"></i></div>`;

    const discountBadge = h.has_discount
      ? `<span class="jd-discount-badge position-absolute" style="top:14px;right:14px;">
           ${h.discount_percent}% ${S.off || "off"}
         </span>`
      : "";

    // Favourite button — bottom-right corner of image
    const favBtn =
      typeof JD_FAV !== "undefined"
        ? JD_FAV.buildCardBtn(h.item_type, h.id, h.is_saved)
        : "";

    const ratingBadge = h.avg_rating
      ? `<span class="jd-rating-badge">
           <i class="bi bi-star-fill"></i>
           ${h.avg_rating}
           <span class="jd-rating-count">(${h.review_count})</span>
         </span>`
      : "";

    const priceHtml = h.has_discount
      ? `<span class="jd-price-original">$${parseFloat(h.price_per_night).toLocaleString()}</span>
         <span class="hotel-card-price-amount">$${parseFloat(h.display_price).toLocaleString()}</span>`
      : `<span class="hotel-card-price-amount">$${parseFloat(h.price_per_night).toLocaleString()}</span>`;

    return `
      <div class="col-lg-4 col-md-6 jd-reveal">
        <div class="hotel-card">
          <div class="hotel-card-img-wrap" style="position:relative;">
            <a href="${h.url}">${imgHtml}</a>
            <span class="hotel-card-location-badge">${h.location}</span>
            ${discountBadge}
            ${favBtn}
          </div>
          <div class="hotel-card-body">
            <div class="d-flex align-items-center justify-content-between mb-1">
              <div class="hotel-card-stars">${renderStars(h.stars)}</div>
              ${ratingBadge}
            </div>
            <h3 class="hotel-card-name">${h.name}</h3>
            <p class="hotel-card-desc">${h.description || ""}</p>
            <div class="hotel-card-footer">
              <div class="hotel-card-price">
                ${priceHtml}
                <span class="hotel-card-price-label">${S.perNight || "per night"}</span>
              </div>
              <a href="${h.url}" class="btn-accent-jd" style="padding:10px 22px;font-size:0.7rem;">
                ${S.viewHotel || "View Hotel"}
              </a>
            </div>
          </div>
        </div>
      </div>`;
  }

  function fetchHotels() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has("location") && urlParams.get("location") !== "")
      $("#filter-location").val(urlParams.get("location"));
    if (urlParams.has("max_price") && urlParams.get("max_price") !== "")
      $("#filter-max-price").val(urlParams.get("max_price"));
    if (urlParams.has("guests") && urlParams.get("guests") !== "")
      $("#filter-guests").val(urlParams.get("guests"));
    if (urlParams.has("q") && urlParams.get("q") !== "")
      $("#search-input").val(urlParams.get("q"));

    const params = {
      location: $("#filter-location").val(),
      stars: $("#filter-stars").val(),
      max_price: $("#filter-max-price").val(),
      guests: $("#filter-guests").val(),
      q: $("#search-input").val().trim(),
    };

    showSkeletons(6);
    Empty.hide();

    $.ajax({
      url: window.location.pathname,
      data: params,
      headers: { "X-Requested-With": "XMLHttpRequest" },
      success: function (data) {
        Grid.empty();
        const hotels = data.hotels || [];
        Count.text(hotels.length);

        if (hotels.length === 0) {
          Empty.show();
          return;
        }

        hotels.forEach(function (h) {
          Grid.append(renderCard(h));
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
          S.hotelsNotFound || "Failed to load hotels. Please try again.",
          "error",
        );
      },
    });
  }

  let debounceTimer;
  function onFilterChange() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(fetchHotels, 300);
  }

  $("#filter-location, #filter-stars, #filter-max-price, #filter-guests").on(
    "change",
    onFilterChange,
  );
  $("#search-input").on("input", onFilterChange);

  // Show/hide inline clear button on search input
  $("#search-input").on("input", function () {
    $("#btn-search-clear").toggle($(this).val().length > 0);
  });
  $("#btn-search-clear").on("click", function () {
    $("#search-input").val("").trigger("input");
  });

  function clearFilters() {
    if (window.location.search.length > 1) {
      window.location.href = window.location.pathname;
    } else {
      $(
        "#filter-location, #filter-stars, #filter-max-price, #filter-guests",
      ).val("");
      $("#search-input").val("");
      $("#btn-search-clear").hide();
      fetchHotels();
    }
  }

  $("#btn-clear-filters, #btn-empty-clear").on("click", clearFilters);

  fetchHotels();
})(jQuery);
