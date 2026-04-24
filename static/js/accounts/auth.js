(function ($) {
  "use strict";

  // Password visibility toggle
  $(document).on("click", ".jd-input-toggle-password", function () {
    var $btn = $(this);
    var $input = $btn
      .closest(".jd-input-icon-wrap")
      .find('input[type="password"], input[type="text"]');
    var isPassword = $input.attr("type") === "password";
    $input.attr("type", isPassword ? "text" : "password");
    $btn
      .find("i")
      .toggleClass("bi-eye", !isPassword)
      .toggleClass("bi-eye-slash", isPassword);
  });

  // Auto-dismiss info/success messages after 4 seconds
  setTimeout(function () {
    $(".auth-alert-info, .auth-alert-success").fadeOut(400, function () {
      $(this).remove();
    });
  }, 4000);
})(jQuery);
