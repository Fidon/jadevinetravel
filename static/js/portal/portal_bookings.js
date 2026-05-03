(function ($) {
  "use strict";

  if (!$.fn.DataTable || !$("#bookings-table").length) return;

  PORTAL.initDataTable("#bookings-table", {
    // Server-side filtering is handled by the Django form above the table.
    // DataTables client-side search is disabled to avoid confusion —
    // the search box at the top already does the job via GET params.
    searching: false,

    // Preserve server-side ordering — Django already orders by -created_at
    order: [],

    // Pagination
    pageLength: 10,
    lengthChange: true,
    lengthMenu: [
      [10, 20, 50, 100],
      ["10 per page", "20 per page", "50 per page", "100 per page"],
    ],

    // dom layout:
    // B = Buttons (Excel, PDF, Print)
    // l = length menu (rows per page selector)
    // r = processing indicator
    // t = table
    // i = info ("Showing 1-10 of 13")
    // p = pagination
    dom: '<"dt-top d-flex align-items-center justify-content-between flex-wrap gap-2"Bl>rt<"dt-bottom d-flex align-items-center justify-content-between flex-wrap gap-2"ip>',

    columnDefs: [
      // Actions column — not sortable, not exportable
      { orderable: false, targets: -1 },
      // Exclude Actions column from exports
      { targets: -1, visible: true, searchable: false },
    ],

    buttons: [
      {
        extend: "csv",
        className: "btn",
        text: '<i class="bi bi-filetype-csv me-1"></i> CSV',
        title: "Jadevine Bookings",
        exportOptions: { columns: ":not(:last-child)" },
      },
      {
        extend: "excel",
        className: "btn",
        text: '<i class="bi bi-file-earmark-excel me-1"></i> Excel',
        title: "Jadevine Bookings",
        exportOptions: { columns: ":not(:last-child)" },
      },
      {
        extend: "pdf",
        className: "btn",
        text: '<i class="bi bi-file-earmark-pdf me-1"></i> PDF',
        title: "Jadevine Bookings",
        orientation: "landscape",
        pageSize: "A4",
        exportOptions: { columns: ":not(:last-child)" },
      },
      {
        extend: "print",
        className: "btn",
        text: '<i class="bi bi-printer me-1"></i> Print',
        title: "Jadevine Bookings",
        exportOptions: { columns: ":not(:last-child)" },
      },
    ],

    language: {
      info: "Showing _START_–_END_ of _TOTAL_ bookings",
      infoEmpty: "No bookings found",
      lengthMenu: "_MENU_",
      paginate: {
        previous: '<i class="bi bi-chevron-left"></i>',
        next: '<i class="bi bi-chevron-right"></i>',
      },
    },
  });
})(jQuery);
