from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("student-login/", views.student_login, name="student_login"),
    path("send-otp/", views.send_otp, name="send_otp"),
    path("send-login-otp/", views.send_login_otp, name="send_login_otp"),
    path("appointment/", views.appointment, name="appointment"),
    path("donation/", views.donation, name="donation"),
    path("blood-bank/", views.blood_bank, name="blood_bank"),
    path("blood-donors/", views.blood_donors_list, name="blood_donors_list"),
    path("blood-donors/<int:donor_id>/request/", views.request_blood_from_donor, name="request_blood_from_donor"),
]
