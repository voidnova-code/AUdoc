from django.shortcuts import render

EXEMPT_PATH_PREFIXES = (
    "/accounts/",     # so a logged-out admin can still reach the login page
    "/static/", "/media/", "/favicon.ico", "/robots.txt", "/sitemap.xml",
    "/restore-site/",  # the no-login-required restore link from §5.3 — must stay reachable even while "down"
)

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from .models import SiteMaintenance

        if SiteMaintenance.is_currently_active():
            user = getattr(request, "user", None)
            is_staff_user = bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))

            if not is_staff_user:
                if user and user.is_authenticated:
                    from django.contrib.auth import logout
                    logout(request)  # force-logout — session only, no data touched

                if not request.path.startswith(EXEMPT_PATH_PREFIXES):
                    maintenance = SiteMaintenance.get_solo()
                    response = render(request, "app/maintenance.html", {
                        "custom_message": maintenance.message,
                    }, status=503)
                    response["Retry-After"] = "1800"
                    return response

        return self.get_response(request)
