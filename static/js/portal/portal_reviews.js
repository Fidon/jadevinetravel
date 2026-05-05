(function ($) {
  "use strict";

  var STRINGS = window.JD_STRINGS || {};
  var csrf = window.PORTAL.csrfToken;

  // ── Toast helper (delegates to portal_base.js flash mechanism) ────────────
  function showFlash(msg, type) {
    // Reuse the portal alert pattern by prepending a dismissible alert
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

  // ── Remove row or update badge after moderation ───────────────────────────
  function updateRowStatus($row, newStatus) {
    var pk = $row.data("review-id");
    $row.attr("data-status", newStatus);

    // Update status badge
    var badgeClass =
      newStatus === "approved"
        ? "approval-badge--approved"
        : "approval-badge--rejected";
    var icon =
      newStatus === "approved"
        ? '<i class="bi bi-check-circle-fill"></i>'
        : '<i class="bi bi-x-circle-fill"></i>';
    var label = newStatus === "approved" ? "Approved" : "Rejected";
    $row
      .find(".approval-badge")
      .attr("class", "approval-badge " + badgeClass)
      .html(icon + " " + label);

    // Remove the button that was just used
    if (newStatus === "approved") {
      $row.find(".review-approve-btn").remove();
    } else {
      $row.find(".review-reject-btn").remove();
    }

    // Update pending count badge in sidebar
    var current =
      parseInt($(".portal-nav-badge--accent").first().text(), 10) || 0;
    if (current > 0) {
      var updated = current - 1;
      $(".portal-nav-badge--accent").text(updated);
      if (updated === 0) {
        $(".portal-nav-badge--accent").hide();
      }
    }
  }

  // ── APPROVE ───────────────────────────────────────────────────────────────
  $(document).on("click", ".review-approve-btn", function () {
    var $btn = $(this);
    var $row = $btn.closest("tr");
    var url = $btn.data("approve-url");

    $btn.prop("disabled", true).html('<i class="bi bi-hourglass-split"></i>');

    $.ajax({
      url: url,
      method: "POST",
      headers: { "X-CSRFToken": csrf },
      success: function (data) {
        if (data.success) {
          updateRowStatus($row, "approved");
          showFlash(STRINGS.approveSuccess || "Review approved.", "success");
        } else {
          $btn.prop("disabled", false).html('<i class="bi bi-check-lg"></i>');
          showFlash(STRINGS.approveError || "Could not approve.", "error");
        }
      },
      error: function () {
        $btn.prop("disabled", false).html('<i class="bi bi-check-lg"></i>');
        showFlash(STRINGS.approveError || "Could not approve.", "error");
      },
    });
  });

  // ── REJECT — open modal ───────────────────────────────────────────────────
  $(document).on("click", ".review-reject-btn", function () {
    var $btn = $(this);
    var pk = $btn.data("review-id");
    var url = "/portal/reviews/" + pk + "/reject/";

    $("#rejectReviewForm").attr("action", url);
    $("#rejectionReasonInput").val("");
    $("#rejectReviewSubmit").prop("disabled", true);
    // Store reference to row for post-submit DOM update
    $("#rejectReviewModal").data("target-row", $btn.closest("tr"));
    $("#rejectReviewModal").modal("show");
  });

  // Enable submit button only when reason has >= 10 chars
  $("#rejectionReasonInput").on("input", function () {
    $("#rejectReviewSubmit").prop("disabled", $(this).val().trim().length < 10);
  });

  // Intercept form submit — use AJAX so the modal can close on success
  $("#rejectReviewForm").on("submit", function (e) {
    e.preventDefault();
    var $form = $(this);
    var url = $form.attr("action");
    var reason = $("#rejectionReasonInput").val().trim();
    var $submit = $("#rejectReviewSubmit");
    var $row = $("#rejectReviewModal").data("target-row");

    $submit.prop("disabled", true).text("Rejecting…");

    $.ajax({
      url: url,
      method: "POST",
      data: { rejection_reason: reason },
      headers: { "X-CSRFToken": csrf },
      success: function (data) {
        if (data.success) {
          $("#rejectReviewModal").modal("hide");
          updateRowStatus($row, "rejected");
          showFlash(STRINGS.rejectSuccess || "Review rejected.", "success");
        } else {
          showFlash(
            data.error || STRINGS.rejectError || "Could not reject.",
            "error",
          );
          $submit.prop("disabled", false).text("Reject Review");
        }
      },
      error: function () {
        showFlash(STRINGS.rejectError || "Could not reject.", "error");
        $submit.prop("disabled", false).text("Reject Review");
      },
    });
  });

  // ── DETAIL MODAL — view full comment and rejection reason ─────────────────
  $(document).on("click", ".review-expand-btn", function () {
    var comment = $(this).data("comment") || "";
    var rejection = $(this).data("rejection") || "";
    var status = $(this).data("status");

    var html = "";

    if (comment) {
      html +=
        '<div class="review-detail-section">' +
        '<div class="review-detail-label">' +
        (STRINGS.comment || "Comment") +
        "</div>" +
        '<div class="review-detail-text">' +
        $("<div>").text(comment).html() +
        "</div></div>";
    } else {
      html +=
        '<div class="review-detail-section">' +
        '<div class="review-detail-label">' +
        (STRINGS.comment || "Comment") +
        "</div>" +
        '<p style="color:var(--color-muted);font-style:italic;' +
        'font-size:var(--text-sm);">' +
        (STRINGS.noComment || "No comment provided.") +
        "</p></div>";
    }

    if (status === "rejected" && rejection) {
      html +=
        '<div class="review-detail-section">' +
        '<div class="review-detail-label">' +
        (STRINGS.rejectionReason || "Rejection Reason") +
        "</div>" +
        '<div class="review-detail-rejection">' +
        $("<div>").text(rejection).html() +
        "</div></div>";
    }

    $("#reviewDetailBody").html(html);
    $("#reviewDetailModal").modal("show");
  });

  // ── DataTables init ───────────────────────────────────────────────────────
  if ($.fn.DataTable && $("#reviews-table").length) {
    PORTAL.initDataTable("#reviews-table", {
      pageLength: 20,
      order: [[5, "desc"]], // Submitted date descending
      columnDefs: [
        { orderable: false, targets: [3, 4, 7] }, // rating, comment, actions
      ],
      exportOptions: { columns: ":not(:last-child)" },
    });
  }
})(jQuery);
