from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django import forms as django_forms

from apps.bookings.models import CancellationPolicy
from apps.portal.mixins import SuperAdminRequiredMixin


# ---------------------------------------------------------------------------
# Form
# ---------------------------------------------------------------------------

class CancellationPolicyForm(django_forms.ModelForm):
    class Meta:
        model  = CancellationPolicy
        fields = [
            'service_type', 'days_before_service',
            'refund_percentage', 'label_en', 'is_active',
        ]
        widgets = {
            'service_type': django_forms.Select(attrs={'class': 'jd-input'}),
            'days_before_service': django_forms.NumberInput(attrs={
                'class': 'jd-input', 'min': '0',
                'placeholder': '14',
            }),
            'refund_percentage': django_forms.NumberInput(attrs={
                'class': 'jd-input', 'min': '0', 'max': '100',
                'placeholder': '100',
            }),
            'label_en': django_forms.TextInput(attrs={
                'class': 'jd-input',
                'placeholder': _('e.g. Full refund (14+ days before service)'),
            }),
            'is_active': django_forms.CheckboxInput(),
        }
        labels = {
            'service_type':       _('Service Type'),
            'days_before_service': _('Days Before Service'),
            'refund_percentage':   _('Refund Percentage (%)'),
            'label_en':            _('Label (English)'),
            'is_active':           _('Active'),
        }

    def clean_refund_percentage(self):
        val = self.cleaned_data.get('refund_percentage')
        if val is None or not (0 <= val <= 100):
            raise django_forms.ValidationError(
                _('Refund percentage must be between 0 and 100.')
            )
        return val

    def clean_days_before_service(self):
        val = self.cleaned_data.get('days_before_service')
        if val is None or val < 0:
            raise django_forms.ValidationError(
                _('Days must be 0 or greater.')
            )
        return val


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class PortalPoliciesView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_policies.html'

    def get(self, request):
        # Group by service type for display
        all_policies = CancellationPolicy.objects.all().order_by(
            'service_type', '-days_before_service'
        )
        grouped = {}
        for policy in all_policies:
            grouped.setdefault(policy.service_type, []).append(policy)

        context = {
            'grouped':    grouped,
            'add_form':   CancellationPolicyForm(),
            'service_types': CancellationPolicy.SERVICE_TYPE_CHOICES,
        }
        return render(request, self.template_name, context)


class PortalPolicyAddView(SuperAdminRequiredMixin, View):

    def post(self, request):
        form = CancellationPolicyForm(request.POST)
        if form.is_valid():
            policy = form.save()
            messages.success(
                request,
                _(f'Policy "{policy.label_en}" created.')
            )
        else:
            errors = '; '.join(
                f'{f}: {", ".join(errs)}'
                for f, errs in form.errors.items()
            )
            messages.error(request, f'{_("Could not create policy")}: {errors}')
        return redirect('portal:policies')


class PortalPolicyEditView(SuperAdminRequiredMixin, View):

    def post(self, request, pk):
        policy = get_object_or_404(CancellationPolicy, pk=pk)
        form   = CancellationPolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                _(f'Policy "{policy.label_en}" updated.')
            )
        else:
            errors = '; '.join(
                f'{f}: {", ".join(errs)}'
                for f, errs in form.errors.items()
            )
            messages.error(request, f'{_("Could not update policy")}: {errors}')
        return redirect('portal:policies')


class PortalPolicyDeleteView(SuperAdminRequiredMixin, View):

    def post(self, request, pk):
        policy = get_object_or_404(CancellationPolicy, pk=pk)
        label  = policy.label_en
        policy.delete()
        messages.success(request, _(f'Policy "{label}" deleted.'))
        return redirect('portal:policies')