from django.urls import path
from django.http import HttpResponse
from django.views.generic import TemplateView
from apps.portal.views.auth import PortalLoginView, PortalLogoutView, PortalPasswordSetView
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
from apps.portal.views.reviews import (PortalReviewListView, PortalReviewApproveView, PortalReviewRejectView)
from apps.portal.views.gallery import (PortalGalleryView, PortalGalleryUploadView, PortalGalleryDeleteView,
        PortalGalleryToggleFeaturedView, PortalGalleryReorderView, PortalGalleryCategoryAddView,
        PortalGalleryCategoryEditView, PortalGalleryCategoryDeleteView)
from apps.portal.views.users import (PortalUserListView, PortalUserDetailView,
        PortalUserDeactivateView, PortalUserResetPasswordView)
from apps.portal.views.miniadmins import (PortalMiniAdminListView, PortalMiniAdminCreateView,
        PortalMiniAdminDetailView, PortalMiniAdminEditView, PortalMiniAdminDeactivateView,
        PortalMiniAdminResetPasswordView)
from apps.portal.views.messages import (PortalMessageListView, PortalMessageDetailView,
        PortalMessageReplyView, PortalMessageStatusView)
from apps.portal.views.newsletter import (PortalNewsletterView, PortalNewsletterToggleView)
from apps.portal.views.policies import (PortalPoliciesView, PortalPolicyAddView,
        PortalPolicyEditView, PortalPolicyDeleteView)
from apps.portal.views.settings import PortalSettingsView



app_name = 'portal'

urlpatterns = [
    path('set-password/<uidb64>/<token>/', PortalPasswordSetView.as_view(), name='set_password'),
    
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

    # Reviews
    path('reviews/', PortalReviewListView.as_view(), name='review_list'),
    path('reviews/<int:pk>/approve/', PortalReviewApproveView.as_view(), name='review_approve'),
    path('reviews/<int:pk>/reject/', PortalReviewRejectView.as_view(), name='review_reject'),

    # Gallery
    path('gallery/', PortalGalleryView.as_view(), name='gallery'),
    path('gallery/upload/', PortalGalleryUploadView.as_view(), name='gallery_upload'),
    path('gallery/reorder/', PortalGalleryReorderView.as_view(), name='gallery_reorder'),
    path('gallery/<int:pk>/delete/', PortalGalleryDeleteView.as_view(), name='gallery_delete'),
    path('gallery/<int:pk>/toggle-featured/', PortalGalleryToggleFeaturedView.as_view(), name='gallery_toggle_featured'),
    path('gallery/categories/add/', PortalGalleryCategoryAddView.as_view(), name='gallery_category_add'),
    path('gallery/categories/<int:pk>/edit/', PortalGalleryCategoryEditView.as_view(), name='gallery_category_edit'),
    path('gallery/categories/<int:pk>/delete/', PortalGalleryCategoryDeleteView.as_view(), name='gallery_category_delete'),

    # Users
    path('users/', PortalUserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', PortalUserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/deactivate/', PortalUserDeactivateView.as_view(), name='user_deactivate'),
    path('users/<int:pk>/reset-password/', PortalUserResetPasswordView.as_view(), name='user_reset_password'),

    # Mini-Admins
    path('mini-admins/', PortalMiniAdminListView.as_view(), name='miniadmin_list'),
    path('mini-admins/add/', PortalMiniAdminCreateView.as_view(), name='miniadmin_add'),
    path('mini-admins/<int:pk>/', PortalMiniAdminDetailView.as_view(), name='miniadmin_detail'),
    path('mini-admins/<int:pk>/edit/', PortalMiniAdminEditView.as_view(), name='miniadmin_edit'),
    path('mini-admins/<int:pk>/deactivate/', PortalMiniAdminDeactivateView.as_view(), name='miniadmin_deactivate'),
    path('mini-admins/<int:pk>/reset-password/', PortalMiniAdminResetPasswordView.as_view(), name='miniadmin_reset_password'),

    # Contact messages
    path('messages/', PortalMessageListView.as_view(), name='message_list'),
    path('messages/<int:pk>/', PortalMessageDetailView.as_view(), name='message_detail'),
    path('messages/<int:pk>/reply/', PortalMessageReplyView.as_view(), name='message_reply'),
    path('messages/<int:pk>/status/', PortalMessageStatusView.as_view(), name='message_status'),

    # Newsletter
    path('newsletter/', PortalNewsletterView.as_view(), name='newsletter'),
    path('newsletter/<int:pk>/toggle/', PortalNewsletterToggleView.as_view(), name='newsletter_toggle'),

    # Cancellation policies
    path('policies/', PortalPoliciesView.as_view(), name='policies'),
    path('policies/add/', PortalPolicyAddView.as_view(), name='policy_add'),
    path('policies/<int:pk>/edit/', PortalPolicyEditView.as_view(), name='policy_edit'),
    path('policies/<int:pk>/delete/', PortalPolicyDeleteView.as_view(), name='policy_delete'),

    # Settings
    path('settings/', PortalSettingsView.as_view(), name='settings'),
]