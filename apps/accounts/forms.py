from django import forms
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm as AllauthSignupForm
from apps.accounts.models import CustomUser
from django.core.exceptions import ValidationError


class CustomSignupForm(AllauthSignupForm):
    """
    Extends allauth's SignupForm to add first_name, last_name,
    preferred_language. allauth calls adapter.save_user() which reads
    these from cleaned_data — the form just needs to declare and validate them.
    """

    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fr', _('Français')),
        ('ru', _('Русский')),
    ]

    first_name = forms.CharField(
        max_length=150,
        label=_('First Name'),
        widget=forms.TextInput(attrs={
            'class': 'jd-input',
            'placeholder': _('First name'),
            'autocomplete': 'given-name',
        })
    )
    last_name = forms.CharField(
        max_length=150,
        label=_('Last Name'),
        widget=forms.TextInput(attrs={
            'class': 'jd-input',
            'placeholder': _('Last name'),
            'autocomplete': 'family-name',
        })
    )
    preferred_language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        label=_('Preferred Language'),
        initial='en',
        widget=forms.Select(attrs={'class': 'jd-input'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply jd-input class to allauth's built-in email/password fields
        for field_name in ('email', 'password1', 'password2'):
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['class'] = 'jd-input'
        self.fields['email'].widget.attrs['placeholder'] = _('Email address')
        self.fields['email'].widget.attrs['autocomplete'] = 'email'
        self.fields['password1'].widget.attrs['placeholder'] = _('Password')
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'].widget.attrs['placeholder'] = _('Confirm password')
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'

    def save(self, request):
        """
        allauth calls form.save(request) at the end of signup.
        We delegate to the adapter via super() — adapter.save_user()
        reads first_name, last_name, preferred_language from self.cleaned_data.
        """
        user = super().save(request)
        return user


NATIONALITY_CHOICES = [
    'Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan',
    'Argentinian', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani',
    'Bahraini', 'Bangladeshi', 'Belarusian', 'Belgian', 'Bolivian',
    'Bosnian', 'Brazilian', 'British', 'Bulgarian', 'Cambodian',
    'Cameroonian', 'Canadian', 'Chilean', 'Chinese', 'Colombian',
    'Congolese', 'Croatian', 'Cuban', 'Czech', 'Danish', 'Dominican',
    'Dutch', 'Ecuadorian', 'Egyptian', 'Emirati', 'Estonian', 'Ethiopian',
    'Finnish', 'French', 'Gambian', 'Georgian', 'German', 'Ghanaian',
    'Greek', 'Guatemalan', 'Guinean', 'Haitian', 'Honduran', 'Hungarian',
    'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli',
    'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakh',
    'Kenyan', 'Korean', 'Kuwaiti', 'Kyrgyz', 'Latvian', 'Lebanese',
    'Libyan', 'Lithuanian', 'Luxembourgish', 'Macedonian', 'Malagasy',
    'Malawian', 'Malaysian', 'Maldivian', 'Malian', 'Maltese', 'Mexican',
    'Moldovan', 'Mongolian', 'Montenegrin', 'Moroccan', 'Mozambican',
    'Namibian', 'Nepali', 'New Zealander', 'Nicaraguan', 'Nigerian',
    'Norwegian', 'Omani', 'Pakistani', 'Palestinian', 'Panamanian',
    'Paraguayan', 'Peruvian', 'Filipino', 'Polish', 'Portuguese', 'Qatari',
    'Romanian', 'Russian', 'Rwandan', 'Saudi', 'Senegalese', 'Serbian',
    'Singaporean', 'Slovak', 'Slovenian', 'Somali', 'South African',
    'Spanish', 'Sri Lankan', 'Sudanese', 'Swedish', 'Swiss', 'Syrian',
    'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tunisian',
    'Turkish', 'Turkmen', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbek',
    'Venezuelan', 'Vietnamese', 'Yemeni', 'Zambian', 'Zimbabwean',
]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone', 'nationality', 'preferred_language', 'profile_photo']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'jd-input',
                'placeholder': _('First name'),
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'jd-input',
                'placeholder': _('Last name'),
            }),
            'phone': forms.TextInput(attrs={
                'class': 'jd-input',
                'placeholder': _('+255 7XX XXX XXX'),
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'jd-input',
                'placeholder': _('Select or type your nationality'),
                'list': 'nationality-options',
                'autocomplete': 'off',
            }),
            'preferred_language': forms.Select(attrs={'class': 'jd-input'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'jd-file-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False
        self.fields['nationality'].required = False
        self.fields['profile_photo'].required = False
        
    def clean_nationality(self):
        nationality = self.cleaned_data.get('nationality')
        if nationality and nationality not in NATIONALITY_CHOICES:
            raise ValidationError(_("Please select a valid nationality from the list."))
        return nationality

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            user_id = self.instance.pk
            if CustomUser.objects.filter(phone=phone).exclude(pk=user_id).exists():
                raise ValidationError(_("This phone number is already used by another user."))
        return phone


class CancellationForm(forms.Form):
    """
    Shown to customer before confirming cancellation.
    Captures optional reason and requires explicit confirmation checkbox.
    """

    cancellation_reason = forms.CharField(
        required=False,
        label=_('Reason for cancellation (optional)'),
        widget=forms.Textarea(attrs={
            'class': 'jd-input',
            'rows': 3,
            'placeholder': _('Let us know why you are cancelling (optional)'),
        })
    )
    confirm = forms.BooleanField(
        required=True,
        label=_('I understand and confirm this cancellation'),
        error_messages={
            'required': _('You must confirm to proceed with cancellation.')
        }
    )