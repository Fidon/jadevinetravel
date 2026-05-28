from django import forms
from django.utils.translation import gettext_lazy as _

from apps.hotels.models import Hotel, HotelRoomType, HotelPhoto
from apps.cars.models import CarRental, CarPhoto
from apps.tours.models import TourPackage, TourItineraryDay
from apps.bookings.models import Booking


# ---------------------------------------------------------------------------
# Shared widget helper — applies jd-input class to all visible inputs
# ---------------------------------------------------------------------------
def _jd(widget):
    """Adds jd-input CSS class to a widget instance."""
    widget.attrs.setdefault('class', '')
    widget.attrs['class'] = (widget.attrs['class'] + ' jd-input').strip()
    return widget


# ===========================================================================
# HOTEL FORMS
# ===========================================================================

class HotelForm(forms.ModelForm):
    """
    Used for both create and edit.
    Excludes: created_by, approval_status, rejection_reason, is_active, slug.
    All of those are set programmatically in the view — never from user input.
    """

    class Meta:
        model = Hotel
        fields = [
            'name', 'location',
            'description_en', 'description_fr', 'description_ru',
            'stars', 'price_per_night', 'address',
            'latitude', 'longitude', 'tripadvisor_url',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'jd-input',
                'placeholder': _('e.g. Zanzibar Serena Hotel'),
            }),
            'location': forms.Select(attrs={'class': 'jd-input'}),
            'stars': forms.Select(attrs={'class': 'jd-input'}),
            'price_per_night': forms.NumberInput(attrs={
                'class': 'jd-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'address': forms.TextInput(attrs={
                'class': 'jd-input',
                'placeholder': _('Street address or area description'),
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'jd-input',
                'placeholder': '-6.1659',
                'step': 'any',
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'jd-input',
                'placeholder': '39.2026',
                'step': 'any',
            }),
            'tripadvisor_url': forms.URLInput(attrs={
                'class': 'jd-input',
                'placeholder': 'https://www.tripadvisor.com/...',
            }),
            'description_en': forms.Textarea(attrs={
                'class': 'jd-input',
                'rows': 5,
                'placeholder': _('Describe this hotel in English (required)'),
            }),
            'description_fr': forms.Textarea(attrs={
                'class': 'jd-input',
                'rows': 4,
                'placeholder': _('Description in French (optional)'),
            }),
            'description_ru': forms.Textarea(attrs={
                'class': 'jd-input',
                'rows': 4,
                'placeholder': _('Description in Russian (optional)'),
            }),
        }
        labels = {
            'name':             _('Hotel Name'),
            'location':         _('Location'),
            'stars':            _('Star Rating'),
            'price_per_night':  _('Base Price Per Night (USD)'),
            'address':          _('Address'),
            'latitude':         _('Latitude (optional)'),
            'longitude':        _('Longitude (optional)'),
            'tripadvisor_url':  _('TripAdvisor URL (optional)'),
            'description_en':   _('Description — English'),
            'description_fr':   _('Description — French (optional)'),
            'description_ru':   _('Description — Russian (optional)'),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError(_('Hotel name is required.'))
        return name

    def clean_price_per_night(self):
        price = self.cleaned_data.get('price_per_night')
        if price is not None and price <= 0:
            raise forms.ValidationError(_('Price must be greater than zero.'))
        return price


class HotelRoomTypeForm(forms.ModelForm):
    """
    Modal form for adding/editing a room type on a hotel.
    amenities is handled as a plain textarea (newline-separated),
    converted to/from JSONField list in clean() and __init__.
    """
    amenities_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'jd-input',
            'rows': 3,
            'placeholder': _('WiFi\nAir Conditioning\nPool View\n(one per line)'),
        }),
        label=_('Amenities (one per line)'),
        help_text=_('Enter each amenity on a new line.'),
    )

    class Meta:
        model = HotelRoomType
        fields = [
            'name',
            'description_en', 'description_fr', 'description_ru',
            'price_per_night', 'max_guests', 'is_available',
            'discount_percent', 'discount_expires_at',
            'is_refundable', 'allows_pay_on_arrival', 'allows_pets',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'jd-input',
                'placeholder': _('e.g. Ocean View Suite'),
            }),
            'description_en': forms.Textarea(attrs={
                'class': 'jd-input', 'rows': 3,
                'placeholder': _('Room description in English (required)'),
            }),
            'description_fr': forms.Textarea(attrs={
                'class': 'jd-input', 'rows': 3,
                'placeholder': _('French (optional)'),
            }),
            'description_ru': forms.Textarea(attrs={
                'class': 'jd-input', 'rows': 3,
                'placeholder': _('Russian (optional)'),
            }),
            'price_per_night': forms.NumberInput(attrs={
                'class': 'jd-input',
                'placeholder': _('Leave blank to use hotel base price'),
                'step': '0.01', 'min': '0',
            }),
            'max_guests': forms.NumberInput(attrs={
                'class': 'jd-input', 'min': '1',
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'jd-input', 'min': '0', 'max': '99',
            }),
            'discount_expires_at': forms.DateTimeInput(
                attrs={'class': 'jd-input', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'is_available':          forms.CheckboxInput(),
            'is_refundable':         forms.CheckboxInput(),
            'allows_pay_on_arrival': forms.CheckboxInput(),
            'allows_pets':           forms.CheckboxInput(),
        }
        labels = {
            'name':                  _('Room Type Name'),
            'price_per_night':       _('Price Per Night (USD) — overrides hotel base if set'),
            'max_guests':            _('Max Guests'),
            'is_available':          _('Available for booking'),
            'discount_percent':      _('Discount (%)'),
            'discount_expires_at':   _('Discount Expires At'),
            'is_refundable':         _('Refundable'),
            'allows_pay_on_arrival': _('Allows Pay on Arrival'),
            'allows_pets':           _('Pets Allowed'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate amenities_text from the existing JSONField list
        if self.instance and self.instance.pk and self.instance.amenities:
            self.fields['amenities_text'].initial = '\n'.join(self.instance.amenities)
        # datetime-local inputs need this input_formats to parse correctly
        self.fields['discount_expires_at'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean_amenities_text(self):
        raw = self.cleaned_data.get('amenities_text', '')
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        return lines  # returns a list

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.amenities = self.cleaned_data.get('amenities_text', [])
        if commit:
            instance.save()
        return instance


class HotelRejectionForm(forms.Form):
    """
    Rejection reason form — rendered inside a Bootstrap modal.
    reason is required; submit button is also disabled by JS until non-empty.
    Server-side validation is the authority.
    """
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'jd-input',
            'rows': 4,
            'placeholder': _('Explain clearly why this listing is being rejected '
                              'so the partner can correct it and resubmit.'),
        }),
        label=_('Rejection Reason'),
        min_length=10,
        error_messages={
            'required':   _('A rejection reason is required.'),
            'min_length': _('Please provide a more detailed reason (at least 10 characters).'),
        }
    )


# ===========================================================================
# CAR FORMS
# ===========================================================================

class CarRentalForm(forms.ModelForm):
    """
    Used for both create and edit.
    pickup_locations stored as JSONField list but edited as newline-separated textarea.
    Excludes: created_by, approval_status, rejection_reason, is_active, slug.
    """
    pickup_locations_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'jd-input',
            'rows': 3,
            'placeholder': _('Zanzibar Airport\nStone Town\nNungwi\n(one per line)'),
        }),
        label=_('Pickup Locations (one per line)'),
    )

    class Meta:
        model = CarRental
        fields = [
            'name', 'vehicle_type', 'make', 'model', 'year',
            'capacity', 'fuel_type', 'transmission',
            'price_per_day',
            'offers_self_drive', 'offers_driver',
            'driver_speaks_en', 'driver_speaks_fr',
            'description_en', 'description_fr', 'description_ru',
            'discount_percent', 'discount_expires_at',
            'is_refundable', 'allows_pay_on_arrival', 'allows_pets',
            'is_available',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'jd-input',
                'placeholder': _('e.g. Toyota Land Cruiser 4x4'),
            }),
            'vehicle_type': forms.Select(attrs={'class': 'jd-input'}),
            'make': forms.TextInput(attrs={
                'class': 'jd-input', 'placeholder': 'Toyota',
            }),
            'model': forms.TextInput(attrs={
                'class': 'jd-input', 'placeholder': 'Land Cruiser',
            }),
            'year': forms.NumberInput(attrs={
                'class': 'jd-input', 'min': '1990', 'max': '2030',
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'jd-input', 'min': '1',
            }),
            'fuel_type': forms.Select(attrs={'class': 'jd-input'}),
            'transmission': forms.Select(attrs={'class': 'jd-input'}),
            'price_per_day': forms.NumberInput(attrs={
                'class': 'jd-input', 'step': '0.01', 'min': '0',
                'placeholder': '0.00',
            }),
            'description_en': forms.Textarea(attrs={
                'class': 'jd-input', 'rows': 4,
                'placeholder': _('Describe this vehicle in English (required)'),
            }),
            'description_fr': forms.Textarea(attrs={
                'class': 'jd-input', 'rows': 3,
                'placeholder': _('French (optional)'),
            }),
            'description_ru': forms.Textarea(attrs={
                'class': 'jd-input', 'rows': 3,
                'placeholder': _('Russian (optional)'),
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'jd-input', 'min': '0', 'max': '99',
            }),
            'discount_expires_at': forms.DateTimeInput(
                attrs={'class': 'jd-input', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'offers_self_drive':     forms.CheckboxInput(),
            'offers_driver':         forms.CheckboxInput(),
            'driver_speaks_en':      forms.CheckboxInput(),
            'driver_speaks_fr':      forms.CheckboxInput(),
            'is_refundable':         forms.CheckboxInput(),
            'allows_pay_on_arrival': forms.CheckboxInput(),
            'allows_pets':           forms.CheckboxInput(),
            'is_available':          forms.CheckboxInput(),
        }
        labels = {
            'name':                  _('Vehicle Name'),
            'vehicle_type':          _('Vehicle Type'),
            'price_per_day':         _('Price Per Day (USD)'),
            'capacity':              _('Passenger Capacity'),
            'offers_self_drive':     _('Offers Self-Drive'),
            'offers_driver':         _('Offers Driver'),
            'driver_speaks_en':      _('Driver speaks English'),
            'driver_speaks_fr':      _('Driver speaks French'),
            'discount_percent':      _('Discount (%)'),
            'discount_expires_at':   _('Discount Expires At'),
            'is_refundable':         _('Refundable'),
            'allows_pay_on_arrival': _('Allows Pay on Arrival'),
            'allows_pets':           _('Pets Allowed'),
            'is_available':          _('Available for booking'),
            'description_en':        _('Description — English'),
            'description_fr':        _('Description — French (optional)'),
            'description_ru':        _('Description — Russian (optional)'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discount_expires_at'].input_formats = ['%Y-%m-%dT%H:%M']
        if self.instance and self.instance.pk and self.instance.pickup_locations:
            self.fields['pickup_locations_text'].initial = '\n'.join(
                self.instance.pickup_locations
            )

    def clean_price_per_day(self):
        price = self.cleaned_data.get('price_per_day')
        if price is not None and price <= 0:
            raise forms.ValidationError(_('Price must be greater than zero.'))
        return price

    def clean_pickup_locations_text(self):
        raw = self.cleaned_data.get('pickup_locations_text', '')
        return [line.strip() for line in raw.splitlines() if line.strip()]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.pickup_locations = self.cleaned_data.get('pickup_locations_text', [])
        if commit:
            instance.save()
        return instance


class CarRejectionForm(forms.Form):
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'jd-input',
            'rows': 4,
            'placeholder': _('Explain clearly why this listing is being rejected '
                              'so the partner can correct it and resubmit.'),
        }),
        label=_('Rejection Reason'),
        min_length=10,
        error_messages={
            'required':   _('A rejection reason is required.'),
            'min_length': _('Please provide a more detailed reason (at least 10 characters).'),
        }
    )


