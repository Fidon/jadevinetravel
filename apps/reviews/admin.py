from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'service_type', 'rating', 'status', 'created_at']
    list_filter = ['service_type', 'status']
    list_editable = ['status']
    search_fields = ['user__email', 'comment']
    readonly_fields = ['user', 'booking', 'service_type', 'hotel', 'tour_package',
                       'car', 'rating', 'comment', 'created_at']