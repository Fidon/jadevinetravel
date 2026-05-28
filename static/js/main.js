$(function () {
  /* ----------------------------------------------------------
     1. NAVBAR — scroll state + hamburger + mobile menu
     ---------------------------------------------------------- */
  var $navbar = $(".jd-navbar");
  var $hamburger = $(".jd-hamburger");
  var $mobileMenu = $(".jd-mobile-menu");
  var heroHeight = 80;
  var isAlwaysSolid = $navbar.hasClass("navbar-scrolled");

  function updateNavbar() {
    if (isAlwaysSolid) return;
    if ($(window).scrollTop() > heroHeight) {
      $navbar.removeClass("navbar-transparent").addClass("navbar-scrolled");
    } else {
      $navbar.addClass("navbar-transparent").removeClass("navbar-scrolled");
    }
  }

  updateNavbar();
  $(window).on("scroll.navbar", updateNavbar);

  $hamburger.on("click", function () {
    var isOpen = $mobileMenu.hasClass("open");
    $hamburger.toggleClass("open", !isOpen);
    $mobileMenu.toggleClass("open", !isOpen);
    $("body").toggleClass("overflow-hidden", !isOpen);
  });

  $mobileMenu.on("click", "a", function () {
    $hamburger.removeClass("open");
    $mobileMenu.removeClass("open");
    $("body").removeClass("overflow-hidden");
  });

  $(document).on("keydown", function (e) {
    if (e.key === "Escape" && $mobileMenu.hasClass("open")) {
      $hamburger.removeClass("open");
      $mobileMenu.removeClass("open");
      $("body").removeClass("overflow-hidden");
    }
  });

  /* ----------------------------------------------------------
     2. ACTIVE NAV LINK
     ---------------------------------------------------------- */
  var currentPath = window.location.pathname;

  // Longest-match algorithm — prevents /hotels/ activating when on /hotels/detail/
  function setActiveLink($links) {
    var bestMatch = "";
    var $bestEl = null;

    $links.each(function () {
      var href = $(this).attr("href");
      if (!href || href === "#") return;

      if (href === "/" || href === "") {
        if (currentPath === "/" || currentPath === "") {
          if (href.length > bestMatch.length) {
            bestMatch = href;
            $bestEl = $(this);
          }
        }
      } else if (currentPath.startsWith(href)) {
        if (href.length > bestMatch.length) {
          bestMatch = href;
          $bestEl = $(this);
        }
      }
    });

    if ($bestEl) $bestEl.addClass("active");
  }

  setActiveLink($(".jd-nav-link"));
  setActiveLink($(".jd-mobile-nav-link"));

  /* ----------------------------------------------------------
     3. SCROLL REVEAL
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
    $(".jd-reveal").addClass("revealed");
  }

  function triggerLoadReveals() {
    $(".jd-load-reveal").each(function () {
      var $el = $(this);
      var delay = parseInt($el.attr("data-delay") || "0", 10);
      setTimeout(function () {
        $el.addClass("revealed");
      }, delay * 80);
    });
  }
  triggerLoadReveals();

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

    var $toast = $(
      '<div class="jd-toast toast-' +
        type +
        '">' +
        '<i class="bi ' +
        (iconMap[type] || iconMap[""]) +
        '"></i>' +
        "<span>" +
        message +
        "</span>" +
        "</div>",
    );

    if ($("#jd-toast-container").length === 0) {
      $("body").append('<div id="jd-toast-container"></div>');
    }

    $("#jd-toast-container").append($toast);
    setTimeout(function () {
      $toast.addClass("show");
    }, 10);
    setTimeout(function () {
      $toast.removeClass("show");
      setTimeout(function () {
        $toast.remove();
      }, 400);
    }, duration);
  };

  /* ----------------------------------------------------------
     5. CSRF HELPER
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
        Shared handler — used by:
        a) Floating pill (desktop + mobile)
        b) Mobile menu inline buttons
     ---------------------------------------------------------- */
  function submitLang(lang) {
    if (!lang) return;
    var cleanPath = window.location.pathname.replace(
      /^\/(en|fr|ru|sw)(\/|$)/,
      "/",
    );
    var $form = $("<form>", { method: "POST", action: "/i18n/setlang/" });
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
      $("<input>", { type: "hidden", name: "next", value: cleanPath }),
    );
    $("body").append($form);
    $form.submit();
  }

  // ── Floating pill ──────────────────────────────────────────
  var $floatLang = $("#jd-float-lang");
  var $floatPill = $("#jd-float-lang-pill");
  var $floatDropdown = $("#jd-float-lang-dropdown");

  $floatPill.on("click", function (e) {
    e.stopPropagation();
    var isOpen = $floatLang.hasClass("open");
    $floatLang.toggleClass("open", !isOpen);
    $floatPill.attr("aria-expanded", !isOpen);
  });

  // Click on a language option in the floating dropdown
  $floatDropdown.on("click", ".jd-float-lang-item", function () {
    submitLang($(this).data("lang"));
  });

  // Close when clicking outside
  $(document).on("click.floatlang", function (e) {
    if (!$(e.target).closest("#jd-float-lang").length) {
      $floatLang.removeClass("open");
      $floatPill.attr("aria-expanded", "false");
    }
  });

  // Close on ESC
  $(document).on("keydown.floatlang", function (e) {
    if (e.key === "Escape") {
      $floatLang.removeClass("open");
      $floatPill.attr("aria-expanded", "false");
    }
  });

  // ── Mobile menu inline language buttons ───────────────────
  $(document).on("click", ".jd-lang-option", function () {
    submitLang($(this).data("lang"));
  });

  /* ----------------------------------------------------------
     7. SMOOTH SCROLL
     ---------------------------------------------------------- */
  $(document).on("click", 'a[href^="#"]', function (e) {
    var target = $(this).attr("href");
    if (target.length > 1 && $(target).length) {
      e.preventDefault();
      var offset = parseInt($(".jd-navbar").css("height")) + 20;
      $("html, body").animate(
        { scrollTop: $(target).offset().top - offset },
        600,
      );
    }
  });

  /* ----------------------------------------------------------
     8. NEWSLETTER FORM
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
