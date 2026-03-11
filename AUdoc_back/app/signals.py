from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone


def _get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    from .models import LoginLog

    # Skip logging for superusers / admin accounts
    if user.is_superuser:
        return

    now = timezone.localtime(timezone.now())
    is_verified = bool(request.session.get("otp_login_verified", False))
    if is_verified:
        del request.session["otp_login_verified"]

    LoginLog.objects.create(
        user=user,
        username=user.username,
        date=now.date(),
        time=now.time(),
        ip_address=_get_client_ip(request),
        is_verified=is_verified,
    )
