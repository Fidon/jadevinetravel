from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class HotelBookingForm(forms.Form):
    """
    Rendered on the hotel detail page.
    Validated server-side in HotelBookingView.
    Data stored in session on success — no DB write at this point.
    """
    room_type_id = forms.IntegerField(widget=forms.HiddenInput())
    check_in_date = forms.DateField(
        label=_('Check-in Date'),
        widget=forms.DateInput(attrs={'type': 'text', 'class': 'jd-input', 'autocomplete': 'off'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
    )
    check_out_date = forms.DateField(
        label=_('Check-out Date'),
        widget=forms.DateInput(attrs={'type': 'text', 'class': 'jd-input', 'autocomplete': 'off'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
    )
    num_guests = forms.IntegerField(
        label=_('Number of Guests'),
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    special_requests = forms.CharField(
        label=_('Special Requests'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 3}),
    )

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get('check_in_date')
        check_out = cleaned.get('check_out_date')
        today = timezone.now().date()

        if check_in and check_in < today:
            self.add_error('check_in_date', _('Check-in date cannot be in the past.'))

        if check_in and check_out:
            if check_out <= check_in:
                self.add_error('check_out_date', _('Check-out must be after check-in.'))

        return cleaned


class CarBookingForm(forms.Form):
    """
    Rendered on the car detail page.
    Conditional server-side validation: licence required for self-drive.
    Data stored in session on success — no DB write at this point.
    """
    RENTAL_MODE_CHOICES = [
        ('with_driver', _('With Driver')),
        ('self_drive', _('Self Drive')),
    ]

    rental_mode = forms.ChoiceField(
        label=_('Rental Mode'),
        choices=RENTAL_MODE_CHOICES,
        widget=forms.RadioSelect(),
    )
    pickup_location = forms.CharField(
        label=_('Pickup Location'),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'jd-input'}),
    )
    pickup_date = forms.DateField(
        label=_('Pickup Date'),
        widget=forms.DateInput(attrs={'type': 'text', 'class': 'jd-input', 'autocomplete': 'off'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
    )
    return_date = forms.DateField(
        label=_('Return Date'),
        widget=forms.DateInput(attrs={'type': 'text', 'class': 'jd-input', 'autocomplete': 'off'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
    )
    driver_licence_number = forms.CharField(
        label=_('Driver\'s Licence Number'),
        max_length=50,
        required=False,  # Conditionally required — enforced in clean()
        widget=forms.TextInput(attrs={'class': 'jd-input'}),
    )
    special_requests = forms.CharField(
        label=_('Special Requests'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 3}),
    )

    def clean(self):
        cleaned = super().clean()
        rental_mode = cleaned.get('rental_mode')
        licence = cleaned.get('driver_licence_number', '').strip()
        pickup = cleaned.get('pickup_date')
        returns = cleaned.get('return_date')
        today = timezone.now().date()

        # Licence is required for self-drive — enforced server-side, not just jQuery
        if rental_mode == 'self_drive' and not licence:
            self.add_error(
                'driver_licence_number',
                _("Driver's licence number is required for self-drive rentals.")
            )

        if pickup and pickup < today:
            self.add_error('pickup_date', _('Pickup date cannot be in the past.'))

        if pickup and returns:
            if returns <= pickup:
                self.add_error('return_date', _('Return date must be after pickup date.'))

        return cleaned


class PaymentModeForm(forms.Form):
    """
    On the booking summary page — user selects Pay Now or Pay on Arrival.
    This form submit triggers the actual Booking DB record creation.
    """
    PAYMENT_MODE_CHOICES = [
        ('pay_now', _('Pay Now — Visa, Mastercard, M-Pesa, AirtelMoney, MixxYas')),
        ('pay_on_arrival', _('Pay on Arrival — Pay when you arrive in Tanzania')),
    ]

    payment_mode = forms.ChoiceField(
        choices=PAYMENT_MODE_CHOICES,
        widget=forms.RadioSelect(),
        label=_('How would you like to pay?'),
    )


class TourBookingForm(forms.Form):
    """
    Rendered on the tour detail page.
    Validated server-side in TourBookingView.
    Data stored in session on success — no DB write at this point.
    Tours always create bookings with status='pending_confirmation'
    because Jadevine must manually confirm the preferred date.
    """
    preferred_date = forms.DateField(
        label=_('Preferred Start Date'),
        widget=forms.DateInput(
            attrs={'type': 'text', 'class': 'jd-input', 'autocomplete': 'off'}
        ),
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
    )
    num_participants = forms.IntegerField(
        label=_('Number of Participants'),
        min_value=1,
        max_value=50,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    special_requests = forms.CharField(
        label=_('Special Requests'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 3}),
    )

    def clean(self):
        cleaned = super().clean()
        preferred_date = cleaned.get('preferred_date')
        # num_participants = cleaned.get('num_participants')
        today = timezone.now().date()

        if preferred_date and preferred_date < today:
            self.add_error('preferred_date', _('Preferred date cannot be in the past.'))

        # num_participants max against group_size_max is validated in the view,
        # not here, because the form has no reference to the TourPackage instance.

        return cleaned