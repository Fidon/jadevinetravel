/**
 * favourites.js
 * Shared favourite toggle logic.
 * Exposes window.JD_FAV.init() and window.JD_FAV.toggle().
 *
 * List pages:   call JD_FAV.initCard(el) after inserting each card into DOM.
 * Detail pages: call JD_FAV.initDetail() on DOMContentLoaded.
 *
 * Expected button markup (list card):
 *   <button class="jd-fav-btn"
 *           data-item-type="hotel|tour|car"
 *           data-item-id="<int>"
 *           data-saved="true|false"
 *           aria-label="Save to favourites">
 *     <i class="bi bi-heart[-fill]"></i>
 *   </button>
 *
 * Expected button markup (detail page):
 *   <button class="jd-fav-btn jd-fav-btn--detail"
 *           data-item-type="hotel|tour|car"
 *           data-item-id="<int>"
 *           data-saved="true|false"
 *           data-toggle-url="/favourites/toggle/"
 *           aria-label="Save to favourites">
 *     <i class="bi bi-heart[-fill]"></i>
 *     <span class="jd-fav-label"></span>
 *   </button>
 */
(function ($) {
  "use strict";

  var TOGGLE_URL = "/favourites/toggle/";
  var S = window.JD_STRINGS || {};
  var csrf = function () {
    return (
      $("[name=csrfmiddlewaretoken]").first().val() ||
      (window.PORTAL ? window.PORTAL.csrf() : "")
    );
  };

  /* ── Build button HTML for card injection ── */
  function buildCardBtn(itemType, itemId, isSaved) {
    var icon = isSaved ? "bi-heart-fill" : "bi-heart";
    var cls = isSaved ? "jd-fav-btn jd-fav-btn--saved" : "jd-fav-btn";
    return (
      '<button type="button"' +
      ' class="' +
      cls +
      '"' +
      ' data-item-type="' +
      itemType +
      '"' +
      ' data-item-id="' +
      itemId +
      '"' +
      ' data-saved="' +
      (isSaved ? "true" : "false") +
      '"' +
      ' aria-label="' +
      (S.saveToFavourites || "Save to favourites") +
      '">' +
      '<i class="bi ' +
      icon +
      '"></i>' +
      "</button>"
    );
  }

  /* ── Build button HTML for detail page injection ── */
  function buildDetailBtn(itemType, itemId, isSaved, toggleUrl) {
    var icon = isSaved ? "bi-heart-fill" : "bi-heart";
    var label = isSaved
      ? S.savedToFavourites || "Saved"
      : S.saveToFavourites || "Save";
    var cls = isSaved
      ? "jd-fav-btn jd-fav-btn--detail jd-fav-btn--saved"
      : "jd-fav-btn jd-fav-btn--detail";
    return (
      '<button type="button"' +
      ' class="' +
      cls +
      '"' +
      ' data-item-type="' +
      itemType +
      '"' +
      ' data-item-id="' +
      itemId +
      '"' +
      ' data-saved="' +
      (isSaved ? "true" : "false") +
      '"' +
      ' data-toggle-url="' +
      (toggleUrl || TOGGLE_URL) +
      '"' +
      ' aria-label="' +
      label +
      '">' +
      '<i class="bi ' +
      icon +
      '"></i>' +
      '<span class="jd-fav-label">' +
      label +
      "</span>" +
      "</button>"
    );
  }

  /* ── Apply saved state to a button element ── */
  function applyState($btn, saved) {
    $btn.data("saved", saved ? "true" : "false");
    $btn.attr("data-saved", saved ? "true" : "false");

    var $icon = $btn.find("i");
    $icon.removeClass("bi-heart bi-heart-fill");
    $icon.addClass(saved ? "bi-heart-fill" : "bi-heart");

    if (saved) {
      $btn.addClass("jd-fav-btn--saved");
    } else {
      $btn.removeClass("jd-fav-btn--saved");
    }

    var $label = $btn.find(".jd-fav-label");
    if ($label.length) {
      $label.text(
        saved ? S.savedToFavourites || "Saved" : S.saveToFavourites || "Save",
      );
    }
  }

  /* ── Core toggle AJAX call ── */
  function toggle($btn) {
    var itemType = $btn.data("item-type");
    var itemId = $btn.data("item-id");
    var url = $btn.data("toggle-url") || TOGGLE_URL;
    var wasSaved = $btn.data("saved") === "true" || $btn.data("saved") === true;

    // Optimistic UI update
    applyState($btn, !wasSaved);
    $btn.prop("disabled", true);

    $.ajax({
      url: url,
      method: "POST",
      data: {
        item_type: itemType,
        item_id: itemId,
        csrfmiddlewaretoken: csrf(),
      },
      success: function (data) {
        if (data.requires_login) {
          // Revert optimistic update and redirect
          applyState($btn, wasSaved);
          window.location.href =
            "/accounts/login/?next=" +
            encodeURIComponent(window.location.pathname);
          return;
        }
        // Confirm server state (server is authority)
        applyState($btn, data.saved);

        if (data.saved) {
          JD.toast(S.addedToFavourites || "Added to favourites", "success");
        } else {
          JD.toast(
            S.removedFromFavourites || "Removed from favourites",
            "info",
          );
        }
      },
      error: function () {
        // Revert on error
        applyState($btn, wasSaved);
        JD.toast(
          S.favouriteError || "Could not update favourites. Try again.",
          "error",
        );
      },
      complete: function () {
        $btn.prop("disabled", false);
      },
    });
  }

  /* ── Delegated click handler — works for dynamically inserted buttons ── */
  $(document).on("click", ".jd-fav-btn", function (e) {
    e.preventDefault();
    e.stopPropagation(); // prevent card link click-through
    toggle($(this));
  });

  /* ── Public API ── */
  window.JD_FAV = {
    buildCardBtn: buildCardBtn,
    buildDetailBtn: buildDetailBtn,
    applyState: applyState,
  };
})(jQuery);
