(function ($) {
  "use strict";

  var csrf = window.PORTAL
    ? window.PORTAL.csrf()
    : $("[name=csrfmiddlewaretoken]").first().val();

  // =========================================================================
  // REJECTION MODAL — list page + detail page
  // Populates the form action and hotel name when the reject button is clicked
  // =========================================================================
  $(document).on("click", '[data-bs-target="#rejectModal"]', function () {
    var $btn = $(this);
    var hotelPk = $btn.data("hotel-pk");
    var hotelName = $btn.data("hotel-name");
    var nextVal = $btn.data("next") || "";

    $("#rejectModal #reject-hotel-name").text(hotelName);
    $("#rejectModal #reject-next").val(nextVal);

    // Build reject URL — detail page already sets action; list page needs dynamic URL
    // Use a pattern string injected from template if available
    var actionUrl = "/portal/hotels/" + hotelPk + "/reject/";
    $("#reject-form").attr("action", actionUrl);

    // Reset textarea and disable submit
    $("#id_rejection_reason").val("");
    $("#reject-submit-btn").prop("disabled", true);
  });

  // Enable submit button once rejection reason has ≥ 10 chars
  $(document).on("input", "#id_rejection_reason", function () {
    var len = $(this).val().trim().length;
    $("#reject-submit-btn").prop("disabled", len < 10);
  });

  // =========================================================================
  // LANGUAGE TABS — form page (FR / RU descriptions)
  // =========================================================================
  $(document).on("click", ".lang-tab", function () {
    var target = $(this).data("target");
    $(".lang-tab").removeClass("active");
    $(this).addClass("active");
    $("#desc-fr, #desc-ru").hide();
    $(target).show();
  });

  // =========================================================================
  // EDIT ROOM MODAL — populate fields from data attributes
  // =========================================================================
  $(document).on("click", ".js-edit-room-btn", function () {
    var roomId = parseInt($(this).data("room-id"));
    var roomTypes = window.HOTEL_ROOM_TYPES || [];
    var rt = null;
    for (var i = 0; i < roomTypes.length; i++) {
      if (roomTypes[i].id === roomId) {
        rt = roomTypes[i];
        break;
      }
    }
    if (!rt) return;

    var $modal = $("#editRoomModal");
    $modal.find('[name="name"]').val(rt.name);
    $modal.find('[name="description_en"]').val(rt.description_en);
    $modal.find('[name="description_fr"]').val(rt.description_fr);
    $modal.find('[name="description_ru"]').val(rt.description_ru);
    $modal.find('[name="price_per_night"]').val(rt.price_per_night);
    $modal.find('[name="max_guests"]').val(rt.max_guests);
    $modal.find('[name="discount_percent"]').val(rt.discount_percent);
    $modal.find('[name="discount_expires_at"]').val(rt.discount_expires_at);
    $modal.find('[name="amenities_text"]').val(rt.amenities.join("\n"));
    $modal.find('[name="is_refundable"]').prop("checked", rt.is_refundable);
    $modal
      .find('[name="allows_pay_on_arrival"]')
      .prop("checked", rt.allows_pay_on_arrival);
    $modal.find('[name="is_available"]').prop("checked", rt.is_available);
    $modal.find('[name="description_fr"]').val(rt.description_fr);
    $modal.find('[name="description_ru"]').val(rt.description_ru);

    $("#edit-room-form").attr("action", rt.edit_url);
  });

  // =========================================================================
  // PHOTO MANAGEMENT — hotel detail page only
  // Runs only when HOTEL_URLS is defined (set in portal_hotel_detail.html)
  // =========================================================================
  if (!window.HOTEL_URLS) return;

  var URLS = window.HOTEL_URLS;
  var $grid = $("#photo-grid");
  var $uploadArea = $("#photo-upload-area");
  var $fileInput = $("#photo-file-input");
  var $spinner = $("#upload-spinner");

  // ── Upload ──────────────────────────────────────────────────────────────
  $uploadArea.on("click", function (e) {
    if (!$(e.target).is($fileInput)) {
      $fileInput.trigger("click");
    }
  });

  $fileInput.on("click", function (e) {
    e.stopPropagation();
  });

  $uploadArea.on("dragover", function (e) {
    e.preventDefault();
    $uploadArea.addClass("drag-over");
  });

  $uploadArea.on("dragleave drop", function (e) {
    e.preventDefault();
    $uploadArea.removeClass("drag-over");
    if (e.type === "drop") {
      uploadFiles(e.originalEvent.dataTransfer.files);
    }
  });

  $fileInput.on("change", function () {
    uploadFiles(this.files);
    this.value = ""; // reset so same file can be re-uploaded if needed
  });

  function uploadFiles(files) {
    if (!files || files.length === 0) return;
    $spinner.show();

    // Upload sequentially to avoid overwhelming the server
    var queue = Array.from(files);

    function uploadNext() {
      if (queue.length === 0) {
        $spinner.hide();
        return;
      }
      var file = queue.shift();
      var fd = new FormData();
      fd.append("image", file);
      fd.append("csrfmiddlewaretoken", csrf);

      $.ajax({
        url: URLS.photoUpload,
        method: "POST",
        data: fd,
        processData: false,
        contentType: false,
        success: function (data) {
          if (data.success) {
            appendPhotoToGrid(data);
          } else {
            JD.toast(data.error || "Upload failed", "error");
          }
          uploadNext();
        },
        error: function () {
          JD.toast("Upload failed. Please try again.", "error");
          uploadNext();
        },
      });
    }

    uploadNext();
  }

  function appendPhotoToGrid(data) {
    var html =
      '<div class="photo-item' +
      (data.is_cover ? " is-cover" : "") +
      '" data-photo-id="' +
      data.photo_id +
      '">' +
      '<img src="' +
      data.url +
      '" alt="photo" loading="lazy">' +
      (data.is_cover ? '<span class="photo-cover-badge">Cover</span>' : "") +
      '<div class="photo-item-actions">' +
      '<button type="button" class="photo-action-btn photo-action-btn--cover js-set-cover" data-photo-id="' +
      data.photo_id +
      '" title="Set as cover"><i class="bi bi-star-fill"></i></button>' +
      '<button type="button" class="photo-action-btn photo-action-btn--delete js-delete-photo" data-photo-id="' +
      data.photo_id +
      '" title="Delete"><i class="bi bi-trash3"></i></button>' +
      "</div>" +
      "</div>";
    $grid.append(html);
    // Reinitialise sortable to include new item
    initSortable();
  }

  // ── Set cover ────────────────────────────────────────────────────────────
  $(document).on("click", ".js-set-cover", function (e) {
    e.stopPropagation();
    var photoId = $(this).data("photo-id");
    var url = URLS.photoSetCover.replace("__ID__", photoId);

    $.post(url, { csrfmiddlewaretoken: csrf }, function (data) {
      if (data.success) {
        // Update cover state in DOM
        $grid.find(".photo-item").removeClass("is-cover");
        $grid.find(".photo-cover-badge").remove();
        var $item = $grid.find('[data-photo-id="' + data.photo_id + '"]');
        $item.addClass("is-cover");
        $item.prepend('<span class="photo-cover-badge">Cover</span>');
      }
    });
  });

  // ── Delete ───────────────────────────────────────────────────────────────
  var _pendingPhotoDelete = null;
  $(document).on("click", ".js-delete-photo", function (e) {
    e.stopPropagation();
    var photoId = $(this).data("photo-id");
    var $item = $(this).closest(".photo-item");
    _pendingPhotoDelete = { photoId: photoId, $item: $item };

    $("#confirm-modal-title").text("Delete Photo");
    $("#confirm-modal-body").text("Delete this photo? This cannot be undone.");
    window._photoDeletePending = true;
    $("#confirmModal").modal("show");
  });

  $(document).on("portal:photo-delete-confirmed", function () {
    if (!_pendingPhotoDelete) return;
    var photoId = _pendingPhotoDelete.photoId;
    var $item = _pendingPhotoDelete.$item;
    _pendingPhotoDelete = null;

    var url = URLS.photoDelete.replace("__ID__", photoId);
    $.post(url, { csrfmiddlewaretoken: csrf }, function (data) {
      if (data.success) {
        $item.fadeOut(200, function () {
          $(this).remove();
        });
      } else {
        JD.toast("Could not delete photo. Please try again.", "error");
      }
    });
  });

  // ── Drag-to-reorder (jQuery UI Sortable) ─────────────────────────────────
  function initSortable() {
    if (typeof $.fn.sortable === "undefined") return; // jQuery UI not loaded
    $grid.sortable({
      items: ".photo-item",
      cursor: "grabbing",
      opacity: 0.8,
      stop: function () {
        var order = [];
        $grid.find(".photo-item").each(function () {
          order.push(parseInt($(this).data("photo-id")));
        });
        $.ajax({
          url: URLS.photoReorder,
          method: "POST",
          contentType: "application/json",
          data: JSON.stringify({ order: order }),
          headers: { "X-CSRFToken": csrf },
        });
      },
    });
  }

  initSortable();
})(jQuery);
