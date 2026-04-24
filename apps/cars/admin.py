from django.contrib import admin
from .models import CarRental, CarPhoto

class CarPhotoInline(admin.TabularInline):
    model = CarPhoto
    extra = 1

@admin.register(CarRental)
class CarRentalAdmin(admin.ModelAdmin):
    list_display = ['name', 'vehicle_type', 'price_per_day', 'approval_status', 'is_available', 'is_active']
    list_filter = ['vehicle_type', 'approval_status', 'is_available']
    inlines = [CarPhotoInline]