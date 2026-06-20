from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class HotelBookingForm(forms.Form):
    """
    Rendered on the hotel detail page.
    Validated server-side in HotelBookingView.
    Data stored in session on success — no DB write at this point.

    Total price = price_per_night × nights × num_rooms
    Guest validation: total_occupants <= max_guests × num_rooms
    Pets validation: enforced if room_type.allows_pets=False
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
    num_rooms = forms.IntegerField(
        label=_('Number of Rooms'),
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    num_adults = forms.IntegerField(
        label=_('Adults'),
        min_value=1,
        max_value=40,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    num_children = forms.IntegerField(
        label=_('Children (2–12)'),
        min_value=0,
        max_value=20,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    num_infants = forms.IntegerField(
        label=_('Infants (under 2)'),
        min_value=0,
        max_value=10,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    num_pets = forms.IntegerField(
        label=_('Pets'),
        min_value=0,
        max_value=5,
        initial=0,
        required=False,
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

        # Normalise optional fields to 0 when omitted
        cleaned['num_children'] = cleaned.get('num_children') or 0
        cleaned['num_infants'] = cleaned.get('num_infants') or 0
        cleaned['num_pets'] = cleaned.get('num_pets') or 0

        return cleaned


class CarBookingForm(forms.Form):
    """
    Rendered on the car detail page.
    Pets enforced server-side in CarBookingView against car.allows_pets.
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
    num_adults = forms.IntegerField(
        label=_('Adults'),
        min_value=1,
        max_value=20,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    num_children = forms.IntegerField(
        label=_('Children (2–12)'),
        min_value=0,
        max_value=20,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    num_infants = forms.IntegerField(
        label=_('Infants (under 2)'),
        min_value=0,
        max_value=10,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    num_pets = forms.IntegerField(
        label=_('Pets'),
        min_value=0,
        max_value=5,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    driver_licence_number = forms.CharField(
        label=_('Driver\'s Licence Number'),
        max_length=50,
        required=False,
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

        if rental_mode == 'self_drive' and not licence:
            self.add_error(
                'driver_licence_number',
                _("Driver's licence number is required for self-drive rentals.")
            )

        if pickup and pickup < today:
            self.add_error('pickup_date', _('Pickup date cannot be in the past.'))

        if pickup and returns:
            if returns < pickup:
                self.add_error('return_date', _('Return date cannot be before pickup date.'))

        cleaned['num_children'] = cleaned.get('num_children') or 0
        cleaned['num_infants'] = cleaned.get('num_infants') or 0
        cleaned['num_pets'] = cleaned.get('num_pets') or 0

        return cleaned


class TourBookingForm(forms.Form):
    """
    Rendered on the tour detail page.
    num_participants = adults + children (infants travel free on tours).
    Pets enforced server-side in TourBookingView against tour.allows_pets.
    """
    preferred_date = forms.DateField(
        label=_('Preferred Start Date'),
        widget=forms.DateInput(
            attrs={'type': 'text', 'class': 'jd-input', 'autocomplete': 'off'}
        ),
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
    )
    num_adults = forms.IntegerField(
        label=_('Adults'),
        min_value=1,
        max_value=50,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    num_children = forms.IntegerField(
        label=_('Children (2–12)'),
        min_value=0,
        max_value=20,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    num_infants = forms.IntegerField(
        label=_('Infants (under 2)'),
        min_value=0,
        max_value=10,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'jd-input'}),
    )
    num_pets = forms.IntegerField(
        label=_('Pets'),
        min_value=0,
        max_value=5,
        initial=0,
        required=False,
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
        today = timezone.now().date()

        if preferred_date and preferred_date < today:
            self.add_error('preferred_date', _('Preferred date cannot be in the past.'))

        cleaned['num_children'] = cleaned.get('num_children') or 0
        cleaned['num_infants'] = cleaned.get('num_infants') or 0
        cleaned['num_pets'] = cleaned.get('num_pets') or 0

        return cleaned


class PaymentModeForm(forms.Form):
    PAYMENT_MODE_CHOICES = [
        ('pay_now', _('Pay Now — Visa, Mastercard, M-Pesa, AirtelMoney, MixxYas')),
        ('pay_on_arrival', _('Pay on Arrival — Pay when you arrive in Tanzania')),
    ]

    payment_mode = forms.ChoiceField(
        choices=PAYMENT_MODE_CHOICES,
        widget=forms.RadioSelect(),
        label=_('How would you like to pay?'),
    )