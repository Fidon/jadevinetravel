from django.contrib import admin
from .models import Hotel, HotelPhoto, HotelRoomType

class HotelPhotoInline(admin.TabularInline):
    model = HotelPhoto
    extra = 1

class HotelRoomTypeInline(admin.TabularInline):
    model = HotelRoomType
    extra = 1

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'stars', 'approval_status', 'is_active', 'created_by']
    list_filter = ['location', 'approval_status', 'is_active', 'stars']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [HotelPhotoInline, HotelRoomTypeInline]