(function ($) {
  "use strict";

  var csrf = window.PORTAL
    ? window.PORTAL.csrf()
    : $("[name=csrfmiddlewaretoken]").first().val();

  // =========================================================================
  // REJECTION MODAL
  // =========================================================================
  $(document).on("click", '[data-bs-target="#rejectModal"]', function () {
    var $btn = $(this);
    var hotelPk = $btn.data("hotel-pk");
    var nextVal = $btn.data("next") || "";

    $("#rejectModal #reject-hotel-name").text($btn.data("hotel-name"));
    $("#rejectModal #reject-next").val(nextVal);
    $("#reject-form").attr("action", "/portal/hotels/" + hotelPk + "/reject/");
    $("#id_rejection_reason").val("");
    $("#reject-submit-btn").prop("disabled", true);
  });

  $(document).on("input", "#id_rejection_reason", function () {
    $("#reject-submit-btn").prop("disabled", $(this).val().trim().length < 10);
  });

  // =========================================================================
  // LANGUAGE TABS
  // =========================================================================
  $(document).on("click", ".lang-tab", function () {
    var target = $(this).data("target");
    $(".lang-tab").removeClass("active");
    $(this).addClass("active");
    $("#desc-fr, #desc-ru").hide();
    $(target).show();
  });

  // =========================================================================
  // EDIT ROOM MODAL — populate fields from HOTEL_ROOM_TYPES data
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
    $modal.find('[name="allows_pets"]').prop("checked", rt.allows_pets);
    $modal.find('[name="is_available"]').prop("checked", rt.is_available);
    $("#edit-room-form").attr("action", rt.edit_url);
  });

  // =========================================================================
  // HOTEL PHOTO MANAGEMENT
  // Runs only when HOTEL_URLS is defined (portal_hotel_detail.html only)
  // =========================================================================
  if (!window.HOTEL_URLS) return;

  var URLS = window.HOTEL_URLS;
  var $grid = $("#photo-grid");
  var $uploadArea = $("#photo-upload-area");
  var $fileInput = $("#photo-file-input");
  var $spinner = $("#upload-spinner");

  // ── Hotel photo upload ───────────────────────────────────────────────────
  $uploadArea.on("click", function (e) {
    if (!$(e.target).is($fileInput)) $fileInput.trigger("click");
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
    if (e.type === "drop") uploadHotelFiles(e.originalEvent.dataTransfer.files);
  });
  $fileInput.on("change", function () {
    uploadHotelFiles(this.files);
    this.value = "";
  });

  function uploadHotelFiles(files) {
    if (!files || !files.length) return;
    $spinner.show();
    var queue = Array.from(files);

    function next() {
      if (!queue.length) {
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
          if (data.success) appendHotelPhoto(data);
          else JD.toast(data.error || "Upload failed", "error");
          next();
        },
        error: function () {
          JD.toast("Upload failed.", "error");
          next();
        },
      });
    }
    next();
  }

  function appendHotelPhoto(data) {
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
      "</div></div>";
    $grid.append(html);
    initHotelSortable();
  }

  // ── Hotel set cover ──────────────────────────────────────────────────────
  $(document).on("click", ".js-set-cover", function (e) {
    e.stopPropagation();
    var photoId = $(this).data("photo-id");
    $.post(
      URLS.photoSetCover.replace("__ID__", photoId),
      { csrfmiddlewaretoken: csrf },
      function (data) {
        if (data.success) {
          $grid.find(".photo-item").removeClass("is-cover");
          $grid.find(".photo-cover-badge").remove();
          var $item = $grid.find('[data-photo-id="' + data.photo_id + '"]');
          $item.addClass("is-cover");
          $item.prepend('<span class="photo-cover-badge">Cover</span>');
        }
      },
    );
  });

  // ── Hotel photo delete ───────────────────────────────────────────────────
  var _pendingHotelPhotoDelete = null;

  $(document).on("click", ".js-delete-photo", function (e) {
    e.stopPropagation();
    var photoId = $(this).data("photo-id");
    _pendingHotelPhotoDelete = {
      photoId: photoId,
      $item: $(this).closest(".photo-item"),
    };
    window._photoDeletePending = true;
    $("#confirm-modal-title").text("Delete Photo");
    $("#confirm-modal-body").text("Delete this photo? This cannot be undone.");
    $("#confirmModal").modal("show");
  });

  $(document).on("portal:photo-delete-confirmed", function () {
    if (_pendingHotelPhotoDelete) {
      var d = _pendingHotelPhotoDelete;
      _pendingHotelPhotoDelete = null;
      $.post(
        URLS.photoDelete.replace("__ID__", d.photoId),
        { csrfmiddlewaretoken: csrf },
        function (data) {
          if (data.success)
            d.$item.fadeOut(200, function () {
              $(this).remove();
            });
          else JD.toast("Could not delete photo.", "error");
        },
      );
    } else if (_pendingRoomPhotoDelete) {
      // Delegated to room photo handler below
      var d = _pendingRoomPhotoDelete;
      _pendingRoomPhotoDelete = null;
      var url = URLS.roomPhotoDelete
        .replace("__RID__", d.roomId)
        .replace("__ID__", d.photoId);
      $.post(url, { csrfmiddlewaretoken: csrf }, function (data) {
        if (data.success) {
          d.$item.fadeOut(200, function () {
            $(this).remove();
          });
          updateRoomPhotoBadge(d.roomId);
        } else {
          JD.toast("Could not delete photo.", "error");
        }
      });
    }
    window._photoDeletePending = false;
  });

  // ── Hotel photo reorder ──────────────────────────────────────────────────
  function initHotelSortable() {
    if (typeof $.fn.sortable === "undefined") return;
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
  initHotelSortable();

  // =========================================================================
  // ROOM TYPE PHOTO MANAGEMENT
  // =========================================================================
  var _pendingRoomPhotoDelete = null;

  // ── Toggle photo panel ───────────────────────────────────────────────────
  $(document).on("click", ".js-toggle-room-photos", function () {
    var roomId = $(this).data("room-id");
    var $panel = $("#room-photo-panel-" + roomId);
    var isVisible = $panel.is(":visible");
    // Close all other open panels first
    $(".room-photo-panel").slideUp(150);
    if (!isVisible) $panel.slideDown(200);
  });

  // ── Room photo upload ────────────────────────────────────────────────────
  $(document).on("click", ".room-photo-upload-area", function (e) {
    var roomId = $(this).data("room-id");
    var $input = $("#room-photo-input-" + roomId);
    if (!$(e.target).is($input)) $input.trigger("click");
  });

  $(document).on("click", ".room-photo-file-input", function (e) {
    e.stopPropagation();
  });

  $(document).on("dragover", ".room-photo-upload-area", function (e) {
    e.preventDefault();
    $(this).addClass("drag-over");
  });
  $(document).on("dragleave drop", ".room-photo-upload-area", function (e) {
    e.preventDefault();
    $(this).removeClass("drag-over");
    if (e.type === "drop") {
      uploadRoomFiles(
        $(this).data("room-id"),
        e.originalEvent.dataTransfer.files,
      );
    }
  });

  $(document).on("change", ".room-photo-file-input", function () {
    uploadRoomFiles($(this).data("room-id"), this.files);
    this.value = "";
  });

  function uploadRoomFiles(roomId, files) {
    if (!files || !files.length) return;
    var $spinner = $("#room-upload-spinner-" + roomId);
    $spinner.show();
    var queue = Array.from(files);

    function next() {
      if (!queue.length) {
        $spinner.hide();
        return;
      }
      var file = queue.shift();
      var fd = new FormData();
      fd.append("image", file);
      fd.append("csrfmiddlewaretoken", csrf);
      var url = URLS.roomPhotoUpload.replace("__RID__", roomId);

      $.ajax({
        url: url,
        method: "POST",
        data: fd,
        processData: false,
        contentType: false,
        success: function (data) {
          if (data.success) {
            appendRoomPhoto(roomId, data);
            updateRoomPhotoBadge(roomId);
          } else {
            JD.toast(data.error || "Upload failed", "error");
          }
          next();
        },
        error: function () {
          JD.toast("Upload failed.", "error");
          next();
        },
      });
    }
    next();
  }

  function appendRoomPhoto(roomId, data) {
    var html =
      '<div class="photo-item" data-photo-id="' +
      data.photo_id +
      '">' +
      '<img src="' +
      data.url +
      '" alt="room photo" loading="lazy">' +
      '<div class="photo-item-actions">' +
      '<button type="button" class="photo-action-btn photo-action-btn--delete js-delete-room-photo"' +
      ' data-photo-id="' +
      data.photo_id +
      '" data-room-id="' +
      roomId +
      '"' +
      ' title="Delete"><i class="bi bi-trash3"></i></button>' +
      "</div></div>";
    $("#room-photo-grid-" + roomId).append(html);
    initRoomSortable(roomId);
  }

  // ── Room photo delete ────────────────────────────────────────────────────
  $(document).on("click", ".js-delete-room-photo", function (e) {
    e.stopPropagation();
    _pendingRoomPhotoDelete = {
      photoId: $(this).data("photo-id"),
      roomId: $(this).data("room-id"),
      $item: $(this).closest(".photo-item"),
    };
    _pendingHotelPhotoDelete = null;
    window._photoDeletePending = true;
    $("#confirm-modal-title").text("Delete Room Photo");
    $("#confirm-modal-body").text(
      "Delete this room photo? This cannot be undone.",
    );
    $("#confirmModal").modal("show");
  });

  // ── Room photo reorder ───────────────────────────────────────────────────
  function initRoomSortable(roomId) {
    if (typeof $.fn.sortable === "undefined") return;
    var $grid = $("#room-photo-grid-" + roomId);
    if ($grid.data("ui-sortable")) $grid.sortable("destroy");
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
          url: URLS.roomPhotoReorder.replace("__RID__", roomId),
          method: "POST",
          contentType: "application/json",
          data: JSON.stringify({ order: order }),
          headers: { "X-CSRFToken": csrf },
        });
      },
    });
  }

  // Initialise sortable for all room grids that already have photos on page load
  $(".room-photo-grid").each(function () {
    var roomId = $(this).data("room-id");
    if ($(this).find(".photo-item").length) initRoomSortable(roomId);
  });

  // ── Update the photo count badge on the toggle button ───────────────────
  function updateRoomPhotoBadge(roomId) {
    var count = $("#room-photo-grid-" + roomId).find(".photo-item").length;
    var $btn = $('.js-toggle-room-photos[data-room-id="' + roomId + '"]');
    $btn.find(".photo-count-badge").remove();
    if (count > 0) {
      $btn.append('<span class="photo-count-badge">' + count + "</span>");
    }
  }
})(jQuery);
