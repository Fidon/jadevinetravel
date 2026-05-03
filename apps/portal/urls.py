from django.urls import path
from django.http import HttpResponse
from django.views.generic import TemplateView
from apps.portal.views.auth import PortalLoginView, PortalLogoutView
from apps.portal.views.dashboard import PortalDashboardView, PendingCountAPIView
from apps.portal.mixins import PortalRequiredMixin
from apps.portal.views.hotels import (PortalHotelListView, PortalPendingHotelsView,PortalHotelDetailView,
        PortalHotelCreateView, PortalHotelEditView, PortalHotelDeleteView, PortalHotelApproveView,
        PortalHotelRejectView, PortalHotelResubmitView, PortalHotelPhotoUploadView, PortalHotelPhotoDeleteView,
        PortalHotelPhotoSetCoverView, PortalHotelPhotoReorderView, PortalHotelRoomAddView,
        PortalHotelRoomEditView, PortalHotelRoomDeleteView)
from apps.portal.views.cars import (PortalCarListView, PortalPendingCarsView, PortalCarDetailView,
        PortalCarCreateView, PortalCarEditView, PortalCarDeleteView, PortalCarApproveView,
        PortalCarRejectView, PortalCarResubmitView, PortalCarPhotoUploadView, PortalCarPhotoDeleteView,
        PortalCarPhotoSetCoverView, PortalCarPhotoReorderView)
from apps.portal.views.tours import (PortalTourListView, PortalTourDetailView, PortalTourCreateView,
        PortalTourEditView, PortalTourDeleteView, PortalTourToggleFeaturedView, PortalTourDayAddView,
        PortalTourDayEditView, PortalTourDayDeleteView, PortalTourPhotoUploadView,
        PortalTourPhotoDeleteView, PortalTourPhotoReorderView)
from apps.portal.views.bookings import (PortalBookingListView, PortalBookingDetailView,
        PortalBookingStatusView, PortalBookingMarkPaidView)

# ---------------------------------------------------------------------------
# Temporary stub view — renders a bare "coming soon" response.
# Replace each stub path as the real view is built in subsequent sessions.
# ---------------------------------------------------------------------------
class _StubView(PortalRequiredMixin, TemplateView):
    template_name = 'portal/portal_stub.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['stub_name'] = self.kwargs.get('stub_name', 'This section')
        return ctx


def _stub(name):
    """Returns a configured _StubView with a label for display."""
    return _StubView.as_view(extra_context={'stub_name': name})


app_name = 'portal'

