from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

from .models import StudentProfile, StaffProfile


class StudentIDBackend(BaseBackend):
    """
    Allows students to log in using only their Student ID — no password needed.
    Only succeeds when the ID matches an existing StudentProfile.
    Staff and admin are not affected (they have no StudentProfile).
    """

    def authenticate(self, request, username=None, **kwargs):
        try:
            profile = StudentProfile.objects.select_related("user").get(
                student_id=username
            )
            return profile.user
        except StudentProfile.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class StaffIDBackend(BaseBackend):
    """
    Allows staff/doctors to log in using their staff_id and password.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            staff = StaffProfile.objects.get(staff_id=username)
            if check_password(password, staff.password):
                # Get or create User account for the staff
                user, created = User.objects.get_or_create(
                    username=staff.staff_id,
                    defaults={
                        'email': staff.email,
                        'first_name': staff.name.split()[0] if staff.name else '',
                        'last_name': ' '.join(staff.name.split()[1:]) if len(staff.name.split()) > 1 else '',
                    }
                )
                return user
        except StaffProfile.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class GoogleStudentBackend(BaseBackend):
    """
    Authenticate students via Google OAuth.
    - Only allows approved (is_verified=True) students
    - Email must match the registered StudentProfile email exactly
    - Stores oauth_id for future logins
    """

    def authenticate(self, request, email=None, oauth_id=None, **kwargs):
        if not email:
            return None
        try:
            user = User.objects.get(email=email)
            profile = user.student_profile
            if not profile.is_verified:
                return None
            profile.oauth_id = oauth_id
            profile.oauth_provider = "google"
            profile.save()
            return user
        except (User.DoesNotExist, StudentProfile.DoesNotExist):
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
