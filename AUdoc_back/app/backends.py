from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from .models import StudentProfile


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
