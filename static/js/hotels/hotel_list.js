/* hotel_list.js — AJAX filter + card rendering */
(function ($) {
  "use strict";

  const Grid = $("#hotels-grid");
  const Loading = $("#hotels-loading");
  const Empty = $("#hotels-empty");
  const Count = $("#results-count");

  /* ── Skeleton placeholders shown on initial load ── */
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

  /* ── Star HTML helper ── */
  function renderStars(count) {
    let html = "";
    for (let i = 1; i <= 5; i++) {
      html += `<i class="bi bi-star${i <= count ? "-fill" : ""}"></i>`;
    }
    return html;
  }

  /* ── Render one hotel card ── */
  function renderCard(h) {
    const imgHtml = h.cover_photo
      ? `<img src="${h.cover_photo}" alt="${h.name}" class="hotel-card-img" loading="lazy">`
      : `<div class="hotel-card-img-placeholder"><i class="bi bi-building"></i></div>`;

    // Discount badge
    const discountBadge = h.has_discount
      ? `<span class="jd-discount-badge position-absolute" style="top:14px;right:14px;">
           ${h.discount_percent}% ${window.JD_STRINGS.off || "off"}
         </span>`
      : "";

    // Rating badge
    const ratingBadge = h.avg_rating
      ? `<span class="jd-rating-badge">
           <i class="bi bi-star-fill"></i>
           ${h.avg_rating}
           <span class="jd-rating-count">(${h.review_count})</span>
         </span>`
      : "";

    // Price display
    const priceHtml = h.has_discount
      ? `<span class="jd-price-original">$${parseFloat(h.price_per_night).toLocaleString()}</span>
         <span class="hotel-card-price-amount">$${parseFloat(h.display_price).toLocaleString()}</span>`
      : `<span class="hotel-card-price-amount">$${parseFloat(h.price_per_night).toLocaleString()}</span>`;

    return `
      <div class="col-lg-4 col-md-6 jd-reveal">
        <div class="hotel-card">
          <div class="hotel-card-img-wrap" style="position:relative;">
            ${imgHtml}
            <span class="hotel-card-location-badge">${h.location}</span>
            ${discountBadge}
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
                <span class="hotel-card-price-label">${window.JD_STRINGS.perNight || "per night"}</span>
              </div>
              <a href="${h.url}" class="btn-accent-jd" style="padding:10px 22px;font-size:0.7rem;">
                ${window.JD_STRINGS.viewHotel || "View Hotel"}
              </a>
            </div>
          </div>
        </div>
      </div>`;
  }

  /* ── Fetch from backend ── */
  function fetchHotels() {
    const params = {
      location: $("#filter-location").val(),
      stars: $("#filter-stars").val(),
      max_price: $("#filter-max-price").val(),
      guests: $("#filter-guests").val(),
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

        /* Trigger scroll reveal on newly inserted cards */
        if (window.JD && window.JD.initReveal) {
          window.JD.initReveal();
        } else {
          /* Fallback: just make them visible */
          Grid.find(".jd-reveal").addClass("revealed");
        }
      },
      error: function () {
        Grid.empty();
        Count.text("—");
        JD.toast(
          window.JD_STRINGS.hotelsNotFound ||
            "Failed to load hotels. Please try again.",
          "error",
        );
      },
    });
  }

  /* ── Filter change handler with debounce ── */
  let debounceTimer;
  function onFilterChange() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(fetchHotels, 300);
  }

  $("#filter-location, #filter-stars, #filter-max-price, #filter-guests").on(
    "change",
    onFilterChange,
  );

  function clearFilters() {
    $("#filter-location, #filter-stars, #filter-max-price, #filter-guests").val(
      "",
    );
    fetchHotels();
  }

  $("#btn-clear-filters, #btn-empty-clear").on("click", clearFilters);

  /* ── Initial load ── */
  fetchHotels();
})(jQuery);
