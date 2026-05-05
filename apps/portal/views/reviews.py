import json
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.reviews.models import Review
from apps.portal.mixins import (
    PortalRequiredMixin,
    SuperAdminRequiredMixin,
    get_accessible_reviews,
    is_mini_admin,
)


class PortalReviewListView(PortalRequiredMixin, View):
    template_name = 'portal/portal_reviews_list.html'

    def get(self, request):
        qs = get_accessible_reviews(request.user).select_related(
            'user', 'hotel', 'tour_package', 'car', 'booking', 'moderated_by'
        )

        status_filter = request.GET.get('status', '').strip()
        service_filter = request.GET.get('service_type', '').strip()

        if status_filter:
            qs = qs.filter(status=status_filter)
        if service_filter:
            qs = qs.filter(service_type=service_filter)

        # Mini-admins cannot see tour reviews — enforced here as a hard
        # filter on top of get_accessible_reviews() which already scopes
        # by hotel/car ownership. Tour reviews have hotel=None, car=None
        # so they are already excluded by the helper, but be explicit.
        if is_mini_admin(request.user):
            qs = qs.exclude(service_type='tour')

        pending_count = get_accessible_reviews(request.user).filter(
            status='pending'
        ).count()

        context = {
            'reviews': qs.order_by('-created_at'),
            'status_filter': status_filter,
            'service_filter': service_filter,
            'pending_count': pending_count,
            'mini_admin': is_mini_admin(request.user),
            'status_choices': Review.STATUS_CHOICES,
            'service_choices': Review.SERVICE_TYPE_CHOICES,
        }
        return render(request, self.template_name, context)


class PortalReviewApproveView(PortalRequiredMixin, View):
    """POST only. Accessible to both roles — scoped via get_accessible_reviews."""

    def post(self, request, pk):
        qs = get_accessible_reviews(request.user)
        review = get_object_or_404(qs, pk=pk)

        # Mini-admin cannot moderate tour reviews — belt-and-suspenders check
        if is_mini_admin(request.user) and review.service_type == 'tour':
            return JsonResponse(
                {'success': False, 'error': 'Not permitted.'},
                status=403
            )

        if review.status == 'approved':
            return JsonResponse({'success': True, 'already': True})

        review.status = 'approved'
        review.moderated_by = request.user
        review.moderated_at = timezone.now()
        review.rejection_reason = ''
        review.save(update_fields=[
            'status', 'moderated_by', 'moderated_at', 'rejection_reason'
        ])

        return JsonResponse({'success': True})


class PortalReviewRejectView(PortalRequiredMixin, View):
    """POST only. Requires rejection_reason in POST body."""

    def post(self, request, pk):
        qs = get_accessible_reviews(request.user)
        review = get_object_or_404(qs, pk=pk)

        if is_mini_admin(request.user) and review.service_type == 'tour':
            return JsonResponse(
                {'success': False, 'error': 'Not permitted.'},
                status=403
            )

        reason = request.POST.get('rejection_reason', '').strip()
        if len(reason) < 10:
            return JsonResponse(
                {'success': False,
                 'error': 'Please provide a reason (at least 10 characters).'},
                status=400
            )

        review.status = 'rejected'
        review.moderated_by = request.user
        review.moderated_at = timezone.now()
        review.rejection_reason = reason
        review.save(update_fields=[
            'status', 'moderated_by', 'moderated_at', 'rejection_reason'
        ])

        return JsonResponse({'success': True})