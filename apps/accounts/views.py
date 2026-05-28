import json
from io import BytesIO
from datetime import date

from allauth.account.views import LoginView as AllauthLoginView
from allauth.account import app_settings as allauth_settings
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.account.internal.flows.email_verification import send_verification_email_to_address
from allauth.account.models import EmailAddress

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from apps.bookings.models import Booking, CancellationPolicy
from apps.hotels.models import Hotel
from apps.tours.models import TourPackage
from apps.cars.models import CarRental
from apps.core.models import SavedFavourite
from apps.contact.models import NewsletterSubscriber
from apps.accounts.forms import ProfileUpdateForm, CancellationForm, NATIONALITY_CHOICES

from apps.reviews.forms import ReviewForm

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_refund_info(booking):
    """
    Given a booking, compute days until service and the applicable
    CancellationPolicy tier. Returns a dict with refund_percentage and label.
    Returns None if no policy is found.
    """
    service_date = booking.service_date
    if not service_date:
        return None

    days_remaining = (service_date - date.today()).days

    # Find highest matching threshold: e.g. days_remaining=10 matches tiers
    # 7 (10>=7) and 0 (10>=0). We want the most favourable to the customer
    # which is the highest threshold they meet.
    policies = CancellationPolicy.objects.filter(
        service_type=booking.service_type,
        is_active=True,
        days_before_service__lte=days_remaining,
    ).order_by('-days_before_service')

    if not policies.exists():
        # days_remaining is negative (past service date) or no policy — no refund
        return {
            'days_remaining': days_remaining,
            'refund_percentage': 0,
            'refund_amount': 0,
            'label': str(_('No refund — service date has passed or no policy applies.')),
        }

    policy = policies.first()
    refund_amount = (booking.total_price * policy.refund_percentage) / 100

    return {
        'days_remaining': days_remaining,
        'refund_percentage': policy.refund_percentage,
        'refund_amount': refund_amount,
        'label': policy.label_en,
    }


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        today = date.today()

        upcoming = Booking.objects.filter(
            user=user,
        ).exclude(
            status__in=['cancelled', 'completed', 'no_show', 'cancellation_requested']
        ).filter(
            # service_date is a property, not a DB field — we must filter on all
            # possible date fields and take non-null ones
            **{}  # can't filter on property; use Q objects below
        )

        # Filter upcoming bookings across all three date field possibilities
        from django.db.models import Q
        upcoming = Booking.objects.filter(user=user).exclude(
            status__in=['cancelled', 'completed', 'no_show']
        ).filter(
            Q(check_in_date__gte=today) |
            Q(preferred_date__gte=today) |
            Q(pickup_date__gte=today)
        ).select_related('hotel', 'tour_package', 'car').order_by(
            'check_in_date', 'preferred_date', 'pickup_date'
        )[:3]

        ctx['upcoming_bookings'] = upcoming
        ctx['user'] = user
        return ctx


# ---------------------------------------------------------------------------
# Booking History
# ---------------------------------------------------------------------------

class BookingHistoryView(LoginRequiredMixin, View):
    template_name = 'accounts/booking_history.html'
    login_url = '/accounts/login/'
    ITEMS_PER_PAGE = 10

    def get(self, request):
        status_filter = request.GET.get('status', '')
        qs = Booking.objects.filter(user=request.user).select_related(
            'hotel', 'tour_package', 'car'
        ).order_by('-created_at')

        if status_filter:
            qs = qs.filter(status=status_filter)

        paginator = Paginator(qs, self.ITEMS_PER_PAGE)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        status_choices = Booking.STATUS_CHOICES

        return render(request, self.template_name, {
            'page_obj': page_obj,
            'status_filter': status_filter,
            'status_choices': status_choices,
        })


# ---------------------------------------------------------------------------
# Booking Detail
# ---------------------------------------------------------------------------

class BookingDetailView(LoginRequiredMixin, View):
    template_name = 'accounts/booking_detail.html'
    login_url = '/accounts/login/'

    def get(self, request, reference):
        booking = get_object_or_404(
            Booking.objects.select_related('hotel', 'tour_package', 'car', 'room_type'),
            reference=reference,
            user=request.user,  # Ownership enforced here — users can only see own bookings
        )
        refund_info = _get_refund_info(booking)

        # Can this booking be cancelled by the customer?
        cancellable = (
            booking.status in ('pending_confirmation', 'confirmed') and
            booking.service_date and
            booking.service_date > date.today()
        )
        
        # Review state — determines which UI block to render
        existing_review = getattr(booking, 'review', None)
        can_review = (
            booking.status == 'completed' and
            existing_review is None
        )

        return render(request, self.template_name, {
            'booking': booking,
            'refund_info': refund_info,
            'cancellable': cancellable,
            'existing_review': existing_review,
            'can_review': can_review,
        })


