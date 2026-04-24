(function ($) {
  "use strict";

  var $sidebar = $("#dashboardSidebar");
  var $overlay = $("#sidebarOverlay");
  var $toggleBtn = $("#sidebarToggleBtn");
  var $closeBtn = $("#sidebarCloseBtn");

  function openSidebar() {
    $sidebar.addClass("open");
    $overlay.addClass("active");
    $("body").css("overflow", "hidden");
    $closeBtn.focus();
  }

  function closeSidebar() {
    $sidebar.removeClass("open");
    $overlay.removeClass("active");
    $("body").css("overflow", "");
  }

  $toggleBtn.on("click", openSidebar);
  $closeBtn.on("click", closeSidebar);
  $overlay.on("click", closeSidebar);

  // ESC to close
  $(document).on("keydown", function (e) {
    if (e.key === "Escape" && $sidebar.hasClass("open")) {
      closeSidebar();
    }
  });

  // Close sidebar on desktop resize (if accidentally open)
  $(window).on("resize", function () {
    if ($(window).width() >= 992) {
      closeSidebar();
    }
  });
})(jQuery);
