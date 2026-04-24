(function ($) {
  "use strict";

  // Live preview for profile photo upload
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
})(jQuery);