urlpatterns = [
    # Auth
    path('login/',  PortalLoginView.as_view(),  name='login'),
    path('logout/', PortalLogoutView.as_view(), name='logout'),

    # Dashboard
    path('',    PortalDashboardView.as_view(), name='dashboard'),
    path('api/pending-count/',  PendingCountAPIView.as_view(), name='pending_count'),

    # Hotels
    path('hotels/', PortalHotelListView.as_view(), name='hotel_list'),
    path('hotels/add/', PortalHotelCreateView.as_view(), name='hotel_add'),
    path('hotels/pending/', PortalPendingHotelsView.as_view(), name='pending_hotels'),
    path('hotels/<int:pk>/', PortalHotelDetailView.as_view(), name='hotel_detail'),
    path('hotels/<int:pk>/edit/', PortalHotelEditView.as_view(), name='hotel_edit'),
    path('hotels/<int:pk>/delete/', PortalHotelDeleteView.as_view(), name='hotel_delete'),
    path('hotels/<int:pk>/approve/', PortalHotelApproveView.as_view(), name='hotel_approve'),
    path('hotels/<int:pk>/reject/', PortalHotelRejectView.as_view(), name='hotel_reject'),
    path('hotels/<int:pk>/resubmit/', PortalHotelResubmitView.as_view(), name='hotel_resubmit'),
    path('hotels/<int:hpk>/photos/upload/', PortalHotelPhotoUploadView.as_view(), name='hotel_photo_upload'),
    path('hotels/<int:hpk>/photos/<int:pk>/delete/', PortalHotelPhotoDeleteView.as_view(), name='hotel_photo_delete'),
    path('hotels/<int:hpk>/photos/<int:pk>/cover/', PortalHotelPhotoSetCoverView.as_view(), name='hotel_photo_cover'),
    path('hotels/<int:hpk>/photos/reorder/', PortalHotelPhotoReorderView.as_view(), name='hotel_photo_reorder'),
    path('hotels/<int:hpk>/rooms/add/', PortalHotelRoomAddView.as_view(), name='hotel_room_add'),
    path('hotels/<int:hpk>/rooms/<int:pk>/edit/', PortalHotelRoomEditView.as_view(), name='hotel_room_edit'),
    path('hotels/<int:hpk>/rooms/<int:pk>/delete/', PortalHotelRoomDeleteView.as_view(), name='hotel_room_delete'),

    # Cars
    path('cars/', PortalCarListView.as_view(), name='car_list'),
    path('cars/add/', PortalCarCreateView.as_view(), name='car_add'),
    path('cars/pending/', PortalPendingCarsView.as_view(), name='pending_cars'),
    path('cars/<int:pk>/', PortalCarDetailView.as_view(), name='car_detail'),
    path('cars/<int:pk>/edit/', PortalCarEditView.as_view(), name='car_edit'),
    path('cars/<int:pk>/delete/', PortalCarDeleteView.as_view(), name='car_delete'),
    path('cars/<int:pk>/approve/', PortalCarApproveView.as_view(), name='car_approve'),
    path('cars/<int:pk>/reject/', PortalCarRejectView.as_view(), name='car_reject'),
    path('cars/<int:pk>/resubmit/', PortalCarResubmitView.as_view(), name='car_resubmit'),
    path('cars/<int:cpk>/photos/upload/', PortalCarPhotoUploadView.as_view(), name='car_photo_upload'),
    path('cars/<int:cpk>/photos/<int:pk>/delete/', PortalCarPhotoDeleteView.as_view(), name='car_photo_delete'),
    path('cars/<int:cpk>/photos/<int:pk>/cover/', PortalCarPhotoSetCoverView.as_view(), name='car_photo_cover'),
    path('cars/<int:cpk>/photos/reorder/', PortalCarPhotoReorderView.as_view(), name='car_photo_reorder'),

    # Tours
    path('tours/', PortalTourListView.as_view(), name='tour_list'),
    path('tours/add/', PortalTourCreateView.as_view(), name='tour_add'),
    path('tours/<int:pk>/', PortalTourDetailView.as_view(), name='tour_detail'),
    path('tours/<int:pk>/edit/', PortalTourEditView.as_view(), name='tour_edit'),
    path('tours/<int:pk>/delete/', PortalTourDeleteView.as_view(), name='tour_delete'),
    path('tours/<int:pk>/toggle-featured/', PortalTourToggleFeaturedView.as_view(), name='tour_toggle_featured'),
    path('tours/<int:tpk>/photos/upload/', PortalTourPhotoUploadView.as_view(), name='tour_photo_upload'),
    path('tours/<int:tpk>/photos/<int:pk>/delete/', PortalTourPhotoDeleteView.as_view(), name='tour_photo_delete'),
    path('tours/<int:tpk>/photos/reorder/', PortalTourPhotoReorderView.as_view(), name='tour_photo_reorder'),
    path('tours/<int:tpk>/itinerary/add/', PortalTourDayAddView.as_view(), name='tour_day_add'),
    path('tours/<int:tpk>/itinerary/<int:pk>/edit/', PortalTourDayEditView.as_view(), name='tour_day_edit'),
    path('tours/<int:tpk>/itinerary/<int:pk>/delete/', PortalTourDayDeleteView.as_view(), name='tour_day_delete'),

    # Bookings
    path('bookings/', PortalBookingListView.as_view(), name='booking_list'),
    path('bookings/<int:pk>/', PortalBookingDetailView.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/status/', PortalBookingStatusView.as_view(), name='booking_status'),
    path('bookings/<int:pk>/mark-paid/', PortalBookingMarkPaidView.as_view(), name='booking_mark_paid'),

    # ------------------------------------------------------------------
    # Reviews (stubs — Phase 5B)
    # ------------------------------------------------------------------
    path('reviews/',     _stub('Reviews'), name='review_list'),
    path('reviews/<int:pk>/approve/',    _stub('Approve Review'),  name='review_approve'),
    path('reviews/<int:pk>/reject/',     _stub('Reject Review'),   name='review_reject'),

    # ------------------------------------------------------------------
    # Gallery (stubs — Phase 5B)
    # ------------------------------------------------------------------
    path('gallery/',     _stub('Gallery'), name='gallery'),
    path('gallery/upload/',      _stub('Gallery Upload'),  name='gallery_upload'),
    path('gallery/<int:pk>/delete/',     _stub('Gallery Delete'),  name='gallery_delete'),
    path('gallery/<int:pk>/toggle-featured/',    _stub('Toggle Featured'), name='gallery_toggle_featured'),
    path('gallery/reorder/',     _stub('Gallery Reorder'), name='gallery_reorder'),
    path('gallery/categories/add/',      _stub('Add Category'),    name='gallery_category_add'),
    path('gallery/categories/<int:pk>/edit/',    _stub('Edit Category'),   name='gallery_category_edit'),
    path('gallery/categories/<int:pk>/delete/',  _stub('Delete Category'), name='gallery_category_delete'),

    # ------------------------------------------------------------------
    # Users (stubs — Phase 5B)
    # ------------------------------------------------------------------
    path('users/',       _stub('Customers'),       name='user_list'),
    path('users/<int:pk>/',      _stub('Customer Detail'), name='user_detail'),
    path('users/<int:pk>/deactivate/',   _stub('Deactivate User'), name='user_deactivate'),
    path('users/<int:pk>/reset-password/',       _stub('Reset Password'),  name='user_reset_password'),

    # ------------------------------------------------------------------
    # Mini-Admins (stubs — Phase 5B)
    # ------------------------------------------------------------------
    path('mini-admins/', _stub('Partners'),name='miniadmin_list'),
    path('mini-admins/add/',     _stub('Add Partner'),     name='miniadmin_add'),
    path('mini-admins/<int:pk>/',_stub('Partner Detail'),  name='miniadmin_detail'),
    path('mini-admins/<int:pk>/edit/',   _stub('Edit Partner'),    name='miniadmin_edit'),
    path('mini-admins/<int:pk>/deactivate/',     _stub('Deactivate'),      name='miniadmin_deactivate'),
    path('mini-admins/<int:pk>/reset-password/', _stub('Reset Password'),  name='miniadmin_reset_password'),

    # ------------------------------------------------------------------
    # Contact messages (stubs — Phase 5B)
    # ------------------------------------------------------------------
    path('messages/',    _stub('Messages'),name='message_list'),
    path('messages/<int:pk>/',   _stub('Message Detail'),  name='message_detail'),
    path('messages/<int:pk>/reply/',     _stub('Reply'),   name='message_reply'),
    path('messages/<int:pk>/status/',    _stub('Update Status'),   name='message_status'),

    # ------------------------------------------------------------------
    # Newsletter (stubs — Phase 5B)
    # ------------------------------------------------------------------
    path('newsletter/',  _stub('Newsletter'),      name='newsletter'),
    path('newsletter/<int:pk>/toggle/',  _stub('Toggle Sub'),      name='newsletter_toggle'),

    # ------------------------------------------------------------------
    # Cancellation policies (stubs — Phase 5B)
    # ------------------------------------------------------------------
    path('policies/',    _stub('Policies'),name='policies'),
    path('policies/add/',_stub('Add Policy'),      name='policy_add'),
    path('policies/<int:pk>/edit/',      _stub('Edit Policy'),     name='policy_edit'),
    path('policies/<int:pk>/delete/',    _stub('Delete Policy'),   name='policy_delete'),

    # ------------------------------------------------------------------
    # Settings (stub — Phase 5B)
    # ------------------------------------------------------------------
    path('settings/',    _stub('Settings'),name='settings'),
]