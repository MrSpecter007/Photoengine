from django.contrib import admin

from .models import (
    EditionFormat,
    PhotoCollection,
    Photograph,
    PhotographEdition,
    PrintSize,
)


class PhotographInline(admin.TabularInline):
    model = Photograph
    extra = 0
    fields = ("title", "code", "location_name", "public_edition_size", "is_active", "is_sold_out")
    show_change_link = True


class PhotographEditionInline(admin.TabularInline):
    model = PhotographEdition
    extra = 0
    fields = ("edition_type", "number", "status")


@admin.register(PhotoCollection)
class PhotoCollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "launch_date", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("title",), "code": ("title",)}
    inlines = [PhotographInline]


@admin.register(Photograph)
class PhotographAdmin(admin.ModelAdmin):
    list_display = ("title", "collection", "location_name", "public_edition_size", "remaining_public_editions", "is_active", "is_sold_out")
    list_filter = ("collection", "is_active", "is_sold_out", "is_preorder")
    prepopulated_fields = {"slug": ("title",), "code": ("title",)}
    inlines = [PhotographEditionInline]

    def remaining_public_editions(self, obj):
        return obj.remaining_public_editions
    remaining_public_editions.short_description = "Remaining"


@admin.register(PhotographEdition)
class PhotographEditionAdmin(admin.ModelAdmin):
    list_display = ("photograph", "edition_type", "number", "status")
    list_filter = ("edition_type", "status", "photograph__collection")


@admin.register(EditionFormat)
class EditionFormatAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "sort_order", "is_active")
    prepopulated_fields = {"code": ("name",)}


@admin.register(PrintSize)
class PrintSizeAdmin(admin.ModelAdmin):
    list_display = ("label", "aspect_ratio", "width_in", "height_in", "is_active")
    list_filter = ("aspect_ratio", "is_active")