# ---------------------------------------------------------------------------
# Cancel Booking
# ---------------------------------------------------------------------------

class CancelBookingView(LoginRequiredMixin, View):
    template_name = 'accounts/booking_detail.html'
    login_url = '/accounts/login/'

    def get(self, request, reference):
        """
        Show cancellation confirmation modal data.
        The cancel button is on booking_detail.html — this view handles the POST.
        For a GET to this URL, redirect back to booking detail.
        """
        return redirect('accounts:booking_detail', reference=reference)

    def post(self, request, reference):
        booking = get_object_or_404(
            Booking,
            reference=reference,
            user=request.user,
        )

        # Guard: only cancellable statuses
        if booking.status not in ('pending_confirmation', 'confirmed'):
            messages.error(request, _('This booking cannot be cancelled.'))
            return redirect('accounts:booking_detail', reference=reference)

        # Guard: cannot cancel past bookings
        if not booking.service_date or booking.service_date <= date.today():
            messages.error(request, _('This booking cannot be cancelled — the service date has passed.'))
            return redirect('accounts:booking_detail', reference=reference)

        form = CancellationForm(request.POST)
        if not form.is_valid():
            messages.error(request, _('Please confirm the cancellation.'))
            return redirect('accounts:booking_detail', reference=reference)

        refund_info = _get_refund_info(booking)
        reason = form.cleaned_data.get('cancellation_reason', '')

        if booking.payment_mode == 'pay_now' and refund_info and refund_info['refund_percentage'] > 0:
            # PAY_NOW with refund due → cancellation_requested, admin confirms after refund
            booking.status = 'cancellation_requested'
            booking.cancellation_reason = reason
            booking.cancelled_by = request.user
            booking.cancelled_at = timezone.now()
            booking.save(update_fields=[
                'status', 'cancellation_reason', 'cancelled_by', 'cancelled_at', 'updated_at'
            ])
            _queue_cancellation_requested_emails(booking, refund_info)
            messages.success(
                request,
                _('Your cancellation request has been submitted. '
                  'We will process your refund and confirm within 2–3 business days.')
            )
        else:
            # PAY_ON_ARRIVAL, or PAY_NOW with 0% refund → immediate cancellation
            booking.status = 'cancelled'
            booking.cancellation_reason = reason
            booking.cancelled_by = request.user
            booking.cancelled_at = timezone.now()
            booking.save(update_fields=[
                'status', 'cancellation_reason', 'cancelled_by', 'cancelled_at', 'updated_at'
            ])
            _queue_cancellation_confirmed_emails(booking, refund_info)
            messages.success(request, _('Your booking has been cancelled.'))

        return redirect('accounts:booking_history')


def _queue_cancellation_requested_emails(booking, refund_info):
    """Queue emails for PAY_NOW cancellation that requires admin refund action."""
    from django_q.tasks import async_task
    async_task(
        'apps.accounts.tasks.send_cancellation_requested_customer_email',
        booking.id,
        refund_info,
    )
    async_task(
        'apps.accounts.tasks.send_cancellation_requested_admin_email',
        booking.id,
        refund_info,
    )


def _queue_cancellation_confirmed_emails(booking, refund_info):
    """Queue emails for immediate cancellations (pay on arrival or 0% refund)."""
    from django_q.tasks import async_task
    async_task(
        'apps.accounts.tasks.send_cancellation_confirmed_customer_email',
        booking.id,
        refund_info,
    )
    async_task(
        'apps.accounts.tasks.send_cancellation_confirmed_admin_email',
        booking.id,
        refund_info,
    )


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------
class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'
    login_url = '/accounts/login/'
    
    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        subscriber = NewsletterSubscriber.objects.filter(
            email__iexact=request.user.email
        ).first()
        return render(request, self.template_name, {
            'form': form,
            'nationality_choices': NATIONALITY_CHOICES,
            'newsletter_subscribed': subscriber.is_active if subscriber else False,
        })
        
    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated.'))
            return redirect('accounts:profile')
        subscriber = NewsletterSubscriber.objects.filter(
            email__iexact=request.user.email
        ).first()
        return render(request, self.template_name, {
            'form': form,
            'nationality_choices': NATIONALITY_CHOICES,
            'newsletter_subscribed': subscriber.is_active if subscriber else False,
        })