# ===========================================================================
# TOUR FORMS
# ===========================================================================

class TourPackageForm(forms.ModelForm):
    """
    Super Admin only. No approval fields — tours skip the workflow entirely.
    highlights/inclusions/exclusions stored as JSONField lists but edited as
    newline-separated textareas, same pattern as amenities and pickup_locations.
    """
    highlights_en_text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 4, 'placeholder': _('Witness the Great Migration\nGame drives at dawn\n(one per line)')}), label=_('Highlights — English'))
    highlights_fr_text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 3, 'placeholder': _('French (optional)')}),  label=_('Highlights — French'))
    highlights_ru_text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 3, 'placeholder': _('Russian (optional)')}),  label=_('Highlights — Russian'))

    inclusions_en_text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 4, 'placeholder': _('Airport transfers\nAll meals\n(one per line)')}), label=_('Inclusions — English'))
    inclusions_fr_text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 3}), label=_('Inclusions — French'))
    inclusions_ru_text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 3}), label=_('Inclusions — Russian'))

    exclusions_en_text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 4, 'placeholder': _('International flights\nTravel insurance\n(one per line)')}), label=_('Exclusions — English'))
    exclusions_fr_text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 3}), label=_('Exclusions — French'))
    exclusions_ru_text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'jd-input', 'rows': 3}), label=_('Exclusions — Russian'))

    class Meta:
        model = TourPackage
        fields = [
            'name_en', 'name_fr', 'name_ru',
            'tour_type', 'duration_days', 'group_size_max',
            'price_per_person',
            'description_en', 'description_fr', 'description_ru',
            'what_to_bring_en', 'what_to_bring_fr', 'what_to_bring_ru',
            'cover_image', 'is_active', 'is_featured',
            'discount_percent', 'discount_expires_at',
            'is_refundable', 'allows_pay_on_arrival', 'allows_pets',
        ]
        widgets = {
            'name_en': forms.TextInput(attrs={'class': 'jd-input', 'placeholder': _('e.g. Serengeti Safari — 5 Days')}),
            'name_fr': forms.TextInput(attrs={'class': 'jd-input', 'placeholder': _('French name (optional)')}),
            'name_ru': forms.TextInput(attrs={'class': 'jd-input', 'placeholder': _('Russian name (optional)')}),
            'tour_type':        forms.Select(attrs={'class': 'jd-input'}),
            'duration_days':    forms.NumberInput(attrs={'class': 'jd-input', 'min': '1'}),
            'group_size_max':   forms.NumberInput(attrs={'class': 'jd-input', 'min': '1'}),
            'price_per_person': forms.NumberInput(attrs={'class': 'jd-input', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'description_en':   forms.Textarea(attrs={'class': 'jd-input', 'rows': 5, 'placeholder': _('Full tour description in English (required)')}),
            'description_fr':   forms.Textarea(attrs={'class': 'jd-input', 'rows': 4}),
            'description_ru':   forms.Textarea(attrs={'class': 'jd-input', 'rows': 4}),
            'what_to_bring_en': forms.Textarea(attrs={'class': 'jd-input', 'rows': 3, 'placeholder': _('Sunscreen, hat, comfortable shoes...')}),
            'what_to_bring_fr': forms.Textarea(attrs={'class': 'jd-input', 'rows': 3}),
            'what_to_bring_ru': forms.Textarea(attrs={'class': 'jd-input', 'rows': 3}),
            'cover_image':      forms.ClearableFileInput(attrs={'class': 'jd-input'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'jd-input', 'min': '0', 'max': '99'}),
            'discount_expires_at': forms.DateTimeInput(
                attrs={'class': 'jd-input', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'is_active':             forms.CheckboxInput(),
            'is_featured':           forms.CheckboxInput(),
            'is_refundable':         forms.CheckboxInput(),
            'allows_pay_on_arrival': forms.CheckboxInput(),
            'allows_pets':           forms.CheckboxInput(),
        }
        labels = {
            'name_en':               _('Package Name — English'),
            'name_fr':               _('Package Name — French (optional)'),
            'name_ru':               _('Package Name — Russian (optional)'),
            'tour_type':             _('Tour Type'),
            'duration_days':         _('Duration (days)'),
            'group_size_max':        _('Max Group Size'),
            'price_per_person':      _('Price Per Person (USD)'),
            'description_en':        _('Description — English'),
            'description_fr':        _('Description — French (optional)'),
            'description_ru':        _('Description — Russian (optional)'),
            'what_to_bring_en':      _('What to Bring — English'),
            'what_to_bring_fr':      _('What to Bring — French (optional)'),
            'what_to_bring_ru':      _('What to Bring — Russian (optional)'),
            'cover_image':           _('Cover Image'),
            'discount_percent':      _('Discount (%)'),
            'discount_expires_at':   _('Discount Expires At'),
            'is_active':             _('Published (visible on site)'),
            'is_featured':           _('Featured on homepage'),
            'is_refundable':         _('Refundable'),
            'allows_pay_on_arrival': _('Allows Pay on Arrival'),
            'allows_pets':           _('Pets Allowed'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discount_expires_at'].input_formats = ['%Y-%m-%dT%H:%M']

        if self.instance and self.instance.pk:
            def to_text(val):
                if isinstance(val, list):
                    return '\n'.join(str(v) for v in val)
                return ''
            self.fields['highlights_en_text'].initial = to_text(self.instance.highlights_en)
            self.fields['highlights_fr_text'].initial = to_text(self.instance.highlights_fr)
            self.fields['highlights_ru_text'].initial = to_text(self.instance.highlights_ru)
            self.fields['inclusions_en_text'].initial = to_text(self.instance.inclusions_en)
            self.fields['inclusions_fr_text'].initial = to_text(self.instance.inclusions_fr)
            self.fields['inclusions_ru_text'].initial = to_text(self.instance.inclusions_ru)
            self.fields['exclusions_en_text'].initial = to_text(self.instance.exclusions_en)
            self.fields['exclusions_fr_text'].initial = to_text(self.instance.exclusions_fr)
            self.fields['exclusions_ru_text'].initial = to_text(self.instance.exclusions_ru)

    def _text_to_list(self, field_name):
        raw = self.cleaned_data.get(field_name, '')
        return [line.strip() for line in raw.splitlines() if line.strip()]

    def clean_price_per_person(self):
        price = self.cleaned_data.get('price_per_person')
        if price is not None and price <= 0:
            raise forms.ValidationError(_('Price must be greater than zero.'))
        return price

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.highlights_en = self._text_to_list('highlights_en_text')
        instance.highlights_fr = self._text_to_list('highlights_fr_text')
        instance.highlights_ru = self._text_to_list('highlights_ru_text')
        instance.inclusions_en = self._text_to_list('inclusions_en_text')
        instance.inclusions_fr = self._text_to_list('inclusions_fr_text')
        instance.inclusions_ru = self._text_to_list('inclusions_ru_text')
        instance.exclusions_en = self._text_to_list('exclusions_en_text')
        instance.exclusions_fr = self._text_to_list('exclusions_fr_text')
        instance.exclusions_ru = self._text_to_list('exclusions_ru_text')
        if commit:
            instance.save()
        return instance


class TourItineraryDayForm(forms.ModelForm):
    class Meta:
        model = TourItineraryDay
        fields = [
            'day_number',
            'title_en', 'title_fr', 'title_ru',
            'description_en', 'description_fr', 'description_ru',
        ]
        widgets = {
            'day_number':     forms.NumberInput(attrs={'class': 'jd-input', 'min': '1'}),
            'title_en':       forms.TextInput(attrs={'class': 'jd-input', 'placeholder': _('e.g. Arrival in Arusha')}),
            'title_fr':       forms.TextInput(attrs={'class': 'jd-input', 'placeholder': _('French (optional)')}),
            'title_ru':       forms.TextInput(attrs={'class': 'jd-input', 'placeholder': _('Russian (optional)')}),
            'description_en': forms.Textarea(attrs={'class': 'jd-input', 'rows': 4, 'placeholder': _('Full day description in English (required)')}),
            'description_fr': forms.Textarea(attrs={'class': 'jd-input', 'rows': 3}),
            'description_ru': forms.Textarea(attrs={'class': 'jd-input', 'rows': 3}),
        }
        labels = {
            'day_number':     _('Day Number'),
            'title_en':       _('Title — English'),
            'title_fr':       _('Title — French (optional)'),
            'title_ru':       _('Title — Russian (optional)'),
            'description_en': _('Description — English'),
            'description_fr': _('Description — French (optional)'),
            'description_ru': _('Description — Russian (optional)'),
        }


# ===========================================================================
# BOOKING FORMS
# ===========================================================================

# Valid status transitions per current status.
# Admin cannot set arbitrary statuses — only logically valid next states.
STATUS_TRANSITIONS = {
    'pending_confirmation':   ['confirmed', 'cancelled'],
    'confirmed':              ['completed', 'no_show', 'cancelled'],
    'cancellation_requested': ['cancelled', 'confirmed'],
    'cancelled':              [],
    'completed':              [],
    'no_show':                [],
}


class BookingStatusForm(forms.Form):
    """
    Status update form. Choices are filtered to valid transitions only,
    computed in the view based on booking.status.
    """
    status = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'jd-input'}),
        label=_('Update Status'),
    )
    admin_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'jd-input',
            'rows': 2,
            'placeholder': _('Optional note (internal only, not shown to customer)'),
        }),
        label=_('Internal Note (optional)'),
    )

    def __init__(self, current_status, *args, **kwargs):
        super().__init__(*args, **kwargs)
        valid_next = STATUS_TRANSITIONS.get(current_status, [])
        all_choices = dict(Booking.STATUS_CHOICES)
        choices = [('', f'— {all_choices.get(current_status, current_status)} (current) —')]
        choices += [(s, all_choices[s]) for s in valid_next if s in all_choices]
        self.fields['status'].choices = choices


class BookingMarkPaidForm(forms.Form):
    """
    Marks a Pay on Arrival booking as fully paid.
    Simple confirmation — no extra fields needed.
    """
    confirm = forms.BooleanField(
        required=True,
        widget=forms.HiddenInput(),
        initial=True,
    )