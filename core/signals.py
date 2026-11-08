from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Project


@receiver(
    post_delete,
    sender=Project,
    dispatch_uid="core.delete_project_image",
)
def delete_project_image(sender, instance, using, **kwargs):
    """
    Delete a project's image after the database deletion
    has successfully committed.

    The image is preserved if another Project still uses it.
    """

    if not instance.image:
        return

    image_name = instance.image.name
    storage = instance.image.storage

    if not image_name:
        return

    def delete_image_if_unused():
        image_is_used = Project.objects.using(using).filter(image=image_name).exists()

        if not image_is_used:
            storage.delete(image_name)

    transaction.on_commit(
        delete_image_if_unused,
        using=using,
    )
