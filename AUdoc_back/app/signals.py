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
    is_verified = False

    # Student OTP login flow.
    if request.session.get("otp_login_verified", False):
        is_verified = True
        del request.session["otp_login_verified"]

    # Successful Google OAuth login flow.
    elif request.session.get("social_login_verified", False):
        is_verified = True
        del request.session["social_login_verified"]

    # Staff/doctor credential login flow (staff_id + password or Django auth for staff accounts).
    elif user.is_staff:
        is_verified = True

    LoginLog.objects.create(
        user=user,
        username=user.username,
        date=now.date(),
        time=now.time(),
        ip_address=_get_client_ip(request),
        is_verified=is_verified,
    )