# ---------------------------------------------------------------------------
# Newsletter Subscription Toggle
# ---------------------------------------------------------------------------
class NewsletterToggleView(LoginRequiredMixin, View):
    """
    AJAX-only POST. Toggles the newsletter subscription state for the
    currently logged-in customer based on their email address.
    Response: { "subscribed": true|false }
    """
    login_url = '/accounts/login/'

    def post(self, request):
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX only'}, status=400)

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email__iexact=request.user.email,
            defaults={'email': request.user.email, 'is_active': False},
        )

        if created:
            subscriber.is_active = True
            subscriber.save(update_fields=['is_active'])
        else:
            subscriber.is_active = not subscriber.is_active
            subscriber.save(update_fields=['is_active'])

        return JsonResponse({'subscribed': subscriber.is_active})


# ---------------------------------------------------------------------------
# Favourites
# ---------------------------------------------------------------------------
class FavouritesView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/favourites.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['favourites'] = SavedFavourite.objects.filter(
            user=self.request.user
        ).select_related('hotel', 'tour_package', 'car').order_by('-saved_at')
        return ctx


class ToggleFavouriteView(LoginRequiredMixin, View):
    """
    AJAX-only POST endpoint.
    Request body (JSON): { "item_type": "hotel"|"tour"|"car", "item_id": <int> }
    Response: { "saved": true|false }
    """
    login_url = '/accounts/login/'

    def post(self, request):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX only'}, status=400)

        try:
            data = json.loads(request.body)
            item_type = data.get('item_type')
            item_id = int(data.get('item_id'))
        except (ValueError, TypeError, KeyError):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        if item_type not in ('hotel', 'tour', 'car'):
            return JsonResponse({'error': 'Invalid item_type'}, status=400)

        # Resolve the FK field name and model
        fk_map = {
            'hotel': ('hotel', Hotel),
            'tour': ('tour_package', TourPackage),
            'car': ('car', CarRental),
        }
        fk_field, Model = fk_map[item_type]

        item = get_object_or_404(Model, pk=item_id)

        lookup = {'user': request.user, fk_field: item}
        # Null out the other two FKs to satisfy UniqueConstraints
        null_fields = {k: None for k in ('hotel', 'tour_package', 'car') if k != fk_field}

        existing = SavedFavourite.objects.filter(**lookup).first()
        if existing:
            existing.delete()
            return JsonResponse({'saved': False})
        else:
            SavedFavourite.objects.create(**lookup, **null_fields)
            return JsonResponse({'saved': True})


# ---------------------------------------------------------------------------
# PDF Booking Confirmation
# ---------------------------------------------------------------------------

