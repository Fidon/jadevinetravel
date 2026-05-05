(function ($) {
  "use strict";

  var S = window.JD_STRINGS || {};
  var csrf = window.JD ? JD.csrfToken() : $("[name=csrfmiddlewaretoken]").val();

  // ── Inquiry type tab switching ────────────────────────────────────────
  $(document).on("click", ".contact-inquiry-tab", function () {
    $(".contact-inquiry-tab").removeClass("active");
    $(this).addClass("active");
    $("#inquiryTypeInput").val($(this).data("value"));
  });

  // ── Character count on textarea ───────────────────────────────────────
  $("#contactMessage").on("input", function () {
    var len = $(this).val().length;
    $("#contactCharCount").text(len + " " + (S.characters || "characters"));
  });

  // ── Inline field validation helpers ──────────────────────────────────
  function showError(fieldId, errorId, msg) {
    $("#" + fieldId).addClass("is-invalid");
    $("#" + errorId)
      .text(msg)
      .addClass("visible");
  }

  function clearError(fieldId, errorId) {
    $("#" + fieldId).removeClass("is-invalid");
    $("#" + errorId)
      .text("")
      .removeClass("visible");
  }

  function clearAllErrors() {
    ["contactName", "contactEmail", "contactSubject", "contactMessage"].forEach(
      function (id) {
        clearError(id, id + "Error");
      },
    );
  }

  // Clear error on input
  $("#contactName, #contactEmail, #contactSubject, #contactMessage").on(
    "input",
    function () {
      var id = $(this).attr("id");
      clearError(id, id + "Error");
    },
  );

  // ── Client-side validation ────────────────────────────────────────────
  function validateForm() {
    var valid = true;

    var name = $("#contactName").val().trim();
    if (!name) {
      showError(
        "contactName",
        "contactNameError",
        S.fieldRequired || "This field is required.",
      );
      valid = false;
    }

    var email = $("#contactEmail").val().trim();
    if (!email || email.indexOf("@") === -1) {
      showError(
        "contactEmail",
        "contactEmailError",
        S.invalidEmail || "Please enter a valid email address.",
      );
      valid = false;
    }

    var subject = $("#contactSubject").val().trim();
    if (!subject) {
      showError(
        "contactSubject",
        "contactSubjectError",
        S.fieldRequired || "This field is required.",
      );
      valid = false;
    }

    var msg = $("#contactMessage").val().trim();
    if (!msg || msg.length < 10) {
      showError(
        "contactMessage",
        "contactMessageError",
        S.messageTooShort || "Message must be at least 10 characters.",
      );
      valid = false;
    }

    return valid;
  }

  // ── Form submit ───────────────────────────────────────────────────────
  $("#contactForm").on("submit", function (e) {
    e.preventDefault();
    clearAllErrors();

    if (!validateForm()) return;

    var $btn = $("#contactSubmitBtn");
    var $label = $("#contactSubmitLabel");

    $btn.prop("disabled", true);
    $label.text(S.sending || "Sending…");

    $.ajax({
      url: S.contactUrl || "/contact/",
      method: "POST",
      data: $(this).serialize(),
      success: function (res) {
        if (res.success) {
          // Hide form, show success state
          $("#contactForm").fadeOut(300, function () {
            $("#contactSuccessState").fadeIn(300);
          });
        } else {
          // Server returned field errors
          if (res.errors) {
            var fieldMap = {
              name: "contactName",
              email: "contactEmail",
              subject: "contactSubject",
              message: "contactMessage",
            };
            $.each(res.errors, function (field, msg) {
              var id = fieldMap[field];
              if (id) {
                showError(id, id + "Error", msg);
              } else if (window.JD && JD.toast) {
                JD.toast(msg, "error");
              }
            });
          }
          $btn.prop("disabled", false);
          $label.text(S.sendMessage || "Send Message");
        }
      },
      error: function () {
        if (window.JD && JD.toast) {
          JD.toast(
            S.networkError || "Network error. Please try again.",
            "error",
          );
        }
        $btn.prop("disabled", false);
        $label.text(S.sendMessage || "Send Message");
      },
    });
  });

  // ── "Send another message" button ─────────────────────────────────────
  $("#contactSendAnother").on("click", function () {
    $("#contactSuccessState").hide();
    $("#contactForm").trigger("reset");
    $("#contactCharCount").text("0 " + (S.characters || "characters"));
    // Reset inquiry tab to general
    $(".contact-inquiry-tab").removeClass("active");
    $('.contact-inquiry-tab[data-value="general"]').addClass("active");
    $("#inquiryTypeInput").val("general");
    clearAllErrors();
    $("#contactForm").fadeIn(300);
    $("#contactSubmitBtn").prop("disabled", false);
    $("#contactSubmitLabel").text(S.sendMessage || "Send Message");
  });
})(jQuery);
