import logging

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ContactForm
from .models import Project

logger = logging.getLogger(__name__)


def home(request):
    projects = Project.objects.filter(is_published=True)[:3]
    return render(request, "pages/index.html", {"projects": projects})


def about(request):
    projects = Project.objects.filter(is_published=True)
    return render(request, "pages/about.html", {"projects": projects})


def resources(request):
    return render(request, "pages/resources.html")


def _client_ip(request):
    return request.META.get("REMOTE_ADDR", "unknown")


def _rate_limited(request):
    key = f"contact-rate:{_client_ip(request)}"
    count = cache.get(key, 0)
    if count >= settings.CONTACT_RATE_LIMIT:
        return True
    cache.set(key, count + 1, 60 * 60)
    return False


def _respond(request, ok, message, status=200, errors=None):
    wants_json = request.headers.get("x-requested-with") == "XMLHttpRequest"
    if wants_json:
        payload = {"ok": ok, "message": message}
        if errors:
            payload["errors"] = errors
        return JsonResponse(payload, status=status)

    from django.contrib import messages

    (messages.success if ok else messages.error)(request, message)
    return redirect(f"{reverse('home')}#contact")


@require_POST
def contact(request):
    form = ContactForm(request.POST)

    if not form.is_valid():
        errors = {field: errs[0] for field, errs in form.errors.items()}
        first = next(iter(errors.values()), "Please check the form and try again.")
        return _respond(request, False, first, status=400, errors=errors)

    if form.is_spam():
        # Pretend success so bots learn nothing; store nothing.
        return _respond(request, True, "Thanks! Your message has been sent.")

    if _rate_limited(request):
        return _respond(
            request, False, "Too many messages. Please try again later.", status=429
        )

    contact_message = form.save()

    if settings.CONTACT_NOTIFY_EMAIL:
        try:
            send_mail(
                subject=f"[Portfolio] New message from {contact_message.name}",
                message=(
                    f"Name: {contact_message.name}\n"
                    f"Email: {contact_message.email}\n\n"
                    f"{contact_message.message}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_NOTIFY_EMAIL],
            )
        except Exception:
            logger.exception("Could not send contact notification email")

    return _respond(request, True, "Thanks! Your message has been sent.")


def not_found(request, exception):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)
