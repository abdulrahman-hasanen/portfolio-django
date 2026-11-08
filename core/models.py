from django.db import models

from .images import to_webp, validate_image_size


class Project(models.Model):
    STATUS_CHOICES = [
        ("Done", "Completed"),
        ("Active", "In Progress"),
        ("Ongoing", "Ongoing"),
    ]

    title = models.CharField(max_length=200, verbose_name="Project Title")
    subtitle = models.CharField(max_length=300, verbose_name="Short Description")
    role = models.CharField(
        max_length=100, default="Front-End", verbose_name="Role (e.g. Full-Stack)"
    )
    tech_stack = models.CharField(
        max_length=150, verbose_name="Tech Stack (e.g. Django / MySQL)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Done")

    github_url = models.URLField(blank=True, null=True, verbose_name="GitHub URL")
    live_url = models.URLField(blank=True, null=True, verbose_name="Live Demo URL")

    description = models.TextField(blank=True, verbose_name="Detailed Description")

    image = models.ImageField(
        upload_to="projects/",
        blank=True,
        null=True,
        verbose_name="Project Screenshot",
        validators=[validate_image_size],
    )

    is_published = models.BooleanField(default=True, verbose_name="Published")

    order = models.PositiveIntegerField(default=0, verbose_name="Order Priority")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Newly uploaded screenshots are resized and stored as WebP.
        # Already-saved files (committed) are left untouched.
        if self.image and not getattr(self.image, "_committed", True):
            try:
                self.image.file.seek(0)
                new_name, content = to_webp(self.image.file, self.image.name)
            except Exception:
                pass  # not processable: keep the original upload
            else:
                self.image.save(new_name, content, save=False)
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField(max_length=1200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.created_at:%Y-%m-%d}"
