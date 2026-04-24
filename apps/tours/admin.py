from django.contrib import admin
from .models import TourPackage, TourItineraryDay, TourPhoto

class TourItineraryDayInline(admin.TabularInline):
    model = TourItineraryDay
    extra = 1

class TourPhotoInline(admin.TabularInline):
    model = TourPhoto
    extra = 1

@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'tour_type', 'duration_days', 'price_per_person', 'is_active', 'is_featured']
    list_filter = ['tour_type', 'is_active', 'is_featured']
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [TourItineraryDayInline, TourPhotoInline]