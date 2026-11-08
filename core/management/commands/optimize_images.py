"""Convert existing project screenshots to resized WebP.

Usage:  python manage.py optimize_images [--dry-run]
Updates Project.image to the new file and deletes the old one when no other
project references it.
"""

from django.core.management.base import BaseCommand

from core.images import to_webp
from core.models import Project


class Command(BaseCommand):
    help = "Convert existing project images to optimised WebP."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry = options["dry_run"]
        for project in Project.objects.exclude(image="").exclude(image__isnull=True):
            old_name = project.image.name
            if old_name.lower().endswith(".webp"):
                self.stdout.write(f"skip   {old_name} (already WebP)")
                continue
            storage = project.image.storage
            try:
                with storage.open(old_name) as source:
                    old_size = storage.size(old_name)
                    new_name, content = to_webp(source, old_name)
            except Exception as exc:  # missing or unreadable file
                self.stderr.write(f"error  {old_name}: {exc}")
                continue
            self.stdout.write(
                f"{'would convert' if dry else 'convert'} {old_name} "
                f"({old_size // 1024} KB) -> {new_name} ({content.size // 1024} KB)"
            )
            if dry:
                continue
            saved_name = storage.save(f"projects/{new_name}", content)
            Project.objects.filter(pk=project.pk).update(image=saved_name)
            if not Project.objects.filter(image=old_name).exists():
                storage.delete(old_name)
