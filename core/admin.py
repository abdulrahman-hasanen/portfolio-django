import logging
from functools import partial

from django.contrib import admin, messages
from django.db import transaction
from django.utils.html import format_html

from .models import ContactMessage, Project


logger = logging.getLogger(__name__)


# =========================================================
# PROJECT ADMIN
# =========================================================


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        "image_preview",
        "title",
        "role",
        "tech_stack",
        "status",
        "is_published",
        "order",
        "created_at",
    )

    list_display_links = ("title",)

    list_editable = (
        "status",
        "is_published",
        "order",
    )

    list_filter = (
        "is_published",
        "status",
    )

    search_fields = (
        "title",
        "subtitle",
        "description",
        "role",
        "tech_stack",
    )

    date_hierarchy = "created_at"
    ordering = ("order", "-created_at")
    list_per_page = 25
    save_on_top = True

    readonly_fields = (
        "image_preview",
        "created_at",
    )

    fieldsets = (
        (
            "Project Information",
            {
                "fields": (
                    "title",
                    "subtitle",
                    "description",
                    "role",
                ),
            },
        ),
        (
            "Project Media",
            {
                "fields": (
                    "image",
                    "image_preview",
                ),
            },
        ),
        (
            "Technology & Status",
            {
                "fields": (
                    "tech_stack",
                    "status",
                    "is_published",
                    "order",
                ),
            },
        ),
        (
            "Project Links",
            {
                "fields": (
                    "github_url",
                    "live_url",
                ),
            },
        ),
        (
            "System Information",
            {
                "classes": ("collapse",),
                "fields": ("created_at",),
            },
        ),
    )

    actions = (
        "publish_selected",
        "unpublish_selected",
    )

    # -----------------------------------------------------
    # Image Preview
    # -----------------------------------------------------


    @admin.display(description="Project Preview")
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" alt="{}" '
                'style="width:112px;height:72px;'
                "object-fit:cover;border-radius:8px;"
                'border:1px solid #334155;" />',
                obj.image.url,
                obj.title,
            )

        return "No image uploaded"

    # -----------------------------------------------------
    # Bulk Publish / Unpublish
    # -----------------------------------------------------

    @admin.action(
        description="Publish selected projects",
        permissions=("change",),
    )
    def publish_selected(self, request, queryset):
        updated = queryset.update(is_published=True)

        self.message_user(
            request,
            f"{updated} project(s) published successfully.",
            level=messages.SUCCESS,
        )

    @admin.action(
        description="Unpublish selected projects",
        permissions=("change",),
    )
    def unpublish_selected(self, request, queryset):
        updated = queryset.update(is_published=False)

        self.message_user(
            request,
            f"{updated} project(s) moved to drafts.",
            level=messages.SUCCESS,
        )

    # -----------------------------------------------------
    # Safe Image Cleanup
    # -----------------------------------------------------

    @staticmethod
    def delete_image_if_unused(storage, image_name):
        if not image_name:
            return

        try:
            # Keep the file if another project still uses it.
            image_is_used = Project.objects.filter(
                image=image_name
            ).exists()

            if not image_is_used:
                storage.delete(image_name)

        except Exception:
            logger.exception(
                "Could not delete unused project image: %s",
                image_name,
            )

    # Clean up the old image when replacing or removing it.
    def save_model(self, request, obj, form, change):
        old_image = None

        if change and obj.pk:
            previous = (
                Project.objects
                .filter(pk=obj.pk)
                .only("image")
                .first()
            )

            if previous and previous.image:
                new_image_name = obj.image.name if obj.image else ""

                if previous.image.name != new_image_name:
                    old_image = (
                        previous.image.storage,
                        previous.image.name,
                    )

        super().save_model(request, obj, form, change)

        if old_image:
            transaction.on_commit(
                partial(self.delete_image_if_unused, *old_image)
            )


# =========================================================
# CONTACT MESSAGES
# =========================================================


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "short_message", "created_at", "is_read")
    list_editable = ("is_read",)
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "message")
    date_hierarchy = "created_at"
    readonly_fields = ("name", "email", "subject", "message", "created_at")
    fields = ("name", "email", "subject", "message", "created_at", "is_read")
    actions = ("mark_read", "mark_unread")

    # Messages come from the public form only.
    def has_add_permission(self, request):
        return False

    @admin.display(description="Message")
    def short_message(self, obj):
        return obj.message if len(obj.message) <= 70 else f"{obj.message[:67]}..."

    @admin.action(description="Mark selected as read", permissions=("change",))
    def mark_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} message(s) marked as read.", messages.SUCCESS)

    @admin.action(description="Mark selected as unread", permissions=("change",))
    def mark_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} message(s) marked as unread.", messages.SUCCESS)


# =========================================================
# ADMIN SITE BRANDING
# =========================================================

admin.site.site_header = (
    "Abdulrahman Hasanen | Portfolio Administration"
)

admin.site.site_title = "Portfolio Admin"

admin.site.index_title = "Manage Your Portfolio"
