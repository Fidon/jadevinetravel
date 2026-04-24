from django.contrib import admin
from .models import GalleryCategory, GalleryItem

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ['media_type', 'category', 'is_featured', 'order']
    list_filter = ['media_type', 'category', 'is_featured']