class BookingPDFView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'

    def get(self, request, reference):
        booking = get_object_or_404(
            Booking.objects.select_related('hotel', 'tour_package', 'car', 'room_type'),
            reference=reference,
            user=request.user,
        )

        buffer = BytesIO()
        page_w, page_h = A4
        margin = 20 * mm
        usable_w = page_w - 2 * margin

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=margin,
            leftMargin=margin,
            topMargin=10 * mm,
            bottomMargin=margin,
        )

        # --- Colours ---
        PRIMARY    = colors.HexColor('#1a4d2e')
        ACCENT     = colors.HexColor('#c89666')
        OFF_WHITE  = colors.HexColor('#f8f5f0')
        LIGHT      = colors.HexColor('#f0ebe3')
        BORDER     = colors.HexColor('#e0d5c8')
        TEXT       = colors.HexColor('#1e1e1e')
        MUTED      = colors.HexColor('#9e8e7e')
        WHITE      = colors.HexColor('#ffffff')
        SUCCESS    = colors.HexColor('#2d7a4f')
        DANGER     = colors.HexColor('#b03a2e')

        # --- Styles ---
        header_brand_style = ParagraphStyle(
            'HeaderBrand',
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=WHITE,
            leading=28,
        )
        header_tagline_style = ParagraphStyle(
            'HeaderTagline',
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#c89666'),
            leading=14,
            letterSpacing=2,
        )
        header_label_style = ParagraphStyle(
            'HeaderLabel',
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#a8c8b4'),
            leading=12,
            alignment=2,
        )
        header_doc_style = ParagraphStyle(
            'HeaderDoc',
            fontName='Helvetica-Bold',
            fontSize=13,
            textColor=WHITE,
            leading=18,
            alignment=2,
        )
        ref_style = ParagraphStyle(
            'Ref',
            fontName='Helvetica-Bold',
            fontSize=15,
            textColor=PRIMARY,
        )
        status_style = ParagraphStyle(
            'Status',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=ACCENT,
            alignment=2,
        )
        section_title_style = ParagraphStyle(
            'SectionTitle',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=PRIMARY,
            spaceBefore=14,
            spaceAfter=6,
        )
        label_style = ParagraphStyle(
            'Label',
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=MUTED,
            leading=10,
        )
        value_style = ParagraphStyle(
            'Value',
            fontName='Helvetica',
            fontSize=10,
            textColor=TEXT,
            leading=14,
            spaceAfter=4,
        )
        total_style = ParagraphStyle(
            'Total',
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=PRIMARY,
            leading=16,
        )
        footer_style = ParagraphStyle(
            'Footer',
            fontName='Helvetica',
            fontSize=8,
            textColor=MUTED,
            alignment=1,  # center
            leading=12,
        )

        story = []

        # ── HEADER ────────────────────────────────────────────────────
        header_table = Table(
            [[
                Paragraph('Jadevine Travel &amp; Tours', header_brand_style),
                Paragraph('BOOKING CONFIRMATION', header_label_style),
            ],
            [
                Paragraph('ZANZIBAR  ·  TANZANIA', header_tagline_style),
                Paragraph('Official Document', header_doc_style),
            ]],
            colWidths=[usable_w * 0.55, usable_w * 0.45],
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
            ('LEFTPADDING', (0, 0), (0, -1), 28),
            ('RIGHTPADDING', (-1, 0), (-1, -1), 28),
            ('LEFTPADDING', (-1, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 26),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 26),
            ('TOPPADDING', (0, 1), (-1, 1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('LINEBELOW', (0, -1), (-1, -1), 3, ACCENT),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10 * mm))

        # ── REFERENCE + STATUS ROW ────────────────────────────────────
        status_display = dict(Booking.STATUS_CHOICES).get(booking.status, booking.status)
        status_colour = SUCCESS if booking.status == 'confirmed' else (
            DANGER if booking.status == 'cancelled' else ACCENT
        )
        dynamic_status_style = ParagraphStyle(
            'DynStatus',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=status_colour,
            alignment=2,
        )
        ref_row = Table(
            [[
                Paragraph(f'Reference: {booking.reference}', ref_style),
                Paragraph(f'Status: {status_display}', dynamic_status_style),
            ]],
            colWidths=[usable_w * 0.55, usable_w * 0.45],
        )
        ref_row.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, BORDER),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(ref_row)
        story.append(Spacer(1, 5 * mm))

        def detail_row(label, value):
            return [Paragraph(label, label_style), Paragraph(str(value), value_style)]

        def build_detail_table(rows):
            t = Table(rows, colWidths=[usable_w * 0.3, usable_w * 0.7])
            t.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [OFF_WHITE, WHITE]),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            return t

        # ── GUEST INFORMATION ─────────────────────────────────────────
        story.append(Paragraph('Guest Information', section_title_style))
        guest_rows = [
            detail_row('Name', booking.user.get_full_name() or booking.user.email),
            detail_row('Email', booking.user.email),
        ]
        if booking.user.phone:
            guest_rows.append(detail_row('Phone', booking.user.phone))
        story.append(build_detail_table(guest_rows))

        # ── BOOKING DETAILS ───────────────────────────────────────────
        story.append(Paragraph('Booking Details', section_title_style))
        details = [detail_row('Service Type', booking.get_service_type_display())]

        if booking.service_type == 'hotel' and booking.hotel:
            details.append(detail_row('Hotel', booking.hotel.name))
            if booking.room_type:
                details.append(detail_row('Room Type', booking.room_type.name))
            if booking.check_in_date:
                details.append(detail_row('Check-in', booking.check_in_date.strftime('%d %B %Y')))
            if booking.check_out_date:
                details.append(detail_row('Check-out', booking.check_out_date.strftime('%d %B %Y')))
            if booking.nights:
                details.append(detail_row('Nights', str(booking.nights)))
            if booking.num_guests:
                details.append(detail_row('Guests', str(booking.num_guests)))

        elif booking.service_type == 'tour' and booking.tour_package:
            details.append(detail_row('Package', booking.tour_package.name_en))
            if booking.preferred_date:
                details.append(detail_row('Preferred Date', booking.preferred_date.strftime('%d %B %Y')))
            if booking.num_participants:
                details.append(detail_row('Participants', str(booking.num_participants)))

        elif booking.service_type == 'car' and booking.car:
            details.append(detail_row('Vehicle', booking.car.name))
            if booking.rental_mode:
                details.append(detail_row('Rental Mode', booking.get_rental_mode_display()))
            if booking.pickup_location:
                details.append(detail_row('Pickup Location', booking.pickup_location))
            if booking.pickup_date:
                details.append(detail_row('Pickup Date', booking.pickup_date.strftime('%d %B %Y')))
            if booking.return_date:
                details.append(detail_row('Return Date', booking.return_date.strftime('%d %B %Y')))
            if booking.num_days:
                details.append(detail_row('Days', str(booking.num_days)))

        if booking.special_requests:
            details.append(detail_row('Special Requests', booking.special_requests))

        story.append(build_detail_table(details))

        # ── PAYMENT SUMMARY ───────────────────────────────────────────
        story.append(Paragraph('Payment Summary', section_title_style))
        payment_rows = [
            detail_row('Base Price', f'{booking.currency} {booking.base_price:.2f}'),
            [Paragraph('Total', label_style),
            Paragraph(f'{booking.currency} {booking.total_price:.2f}', total_style)],
            detail_row('Payment Mode', booking.get_payment_mode_display()),
            detail_row('Payment Status', booking.get_payment_status_display()),
        ]
        payment_table = Table(
            payment_rows,
            colWidths=[usable_w * 0.3, usable_w * 0.7],
        )
        payment_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [OFF_WHITE, WHITE]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, 1), (-1, 1), 1, ACCENT),  # gold line above total
        ]))
        story.append(payment_table)

        # ── DIVIDER ───────────────────────────────────────────────────
        story.append(Spacer(1, 8 * mm))
        story.append(HRFlowable(
            width='100%', thickness=0.5, color=BORDER, spaceAfter=6
        ))

        # ── FOOTER ────────────────────────────────────────────────────
        # Gold accent line above footer text
        story.append(HRFlowable(
            width=60 * mm, thickness=2, color=ACCENT,
            hAlign='CENTER', spaceAfter=6
        ))
        story.append(Paragraph(
            'Jadevine Travel & Tours  |  Zanzibar, Tanzania  |  '
            'info@jadevinetours.com  |  +255 713 529 019',
            footer_style,
        ))
        story.append(Paragraph(
            f'Generated on {date.today().strftime("%d %B %Y")}  ·  '
            'This document serves as your official booking confirmation.',
            footer_style,
        ))

        doc.build(story)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="jadevine-booking-{booking.reference}.pdf"'
        )
        return response

