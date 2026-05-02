from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import StudentProfile
from .security import log_security_event


class GoogleStudentSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter for Google OAuth - validates and auto-approves registered students."""

    def pre_social_login(self, request, sociallogin):
        """Called before social login is processed. Validate student and prevent signup form."""
        email = sociallogin.account.extra_data.get("email", "")
        google_id = sociallogin.account.extra_data.get("sub", "")

        if not email:
            raise Exception("Google email not provided")

        try:
            user = User.objects.get(email=email)
            profile = user.student_profile

            if not profile.is_verified:
                raise Exception("Your student account has not been approved yet. Please wait for admin approval.")

            # Update oauth info
            profile.oauth_id = google_id
            profile.oauth_provider = "google"
            profile.save()
            log_security_event("google_login_success", request, {"email": email}, level="info")

            # Connect the social account to existing user
            sociallogin.user = user

        except (User.DoesNotExist, StudentProfile.DoesNotExist):
            raise Exception("Your email is not registered as a student. Please register first and wait for approval.")

    def save_user(self, request, sociallogin, form=None):
        """Override to skip the signup form for validated students."""
        # If we reach here, pre_social_login passed and user should be set
        # Just return the already-connected user without showing a form
        return sociallogin.user
