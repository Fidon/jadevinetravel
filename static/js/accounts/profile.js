(function ($) {
  "use strict";

  // ── Profile photo live preview ─────────────────────────────────────────
  $("#id_profile_photo").on("change", function () {
    var file = this.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      JD.toast(
        window.JD_STRINGS && window.JD_STRINGS.photoTooLarge
          ? window.JD_STRINGS.photoTooLarge
          : "Photo must be under 5MB.",
        "error",
      );
      this.value = "";
      return;
    }

    var reader = new FileReader();
    reader.onload = function (e) {
      var $preview = $("#photoPreview");
      $preview.find("img").remove();
      $preview.find(".profile-photo-placeholder").remove();
      $("<img>", {
        src: e.target.result,
        id: "photoImg",
        alt: "Profile preview",
      }).appendTo($preview);
    };
    reader.readAsDataURL(file);
  });

  // ── Newsletter subscribe / unsubscribe toggle ──────────────────────────
  $("#newsletterToggleBtn").on("click", function () {
    var $btn = $(this);
    var $label = $("#newsletterStatusLabel");
    var $feedback = $("#newsletterFeedback");
    var subscribed =
      $btn.data("subscribed") === true || $btn.data("subscribed") === "true";

    $btn.prop("disabled", true);
    $feedback.text("").removeClass("text-success text-danger");

    $.ajax({
      url: window.JD_URLS.newsletterToggle,
      method: "POST",
      headers: {
        "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
        "X-Requested-With": "XMLHttpRequest",
      },
      success: function (data) {
        var nowSubscribed = data.subscribed;
        $btn.data("subscribed", nowSubscribed);

        if (nowSubscribed) {
          $btn
            .removeClass("btn-primary-jd")
            .addClass("btn-outline-jd")
            .html(
              '<i class="bi bi-bell-slash me-1"></i>' +
                (window.JD_STRINGS.unsubscribe || "Unsubscribe"),
            );
          $label.html(
            '<i class="bi bi-check-circle-fill text-success me-1"></i>' +
              (window.JD_STRINGS.subscribed || "Subscribed"),
          );
          $feedback
            .addClass("text-success")
            .text(
              window.JD_STRINGS.newsletterSubscribedMsg ||
                "You're now subscribed. Welcome!",
            );
        } else {
          $btn
            .removeClass("btn-outline-jd")
            .addClass("btn-primary-jd")
            .html(
              '<i class="bi bi-bell me-1"></i>' +
                (window.JD_STRINGS.subscribe || "Subscribe"),
            );
          $label.html(
            '<i class="bi bi-x-circle-fill text-muted me-1"></i>' +
              (window.JD_STRINGS.notSubscribed || "Not subscribed"),
          );
          $feedback
            .addClass("text-danger")
            .text(
              window.JD_STRINGS.newsletterUnsubscribedMsg ||
                "You have been unsubscribed.",
            );
        }
      },
      error: function () {
        $feedback
          .addClass("text-danger")
          .text(
            window.JD_STRINGS.genericError ||
              "Something went wrong. Please try again.",
          );
      },
      complete: function () {
        $btn.prop("disabled", false);
      },
    });
  });
})(jQuery);
