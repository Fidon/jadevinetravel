(function ($) {
  "use strict";

  var TOGGLE_URL =
    window.JD_URLS && window.JD_URLS.toggleFavourite
      ? window.JD_URLS.toggleFavourite
      : "/accounts/favourites/toggle/";

  $(document).on("click", ".fav-remove-btn", function () {
    var $btn = $(this);
    var $card = $btn.closest(".fav-item");
    var itemType = $btn.data("item-type");
    var itemId = $btn.data("item-id");

    $btn.prop("disabled", true);

    $.ajax({
      url: TOGGLE_URL,
      method: "POST",
      contentType: "application/json",
      headers: { "X-Requested-With": "XMLHttpRequest" },
      data: JSON.stringify({ item_type: itemType, item_id: itemId }),
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-CSRFToken", JD.csrfToken());
      },
      success: function (data) {
        if (!data.saved) {
          // Animate out and remove
          $card.addClass("removing");
          setTimeout(function () {
            $card.remove();
            // Check if grid is now empty
            if ($("#favouritesGrid .fav-item").length === 0) {
              location.reload();
            }
          }, 320);
        }
      },
      error: function () {
        $btn.prop("disabled", false);
        JD.toast(
          window.JD_STRINGS && window.JD_STRINGS.removeError
            ? window.JD_STRINGS.removeError
            : "Could not remove. Please try again.",
          "error",
        );
      },
    });
  });
})(jQuery);