class JadevineLoginView(AllauthLoginView):
    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['unverified_email'] = False

        # Check if the submitted email belongs to an existing unverified account
        email = self.request.POST.get('login', '').strip().lower()
        if email:
            try:
                user = User.objects.get(email__iexact=email)
                if not user.is_active:
                    ctx['unverified_email'] = True
            except User.DoesNotExist:
                pass
        return ctx
    
    
class ResendVerificationView(View):
    template_name = 'account/resend_verification.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return render(request, self.template_name, {})

    def post(self, request):
        email = request.POST.get('email', '').strip().lower()

        if not email:
            return render(request, self.template_name, {
                'error': _('Please enter your email address.')
            })

        try:
            email_address = EmailAddress.objects.select_related('user').get(
                email__iexact=email
            )
        except EmailAddress.DoesNotExist:
            return render(request, self.template_name, {'sent': True})

        if email_address.verified:
            messages.info(request, _('This email is already verified. You can sign in.'))
            return redirect('account_login')

        user = email_address.user
        if not user or user.is_staff:
            return render(request, self.template_name, {'sent': True})

        if user.is_active:
            email_address.verified = True
            email_address.save(update_fields=['verified'])
            messages.info(request, _('Your email is already verified. You can sign in.'))
            return redirect('account_login')

        # All guards passed — send fresh verification link
        send_verification_email_to_address(request, email_address, signup=False)
        return render(request, self.template_name, {'sent': True})