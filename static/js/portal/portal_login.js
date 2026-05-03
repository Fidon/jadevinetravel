(function ($) {
  "use strict";

  // Password visibility toggle
  $(document).on("click", ".password-toggle", function () {
    var $btn = $(this);
    var $input = $("#id_password");
    var $icon = $("#pwd-eye");

    var isPassword = $input.attr("type") === "password";

    $input.attr("type", isPassword ? "text" : "password");

    $icon
      .toggleClass("bi-eye", !isPassword)
      .toggleClass("bi-eye-slash", isPassword);
  });
})(jQuery);
