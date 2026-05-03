(function ($) {
  "use strict";

  var csrf = window.PORTAL
    ? window.PORTAL.csrf()
    : $("[name=csrfmiddlewaretoken]").first().val();

  // =========================================================================
  // REJECTION MODAL — list + detail pages
  // =========================================================================
  $(document).on("click", '[data-bs-target="#rejectCarModal"]', function () {
    var $btn = $(this);
    var carPk = $btn.data("car-pk");
    var carName = $btn.data("car-name");
    var nextVal = $btn.data("next") || "";

    $("#rejectCarModal #reject-car-name").text(carName);
    $("#rejectCarModal #reject-car-next").val(nextVal);
    $("#reject-car-form").attr("action", "/portal/cars/" + carPk + "/reject/");
    $("#id_car_rejection_reason").val("");
    $("#reject-car-submit").prop("disabled", true);
  });

  $(document).on("input", "#id_car_rejection_reason", function () {
    $("#reject-car-submit").prop("disabled", $(this).val().trim().length < 10);
  });

  // =========================================================================
  // LANGUAGE TABS — form page
  // =========================================================================
  $(document).on("click", ".lang-tab", function () {
    var target = $(this).data("target");
    $(".lang-tab").removeClass("active");
    $(this).addClass("active");
    $("#car-desc-fr, #car-desc-ru").hide();
    $(target).show();
  });

  // =========================================================================
  // PHOTO MANAGEMENT — car detail page only
  // =========================================================================
  if (!window.CAR_URLS) return;

  var URLS = window.CAR_URLS;
  var $grid = $("#photo-grid");
  var $area = $("#photo-upload-area");
  var $input = $("#photo-file-input");
  var $spinner = $("#upload-spinner");

  // Upload area click
  $area.on("click", function (e) {
    if (!$(e.target).is($input)) {
      $input.trigger("click");
    }
  });
  $input.on("click", function (e) {
    e.stopPropagation();
  });

  // Drag & drop
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
      '"><i class="bi bi-star-fill"></i></button>' +
      '<button type="button" class="photo-action-btn photo-action-btn--delete js-delete-photo" data-photo-id="' +
      data.photo_id +
      '"><i class="bi bi-trash3"></i></button>' +
      "</div>" +
      "</div>";
    $grid.append(html);
    initSortable();
  }

  // Set cover
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

  // Delete photo — uses shared confirm modal
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

  // Sortable
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
