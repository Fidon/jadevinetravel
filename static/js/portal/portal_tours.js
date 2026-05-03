(function ($) {
  "use strict";

  var csrf = window.PORTAL
    ? window.PORTAL.csrf()
    : $("[name=csrfmiddlewaretoken]").first().val();

  // =========================================================================
  // LANGUAGE TABS — form page
  // Each tab group is independent; target IDs distinguish them
  // =========================================================================
  $(document).on("click", ".lang-tab", function () {
    var $btn = $(this);
    var target = $btn.data("target");
    var $siblings = $btn.closest("ul").find(".lang-tab");
    $siblings.removeClass("active");
    $btn.addClass("active");

    // Hide all panels that share the same tab group
    // Determine siblings by closest tab group container
    var $panel = $(target);
    $panel.siblings('[id^="tour-name-"], [id^="desc-lang-"]').hide();
    $panel.show();
  });

  // =========================================================================
  // EDIT ITINERARY DAY MODAL — populate from window.ITINERARY_DAYS JSON
  // =========================================================================
  $(document).on("click", ".js-edit-day-btn", function () {
    var dayId = parseInt($(this).data("day-id"));
    var days = window.ITINERARY_DAYS || [];
    var day = null;
    for (var i = 0; i < days.length; i++) {
      if (days[i].id === dayId) {
        day = days[i];
        break;
      }
    }
    if (!day) return;

    var $modal = $("#editDayModal");
    $modal.find('[name="day_number"]').val(day.day_number);
    $modal.find('[name="title_en"]').val(day.title_en);
    $modal.find('[name="title_fr"]').val(day.title_fr);
    $modal.find('[name="title_ru"]').val(day.title_ru);
    $modal.find('[name="description_en"]').val(day.description_en);
    $modal.find('[name="description_fr"]').val(day.description_fr);
    $modal.find('[name="description_ru"]').val(day.description_ru);
    $("#edit-day-form").attr("action", day.edit_url);
  });

  // =========================================================================
  // PHOTO MANAGEMENT — tour detail page only
  // No set-cover button (cover is the TourPackage.cover_image field, set on edit page)
  // =========================================================================
  if (!window.TOUR_URLS) return;

  var URLS = window.TOUR_URLS;
  var $grid = $("#photo-grid");
  var $area = $("#photo-upload-area");
  var $input = $("#photo-file-input");
  var $spinner = $("#upload-spinner");

  $area.on("click", function (e) {
    if (!$(e.target).is($input)) {
      $input.trigger("click");
    }
  });
  $input.on("click", function (e) {
    e.stopPropagation();
  });

  $area.on("dragover", function (e) {
    e.preventDefault();
    $area.addClass("drag-over");
  });
  $area.on("dragleave drop", function (e) {
    e.preventDefault();
    $area.removeClass("drag-over");
    if (e.type === "drop") {
      uploadFiles(e.originalEvent.dataTransfer.files);
    }
  });

  $input.on("change", function () {
    uploadFiles(this.files);
    this.value = "";
  });

  function uploadFiles(files) {
    if (!files || files.length === 0) return;
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
          if (data.success) {
            appendPhoto(data);
          } else {
            JD.toast(data.error || "Upload failed", "error");
          }
          next();
        },
        error: function () {
          JD.toast("Upload failed. Please try again.", "error");
          next();
        },
      });
    }
    next();
  }

  function appendPhoto(data) {
    var html =
      '<div class="photo-item" data-photo-id="' +
      data.photo_id +
      '">' +
      '<img src="' +
      data.url +
      '" alt="photo" loading="lazy">' +
      '<div class="photo-item-actions">' +
      '<button type="button" class="photo-action-btn photo-action-btn--delete js-delete-photo" data-photo-id="' +
      data.photo_id +
      '"><i class="bi bi-trash3"></i></button>' +
      "</div>" +
      "</div>";
    $grid.append(html);
    initSortable();
  }

  // Delete — shared confirm modal
  var _pendingPhotoDelete = null;

  $(document).on("click", ".js-delete-photo", function (e) {
    e.stopPropagation();
    _pendingPhotoDelete = {
      photoId: $(this).data("photo-id"),
      $item: $(this).closest(".photo-item"),
    };
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

    $.post(
      URLS.photoDelete.replace("__ID__", photoId),
      { csrfmiddlewaretoken: csrf },
      function (data) {
        if (data.success) {
          $item.fadeOut(200, function () {
            $(this).remove();
          });
        } else {
          JD.toast("Could not delete photo.", "error");
        }
      },
    );
  });

  function initSortable() {
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

  initSortable();
})(jQuery);
