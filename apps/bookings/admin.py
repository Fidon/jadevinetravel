from django.contrib import admin
from .models import Booking, CancellationPolicy

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['reference', 'user', 'service_type', 'status', 'payment_status', 'total_price', 'created_at']
    list_filter = ['service_type', 'status', 'payment_status', 'payment_mode']
    search_fields = ['reference', 'user__email']
    readonly_fields = ['reference', 'created_at', 'updated_at']

@admin.register(CancellationPolicy)
class CancellationPolicyAdmin(admin.ModelAdmin):
    list_display = ['service_type', 'days_before_service', 'refund_percentage', 'is_active']