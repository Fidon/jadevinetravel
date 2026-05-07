(function ($) {
  "use strict";

  // -------------------------------------------------------------------------
  // Sidebar toggle (mobile)
  // -------------------------------------------------------------------------
  var $sidebar = $("#portalSidebar");
  var $overlay = $("#sidebarOverlay");
  var $toggleBtn = $("#sidebarToggle");

  function openSidebar() {
    $sidebar.addClass("is-open");
    $overlay.addClass("is-visible");
    $toggleBtn.attr("aria-expanded", "true");
    $("body").css("overflow", "hidden"); // prevent body scroll on mobile
  }

  function closeSidebar() {
    $sidebar.removeClass("is-open");
    $overlay.removeClass("is-visible");
    $toggleBtn.attr("aria-expanded", "false");
    $("body").css("overflow", "");
  }

  $toggleBtn.on("click", function () {
    $sidebar.hasClass("is-open") ? closeSidebar() : openSidebar();
  });

  $overlay.on("click", closeSidebar);

  // Close sidebar on ESC
  $(document).on("keydown", function (e) {
    if (e.key === "Escape" && $sidebar.hasClass("is-open")) {
      closeSidebar();
    }
  });

  // Close sidebar when a nav link is tapped on mobile
  $(".portal-nav-link").on("click", function () {
    if ($(window).width() < 992) {
      closeSidebar();
    }
  });

  // -------------------------------------------------------------------------
  // Flash message auto-dismiss + close button
  // -------------------------------------------------------------------------
  (function () {
    // Auto-dismiss success and info alerts after 5 seconds
    setTimeout(function () {
      $(".portal-alert--success, .portal-alert--info").fadeOut(400);
    }, 5000);

    $(document).on("click", ".portal-alert-close", function () {
      $(this).closest(".portal-alert").fadeOut(300);
    });
  })();

  // -------------------------------------------------------------------------
  // Pending approvals polling (Super Admin only)
  // Polls /portal/api/pending-count/ every 60 seconds.
  // Updates sidebar badge and topbar badge without page reload.
  // Does nothing for mini-admins (server returns zeros; window.PORTAL.isMiniAdmin check skips the interval).
  // -------------------------------------------------------------------------
  (function () {
    if (!window.PORTAL || window.PORTAL.isMiniAdmin) return;

    var POLL_INTERVAL = 60000; // 60 seconds
    var $topbarBadge = $(".pending-count-badge"); // topbar + sidebar badge (same class)
    var $navBadge = $(".portal-nav-link .pending-count-badge"); // sidebar nav badge specifically

    function updatePendingCount(data) {
      var total = data.total || 0;

      // Update all .pending-count-badge elements
      $(".pending-count-badge").text(total);

      // Toggle zero state on topbar badge container
      var $topbarContainer = $(".portal-topbar-badge");
      if (total === 0) {
        $topbarContainer.addClass("portal-topbar-badge--zero");
      } else {
        $topbarContainer.removeClass("portal-topbar-badge--zero");
      }

      // Show/hide sidebar nav badge
      var $sidebarBadge = $(".portal-nav-link .pending-count-badge");
      if (total === 0) {
        $sidebarBadge.hide();
      } else {
        $sidebarBadge.show().text(total);
      }

      // Update any dashboard-specific count elements
      $(".js-pending-hotels-count").text(data.hotels || 0);
      $(".js-pending-cars-count").text(data.cars || 0);
      $(".js-pending-total-count").text(total);
    }

    function pollPendingCount() {
      $.ajax({
        url: window.PORTAL.urls.pendingCount,
        method: "GET",
        dataType: "json",
        timeout: 8000,
        success: function (data) {
          updatePendingCount(data);
        },
        error: function () {
          // Silent fail — stale count is better than broken UI
        },
      });
    }

    // Start polling after 60 seconds (not immediately — page just loaded with correct count)
    setInterval(pollPendingCount, POLL_INTERVAL);
  })();

  // -------------------------------------------------------------------------
  // CSRF token helper (mirrors public site JD.csrfToken())
  // Usage: PORTAL.csrf()
  // -------------------------------------------------------------------------
  if (window.PORTAL) {
    window.PORTAL.csrf = function () {
      return (
        window.PORTAL.csrfToken || $("[name=csrfmiddlewaretoken]").val() || ""
      );
    };
  }

  // Shared confirm modal for all destructive actions.
  // Usage: add data-confirm="message" + data-confirm-title="Title" (optional)
  // to any <button type="submit"> inside a <form>, or any <a> tag.
  // The modal intercepts the click, shows confirmation, then submits/follows on proceed.

  var $confirmModal = $("#confirmModal");
  var $confirmProceed = $("#confirm-modal-proceed");
  var $confirmBody = $("#confirm-modal-body");
  var $confirmTitle = $("#confirm-modal-title");
  var _pendingAction = null; // stores { type: 'form'|'link', target: element }

  $(document).on("click", "[data-confirm]", function (e) {
    e.preventDefault();
    e.stopPropagation();
    window._photoDeletePending = false;

    var msg = $(this).data("confirm") || "Are you sure?";
    var title = $(this).data("confirm-title") || "Confirm Action";

    $confirmBody.text(msg);
    $confirmTitle.text(title);

    var $el = $(this);
    if ($el.is('button[type="submit"]')) {
      _pendingAction = { type: "form", form: $el.closest("form")[0] };
    } else if ($el.is("a")) {
      _pendingAction = { type: "link", href: $el.attr("href") };
    } else {
      _pendingAction = null;
    }

    $confirmModal.modal("show");
  });

  $confirmProceed.on("click", function () {
    $confirmModal.modal("hide");

    // Photo delete is handled separately via AJAX in portal_hotels.js
    // portal_hotels.js sets window._photoDeletePending and listens for this event
    if (window._photoDeletePending) {
      $(document).trigger("portal:photo-delete-confirmed");
      window._photoDeletePending = false;
      return;
    }

    if (!_pendingAction) return;
    if (_pendingAction.type === "form" && _pendingAction.form) {
      _pendingAction.form.submit();
    } else if (_pendingAction.type === "link" && _pendingAction.href) {
      window.location.href = _pendingAction.href;
    }
    _pendingAction = null;
  });

  // Clean up on modal close without confirming
  $confirmModal.on("hidden.bs.modal", function () {
    _pendingAction = null;
  });

  // -------------------------------------------------------------------------
  // Auto-submit status/filter forms on select change (tables with filter dropdowns)
  // Usage: add class .portal-autosubmit to any <select> inside a <form>
  // -------------------------------------------------------------------------
  $(document).on("change", ".portal-autosubmit", function () {
    $(this).closest("form").submit();
  });

  // -------------------------------------------------------------------------
  // DataTables default configuration factory
  // Usage in page JS:
  //   PORTAL.initDataTable('#my-table', { extraOption: value });
  // -------------------------------------------------------------------------
  if (window.PORTAL && typeof $.fn.DataTable !== "undefined") {
    window.PORTAL.initDataTable = function (selector, overrides) {
      var defaults = {
        responsive: true,
        pageLength: 25,
        order: [[0, "desc"]],
        dom: '<"dt-top"Bf>rt<"dt-bottom"ip>',
        buttons: [
          {
            extend: "excel",
            className: "btn",
            text: '<i class="bi bi-file-earmark-excel"></i> Excel',
            title: document.title,
          },
          {
            extend: "pdf",
            className: "btn",
            text: '<i class="bi bi-file-earmark-pdf"></i> PDF',
            title: document.title,
            orientation: "landscape",
            pageSize: "A4",
          },
          {
            extend: "print",
            className: "btn",
            text: '<i class="bi bi-printer"></i> Print',
            title: document.title,
          },
        ],
        language: {
          search: "",
          searchPlaceholder: "Search...",
          lengthMenu: "Show _MENU_",
          info: "Showing _START_–_END_ of _TOTAL_",
          infoEmpty: "No records found",
          paginate: {
            previous: '<i class="bi bi-chevron-left"></i>',
            next: '<i class="bi bi-chevron-right"></i>',
          },
        },
      };

      var options = $.extend(true, {}, defaults, overrides || {});
      return $(selector).DataTable(options);
    };
  }

  // Update footer clock
  function updateClock() {
    const now = new Date();

    const day = now.getDate().toString().padStart(2, "0");
    const month = now.toLocaleString("en-GB", { month: "short" });
    const year = now.getFullYear();

    const hours = now.getHours().toString().padStart(2, "0");
    const minutes = now.getMinutes().toString().padStart(2, "0");
    const seconds = now.getSeconds().toString().padStart(2, "0");

    // Format: DD MMM YYYY - HH:mm:ss
    const fullString = `${day} ${month} ${year} - ${hours}:${minutes}:${seconds}`;

    const clockElement = document.getElementById("liveClock");
    if (clockElement) {
      clockElement.textContent = fullString;
    }
  }

  // Update immediately, then every second
  updateClock();
  setInterval(updateClock, 1000);
})(jQuery);
