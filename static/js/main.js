$(function () {
  /* ----------------------------------------------------------
     1. NAVBAR — scroll state + hamburger + mobile menu
     ---------------------------------------------------------- */
  var $navbar = $(".jd-navbar");
  var $hamburger = $(".jd-hamburger");
  var $mobileMenu = $(".jd-mobile-menu");
  var heroHeight = 80; // px from top before navbar goes solid
  var isAlwaysSolid = $navbar.hasClass("navbar-scrolled");

  function updateNavbar() {
    if (isAlwaysSolid) return;
    if ($(window).scrollTop() > heroHeight) {
      $navbar.removeClass("navbar-transparent").addClass("navbar-scrolled");
    } else {
      $navbar.addClass("navbar-transparent").removeClass("navbar-scrolled");
    }
  }

  // Run on load and on scroll
  updateNavbar();
  $(window).on("scroll.navbar", updateNavbar);

  // Hamburger toggle
  $hamburger.on("click", function () {
    var isOpen = $mobileMenu.hasClass("open");
    $hamburger.toggleClass("open", !isOpen);
    $mobileMenu.toggleClass("open", !isOpen);
    $("body").toggleClass("overflow-hidden", !isOpen);
  });

  // Close mobile menu when a link is clicked
  $mobileMenu.on("click", "a", function () {
    $hamburger.removeClass("open");
    $mobileMenu.removeClass("open");
    $("body").removeClass("overflow-hidden");
  });

  // Close on ESC
  $(document).on("keydown", function (e) {
    if (e.key === "Escape" && $mobileMenu.hasClass("open")) {
      $hamburger.removeClass("open");
      $mobileMenu.removeClass("open");
      $("body").removeClass("overflow-hidden");
    }
  });

  /* ----------------------------------------------------------
     2. ACTIVE NAV LINK — highlight current page
     ---------------------------------------------------------- */
  var currentPath = window.location.pathname;
  $(".jd-nav-link, .jd-mobile-nav-link").each(function () {
    var href = $(this).attr("href");
    if (href && href !== "/" && currentPath.startsWith(href)) {
      $(this).addClass("active");
    } else if (href === "/" && currentPath === "/") {
      $(this).addClass("active");
    }
  });

  /* ----------------------------------------------------------
     3. SCROLL REVEAL — IntersectionObserver for .jd-reveal
     ---------------------------------------------------------- */
  if ("IntersectionObserver" in window) {
    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            $(entry.target).addClass("revealed");
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 },
    );

    $(".jd-reveal").each(function () {
      revealObserver.observe(this);
    });
  } else {
    // Fallback for old browsers
    $(".jd-reveal").addClass("revealed");
  }

  /* ----------------------------------------------------------
     3b. PAGE-LOAD REVEAL — staggered reveal for above-fold
         structural elements marked with .jd-load-reveal.
         Also exposes JD.initReveal() so page JS can call it
         after dynamically injecting cards.
     ---------------------------------------------------------- */
  function triggerLoadReveals() {
    $(".jd-load-reveal").each(function () {
      var $el = $(this);
      var delay = parseInt($el.attr("data-delay") || "0", 10);
      // Base delay 80ms per step so the sequence feels natural
      setTimeout(function () {
        $el.addClass("revealed");
      }, delay * 80);
    });
  }

  // Fire on DOMContentLoaded — already inside $(function(){}) so fires immediately
  triggerLoadReveals();

  // Expose initReveal so page JS (tour_list.js, car_list.js, hotel_list.js)
  // can call JD.initReveal() after injecting cards into the DOM.
  // Observes any .jd-reveal elements not yet being watched.
  window.JD = window.JD || {};
  JD.initReveal = function () {
    if (!("IntersectionObserver" in window)) {
      $(".jd-reveal").addClass("revealed");
      return;
    }
    $(".jd-reveal:not([data-observed])").each(function () {
      $(this).attr("data-observed", "1");
      revealObserver.observe(this);
    });
  };

  /* ----------------------------------------------------------
     4. TOAST NOTIFICATIONS
     Usage: JD.toast('Message here', 'success')
     Types: 'success', 'error', 'info', '' (default)
     ---------------------------------------------------------- */
  window.JD = window.JD || {};

  JD.toast = function (message, type, duration) {
    type = type || "";
    duration = duration || 3500;

    var iconMap = {
      success: "bi-check-circle-fill",
      error: "bi-x-circle-fill",
      info: "bi-info-circle-fill",
      "": "bi-bell-fill",
    };

    var icon = iconMap[type] || iconMap[""];

    var $toast = $(
      '<div class="jd-toast toast-' +
        type +
        '">' +
        '<i class="bi ' +
        icon +
        '"></i>' +
        "<span>" +
        message +
        "</span>" +
        "</div>",
    );

    // Create container if it doesn't exist
    if ($("#jd-toast-container").length === 0) {
      $("body").append('<div id="jd-toast-container"></div>');
    }

    $("#jd-toast-container").append($toast);

    // Trigger animation after paint
    setTimeout(function () {
      $toast.addClass("show");
    }, 10);

    // Auto dismiss
    setTimeout(function () {
      $toast.removeClass("show");
      setTimeout(function () {
        $toast.remove();
      }, 400);
    }, duration);
  };

  /* ----------------------------------------------------------
     5. CSRF HELPER — for AJAX POST requests
     Usage: JD.csrfToken()
     ---------------------------------------------------------- */
  JD.csrfToken = function () {
    return $("[name=csrfmiddlewaretoken]").val() || getCookie("csrftoken");
  };

  function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  }

  /* ----------------------------------------------------------
     6. LANGUAGE SWITCHER
     ---------------------------------------------------------- */
  $(document).on("click", ".jd-lang-btn", function () {
    var lang = $(this).data("lang");
    if (!lang) return;

    // Submit Django's built-in language form
    var $form = $("<form>", {
      method: "POST",
      action: "/i18n/set_language/",
    });

    $form.append(
      $("<input>", {
        type: "hidden",
        name: "csrfmiddlewaretoken",
        value: JD.csrfToken(),
      }),
    );
    $form.append(
      $("<input>", { type: "hidden", name: "language", value: lang }),
    );
    $form.append(
      $("<input>", {
        type: "hidden",
        name: "next",
        value: window.location.pathname,
      }),
    );

    $("body").append($form);
    $form.submit();
  });

  /* ----------------------------------------------------------
     7. SMOOTH SCROLL for anchor links
     ---------------------------------------------------------- */
  $(document).on("click", 'a[href^="#"]', function (e) {
    var target = $(this).attr("href");
    if (target.length > 1 && $(target).length) {
      e.preventDefault();
      var offset = parseInt($(".jd-navbar").css("height")) + 20;
      $("html, body").animate(
        {
          scrollTop: $(target).offset().top - offset,
        },
        600,
      );
    }
  });

  /* ----------------------------------------------------------
     8. NEWSLETTER FORM (global — used on homepage + footer)
     ---------------------------------------------------------- */
  $(document).on("submit", ".jd-newsletter-form", function (e) {
    e.preventDefault();
    var $form = $(this);
    var $btn = $form.find("[type=submit]");
    var $input = $form.find("input[type=email]");
    var email = $input.val().trim();

    if (!email) return;

    $btn.prop("disabled", true).text("...");

    $.ajax({
      url: "/contact/newsletter/",
      method: "POST",
      data: { email: email, csrfmiddlewaretoken: JD.csrfToken() },
      success: function (res) {
        if (res.success) {
          JD.toast(res.message || "Subscribed! Thank you.", "success");
          $input.val("");
        } else {
          JD.toast(res.error || "Something went wrong.", "error");
        }
      },
      error: function () {
        JD.toast("Network error. Please try again.", "error");
      },
      complete: function () {
        $btn.prop("disabled", false).text("Subscribe");
      },
    });
  });
});
