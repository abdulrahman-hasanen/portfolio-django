from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.views.static import serve

from core.sitemaps import StaticViewSitemap
from core.views import about, contact, home, resources

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("about/", about, name="about"),
    path("resources/", resources, name="resources"),
    path("contact/", contact, name="contact"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"static": StaticViewSitemap}},
        name="sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
]

if settings.SERVE_MEDIA:
    urlpatterns += [
        re_path(
            r"^%s(?P<path>.*)$" % settings.MEDIA_URL.lstrip("/"),
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

handler404 = "core.views.not_found"
handler500 = "core.views.server_error"
