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
    path("donation/create-order/", views.donation_create_order, name="donation_create_order"),
    path("donation/verify-payment/", views.donation_verify_payment, name="donation_verify_payment"),
    path("blood-bank/", views.blood_bank, name="blood_bank"),
    path("blood-donors/", views.blood_donors_list, name="blood_donors_list"),
    path("blood/respond/<uuid:token>/<str:action>/", views.donor_respond, name="donor_respond"),
    path("appointment/confirm/<uuid:token>/<str:action>/", views.appointment_confirm, name="appointment_confirm"),
    path("about/", views.about, name="about"),

    # ── post-login redirect ──────────────────────────────────────
    path("post-login/", views.post_login_redirect, name="post_login"),

    # ── custom admin panel ───────────────────────────────────────
    path("manage/", views.admin_dashboard, name="admin_dashboard"),
    path("manage/stats/", views.admin_dashboard_stats, name="admin_dashboard_stats"),
    path("manage/chart-data/", views.admin_chart_data, name="admin_chart_data"),
    path("manage/registration/<int:pk>/action/", views.admin_registration_action, name="admin_registration_action"),
    path("manage/appointment/<int:pk>/status/", views.admin_appointment_status, name="admin_appointment_status"),
    path("manage/blood-donation/<int:pk>/status/", views.admin_blood_donation_status, name="admin_blood_donation_status"),
    path("manage/blood-request/<int:pk>/status/", views.admin_blood_request_status, name="admin_blood_request_status"),
    path("manage/donation/<int:pk>/toggle-paid/", views.admin_donation_toggle_paid, name="admin_donation_toggle_paid"),
    path("manage/doctor/save/", views.admin_doctor_save, name="admin_doctor_save"),
    path("manage/doctor/<int:pk>/delete/", views.admin_doctor_delete, name="admin_doctor_delete"),
    path("manage/clear-all-data/", views.admin_clear_all_data, name="admin_clear_all_data"),
    path("manage/staff/save/", views.admin_staff_save, name="admin_staff_save"),
    path("manage/staff/<int:pk>/delete/", views.admin_staff_delete, name="admin_staff_delete"),

    # ── AI Chatbot ───────────────────────────────────────────────
    path("chat/", views.chat_api, name="chat_api"),

    # ── Flutter App REST API ─────────────────────────────────────
    path("api/send-login-otp/", views.api_send_login_otp, name="api_send_login_otp"),
    path("api/student-login/", views.api_student_login, name="api_student_login"),
    path("api/send-register-otp/", views.api_send_register_otp, name="api_send_register_otp"),
    path("api/register/", views.api_register, name="api_register"),
    path("api/doctors/", views.api_doctors, name="api_doctors"),
    path("api/appointments/", views.api_appointments, name="api_appointments"),
    path("api/blood-donations/", views.api_blood_donations, name="api_blood_donations"),
    path("api/blood-requests/", views.api_blood_requests, name="api_blood_requests"),
    path("api/profile/", views.api_profile, name="api_profile"),
    path("api/logout/", views.api_logout, name="api_logout"),
]
