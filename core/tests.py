import shutil
import tempfile
from io import BytesIO

from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import ContactMessage, Project

TMP_MEDIA = tempfile.mkdtemp()


def make_png(size=(40, 30), name="shot.png"):
    buffer = BytesIO()
    Image.new("RGB", size, (30, 60, 140)).save(buffer, "PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def make_project(**kwargs):
    defaults = dict(title="P", subtitle="s", tech_stack="Django")
    defaults.update(kwargs)
    return Project.objects.create(**defaults)


@override_settings(SECURE_SSL_REDIRECT=False)
class PageTests(TestCase):
    def test_pages_render(self):
        for name in ("home", "about", "resources"):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_unpublished_projects_are_hidden(self):
        make_project(title="Visible Project")
        make_project(title="Secret Draft", is_published=False)
        for name in ("home", "about"):
            html = self.client.get(reverse(name)).content.decode()
            self.assertIn("Visible Project", html)
            self.assertNotIn("Secret Draft", html)

    def test_home_shows_three_and_respects_order(self):
        for i in range(5):
            make_project(title=f"Proj{i}", order=10 - i)
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn("Proj4", html)   # order=6, lowest -> first
        self.assertNotIn("Proj0", html)  # order=10, cut by [:3]

    def test_pages_have_seo_meta(self):
        html = self.client.get(reverse("home")).content.decode()
        for needle in ('name="description"', 'property="og:title"', 'rel="canonical"', "application/ld+json"):
            self.assertIn(needle, html)

    def test_no_placeholder_links(self):
        html = self.client.get(reverse("home")).content.decode()
        self.assertNotIn("YOUR_", html)

    def test_nav_marks_current_page(self):
        html = self.client.get(reverse("about")).content.decode()
        self.assertIn('aria-current="page"', html)

    def test_404_uses_custom_template(self):
        response = self.client.get("/does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page not found", status_code=404)

    def test_robots_and_sitemap(self):
        self.assertContains(self.client.get("/robots.txt"), "Sitemap:")
        self.assertContains(self.client.get("/sitemap.xml"), "<urlset")


@override_settings(SECURE_SSL_REDIRECT=False)
class ContactFormTests(TestCase):
    url = "/contact/"
    valid = {"name": "Sara", "email": "sara@example.com", "message": "Hello, I like your work."}

    def setUp(self):
        cache.clear()

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_valid_post_is_stored_and_redirects(self):
        response = self.client.post(self.url, self.valid)
        self.assertRedirects(response, "/#contact", fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_ajax_success_json(self):
        response = self.client.post(self.url, self.valid, headers={"x-requested-with": "XMLHttpRequest"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])

    def test_invalid_post_rejected(self):
        response = self.client.post(
            self.url, {"name": "S", "email": "nope", "message": "short"},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_honeypot_discards_silently(self):
        response = self.client.post(
            self.url, {**self.valid, "website": "http://spam"},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        self.assertTrue(response.json()["ok"])
        self.assertEqual(ContactMessage.objects.count(), 0)

    @override_settings(CONTACT_RATE_LIMIT=2)
    def test_rate_limit(self):
        ajax = {"x-requested-with": "XMLHttpRequest"}
        for _ in range(2):
            self.assertEqual(self.client.post(self.url, self.valid, headers=ajax).status_code, 200)
        self.assertEqual(self.client.post(self.url, self.valid, headers=ajax).status_code, 429)
        self.assertEqual(ContactMessage.objects.count(), 2)

    @override_settings(
        CONTACT_NOTIFY_EMAIL="me@example.com",
        MAILERS={"default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}},
    )
    def test_notification_email_sent(self):
        self.client.post(self.url, self.valid)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Sara", mail.outbox[0].subject)

    def test_message_visible_after_redirect(self):
        response = self.client.post(self.url, self.valid, follow=True)
        self.assertContains(response, "Your message has been sent")


@override_settings(MEDIA_ROOT=TMP_MEDIA, SECURE_SSL_REDIRECT=False)
class ProjectImageTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def test_upload_converted_to_webp(self):
        project = make_project(image=make_png())
        self.assertTrue(project.image.name.endswith(".webp"))

    def test_large_image_is_downscaled(self):
        project = make_project(image=make_png(size=(3000, 1000)))
        with Image.open(project.image.path) as img:
            self.assertEqual(img.width, 1600)

    def test_image_deleted_with_project(self):
        project = make_project(image=make_png())
        path = project.image.path
        with self.captureOnCommitCallbacks(execute=True):
            project.delete()
        import os
        self.assertFalse(os.path.exists(path))

    def test_shared_image_kept_while_in_use(self):
        first = make_project(title="A", image=make_png())
        second = make_project(title="B")
        Project.objects.filter(pk=second.pk).update(image=first.image.name)
        with self.captureOnCommitCallbacks(execute=True):
            first.delete()
        import os
        self.assertTrue(os.path.exists(os.path.join(TMP_MEDIA, first.image.name)))
