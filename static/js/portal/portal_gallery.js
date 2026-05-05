(function ($) {
  "use strict";

  var URLS = window.GALLERY_URLS || {};
  var CAT_ID = window.GALLERY_CATEGORY_ID || "";
  var STRINGS = window.JD_STRINGS || {};
  var csrf = window.PORTAL.csrfToken;

  // ── Flash helper ─────────────────────────────────────────────────────────
  function showFlash(msg, type) {
    var icon = type === "success" ? "bi-check-circle-fill" : "bi-x-circle-fill";
    var $alert = $(
      '<div class="portal-alert portal-alert--' +
        type +
        '" role="alert">' +
        '<i class="bi ' +
        icon +
        '"></i>' +
        msg +
        '<button type="button" class="portal-alert-close" aria-label="Close">' +
        '<i class="bi bi-x"></i></button></div>',
    );
    var $container = $(".portal-messages");
    if (!$container.length) {
      $container = $('<div class="portal-messages"></div>');
      $(".portal-content").prepend($container);
    }
    $container.append($alert);
    setTimeout(function () {
      $alert.fadeOut(400, function () {
        $(this).remove();
      });
    }, 4000);
  }

  // ── Build a gallery item card from server response ────────────────────────
  function buildItemCard(data) {
    var deleteUrl = URLS.deleteBase.replace("__ID__", data.item_id);
    var featUrl = URLS.featuredBase.replace("__ID__", data.item_id);
    var thumbHtml = "";

    if (data.media_type === "photo") {
      thumbHtml = '<img src="' + data.url + '" alt="" loading="lazy">';
    } else {
      thumbHtml =
        '<div class="gallery-video-thumb">' +
        '<i class="bi bi-play-circle-fill"></i>' +
        '<span class="gallery-video-label">VIDEO</span>' +
        "</div>";
    }

    return $(
      '<div class="gallery-item" data-item-id="' +
        data.item_id +
        '" ' +
        'data-is-featured="false">' +
        '<div class="gallery-thumb">' +
        thumbHtml +
        '<div class="gallery-item-actions">' +
        '<button type="button" class="photo-action-btn gallery-featured-btn" ' +
        'data-item-id="' +
        data.item_id +
        '" ' +
        'data-featured-url="' +
        featUrl +
        '" ' +
        'title="Feature on homepage">' +
        '<i class="bi bi-star" style="color:#fff;font-size:0.85rem;"></i>' +
        "</button>" +
        '<button type="button" class="photo-action-btn photo-action-btn--delete ' +
        'gallery-delete-btn" data-item-id="' +
        data.item_id +
        '" ' +
        'data-delete-url="' +
        deleteUrl +
        '" title="Delete">' +
        '<i class="bi bi-trash"></i>' +
        "</button>" +
        "</div></div>" +
        (data.caption
          ? '<p class="gallery-item-caption">' + data.caption + "</p>"
          : "") +
        "</div>",
    );
  }

  // ── Photo upload — sequential queue ──────────────────────────────────────
  $("#galleryPhotoInput").on("change", function () {
    var files = Array.from(this.files);
    if (!files.length || !CAT_ID) return;

    var total = files.length;
    var uploaded = 0;
    var $progress = $("#galleryUploadProgress");
    var $fill = $("#galleryUploadFill");
    var $label = $("#galleryUploadLabel");

    $progress.show();

    function uploadNext() {
      if (uploaded >= total) {
        $progress.hide();
        $fill.css("width", "0%");
        // Clear the input so the same files can be re-selected if needed
        $("#galleryPhotoInput").val("");
        return;
      }

      var file = files[uploaded];
      $label.text("Uploading " + (uploaded + 1) + " of " + total + "…");
      $fill.css("width", Math.round((uploaded / total) * 100) + "%");

      var fd = new FormData();
      fd.append("image", file);
      fd.append("media_type", "photo");
      fd.append("category_id", CAT_ID);
      fd.append("csrfmiddlewaretoken", csrf);

      $.ajax({
        url: URLS.upload,
        method: "POST",
        data: fd,
        processData: false,
        contentType: false,
        success: function (data) {
          if (data.success) {
            var $card = buildItemCard(data);
            var $grid = $("#galleryGrid");
            if (!$grid.length) {
              // Grid doesn't exist yet (was empty) — rebuild section
              location.reload();
              return;
            }
            $grid.append($card);
            // Re-init sortable on the new item
            $grid.sortable("refresh");
          } else {
            showFlash(data.error || STRINGS.uploadError, "error");
          }
          uploaded++;
          uploadNext();
        },
        error: function () {
          showFlash(STRINGS.uploadError || "Upload failed.", "error");
          uploaded++;
          uploadNext();
        },
      });
    }

    uploadNext();
  });

  // ── Video URL submit ──────────────────────────────────────────────────────
  $("#addVideoForm").on("submit", function (e) {
    e.preventDefault();
    var url = $("#videoUrlInput").val().trim();
    var caption = $("#videoCaptionInput").val().trim();
    var $submit = $("#addVideoSubmit");

    if (!url || !CAT_ID) return;

    $submit.prop("disabled", true).text("Adding…");

    $.ajax({
      url: URLS.upload,
      method: "POST",
      data: {
        media_type: "video",
        video_url: url,
        caption_en: caption,
        category_id: CAT_ID,
        csrfmiddlewaretoken: csrf,
      },
      success: function (data) {
        if (data.success) {
          $("#addVideoModal").modal("hide");
          $("#videoUrlInput").val("");
          $("#videoCaptionInput").val("");
          var $grid = $("#galleryGrid");
          if (!$grid.length) {
            location.reload();
            return;
          }
          $grid.append(buildItemCard(data));
          $grid.sortable("refresh");
          showFlash(STRINGS.videoSuccess || "Video added.", "success");
        } else {
          showFlash(
            data.error || STRINGS.videoError || "Could not add video.",
            "error",
          );
        }
        $submit
          .prop("disabled", false)
          .html('<i class="bi bi-check-lg"></i> Add Video');
      },
      error: function () {
        showFlash(STRINGS.videoError || "Could not add video.", "error");
        $submit
          .prop("disabled", false)
          .html('<i class="bi bi-check-lg"></i> Add Video');
      },
    });
  });

  // ── Delete item ───────────────────────────────────────────────────────────
  // Uses shared #confirmModal from portal_base.js
  $(document).on("click", ".gallery-delete-btn", function () {
    var $btn = $(this);
    var url = $btn.data("delete-url");

    window._photoDeletePending = true;
    $("#confirm-modal-title").text(
      STRINGS.deleteTitle || "Delete Gallery Item",
    );
    $("#confirm-modal-body").text(
      STRINGS.deleteConfirm || "Delete this item? This cannot be undone.",
    );
    $("#confirmModal").data("gallery-delete-url", url);
    $("#confirmModal").data("gallery-item-id", $btn.data("item-id"));
    $("#confirmModal").modal("show");
  });

  $(document).on("portal:photo-delete-confirmed", function () {
    if (!window._photoDeletePending) return;
    window._photoDeletePending = false;

    var url = $("#confirmModal").data("gallery-delete-url");
    var itemId = $("#confirmModal").data("gallery-item-id");

    if (!url) return;

    $.ajax({
      url: url,
      method: "POST",
      headers: { "X-CSRFToken": csrf },
      success: function (data) {
        if (data.success) {
          $('[data-item-id="' + itemId + '"]').fadeOut(300, function () {
            $(this).remove();
          });
        } else {
          showFlash("Could not delete item.", "error");
        }
      },
      error: function () {
        showFlash("Could not delete item.", "error");
      },
    });
  });

  // ── Toggle featured ───────────────────────────────────────────────────────
  $(document).on("click", ".gallery-featured-btn", function () {
    var $btn = $(this);
    var url = $btn.data("featured-url");
    var $item = $btn.closest(".gallery-item");

    $btn.prop("disabled", true);

    $.ajax({
      url: url,
      method: "POST",
      headers: { "X-CSRFToken": csrf },
      success: function (data) {
        if (data.success) {
          var isFeatured = data.is_featured;
          $item.attr("data-is-featured", isFeatured ? "true" : "false");
          $btn.toggleClass("is-featured", isFeatured);
          $btn
            .find("i")
            .removeClass("bi-star bi-star-fill")
            .addClass(isFeatured ? "bi-star-fill" : "bi-star");

          // Badge on thumbnail
          $item.find(".gallery-featured-badge").remove();
          if (isFeatured) {
            $item
              .find(".gallery-thumb")
              .prepend(
                '<span class="gallery-featured-badge">' +
                  '<i class="bi bi-star-fill"></i></span>',
              );
          }

          showFlash(
            isFeatured
              ? STRINGS.featuredOn || "Added to homepage highlights."
              : STRINGS.featuredOff || "Removed from homepage highlights.",
            "success",
          );
        }
        $btn.prop("disabled", false);
      },
      error: function () {
        $btn.prop("disabled", false);
        showFlash("Could not update featured status.", "error");
      },
    });
  });

  // ── Drag-to-reorder (jQuery UI Sortable) ─────────────────────────────────
  var $grid = $("#galleryGrid");
  if ($grid.length) {
    $grid.sortable({
      items: ".gallery-item",
      tolerance: "pointer",
      placeholder: "gallery-item gallery-item-placeholder",
      forcePlaceholderSize: true,
      delay: 120, // prevents accidental drags on click
      stop: function () {
        var order = [];
        $grid.find(".gallery-item").each(function () {
          order.push(parseInt($(this).data("item-id"), 10));
        });
        $.ajax({
          url: URLS.reorder,
          method: "POST",
          contentType: "application/json",
          data: JSON.stringify({ order: order }),
          headers: { "X-CSRFToken": csrf },
          error: function () {
            showFlash("Could not save order. Please try again.", "error");
          },
        });
      },
    });
    $grid.disableSelection();
  }

  // ── Edit category modal ───────────────────────────────────────────────────
  $(document).on("click", ".gallery-edit-cat-btn", function () {
    var $btn = $(this);
    var catId = $btn.data("cat-id");
    var url = URLS.catEditBase.replace("__ID__", catId);

    $("#editCatNameEn").val($btn.data("cat-name-en"));
    $("#editCatNameFr").val($btn.data("cat-name-fr"));
    $("#editCatNameRu").val($btn.data("cat-name-ru"));
    $("#editCategoryForm").attr("action", url);
    $("#editCategoryModal").modal("show");
  });
})(jQuery);
