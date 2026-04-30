import json
import os
import time
import razorpay
import logging
import threading
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q, Case, When, Value, IntegerField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .forms import AppointmentForm, BloodDonationForm, BloodRequestForm, DonationForm, HelpDeskForm, StudentRegistrationForm
from .models import Appointment, BloodDonation, BloodRequest, Doctor, Donation, DonorResponse, HelpDesk, LoginLog, StaffProfile, StudentProfile, StudentRegistration, TodaysAppointment, DoctorLeave, TIME_SLOT_CHOICES, BLOOD_GROUP_CHOICES, DAY_CHOICES, MEDICAL_DEPT_CHOICES
from .security import (
    generate_secure_otp,
    constant_time_compare,
    rate_limit_otp,
    rate_limit_login,
    rate_limit_api,
    get_client_ip,
    log_failed_login,
    log_security_event,
    sanitize_string,
    validate_student_id,
    validate_email_format,
)

logger = logging.getLogger(__name__)


def send_email_async(email_msg):
    """Send email in background thread to prevent blocking on SMTP timeout."""
    def _send():
        try:
            logger.info(f"🔄 [Async] Sending email in background thread...")
            email_msg.send(fail_silently=False)
            logger.info(f"✅ [Async] Email sent successfully")
        except Exception as e:
            logger.error(f"❌ [Async] Failed to send email: {str(e)}")

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
    logger.info(f"🧵 [Async] Email thread started (daemon)")



def about(request):
    if request.method == "POST":
        form = HelpDeskForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            feedback = HelpDesk.objects.create(
                name=cd["name"],
                stars=cd["stars"],
                message=cd.get("message", ""),
            )
            return render(request, "app/about.html", {"submitted": True, "stars": feedback.stars})
    else:
        form = HelpDeskForm()
    return render(request, "app/about.html", {"form": form, "submitted": False})


def student_login(request):
    if request.method == "POST":
        student_id  = sanitize_string(request.POST.get("student_id", ""), max_length=50)
        otp_entered = sanitize_string(request.POST.get("otp", ""), max_length=10)
        otp_data    = request.session.get("login_otp_data", {})

        # Validate student_id format
        if not validate_student_id(student_id):
            log_failed_login(request, student_id, "invalid_format")
            messages.error(request, "Invalid Student ID format.")
            return redirect("/accounts/login/")

        if not otp_entered:
            messages.error(request, "Please verify your Student ID with OTP before logging in.")
            return redirect("/accounts/login/")
        if otp_data.get("student_id") != student_id:
            log_failed_login(request, student_id, "otp_mismatch_student_id")
            messages.error(request, "OTP was sent for a different Student ID. Please re-send.")
            return redirect("/accounts/login/")
        if time.time() > otp_data.get("expires", 0):
            log_failed_login(request, student_id, "otp_expired")
            messages.error(request, "Your OTP has expired. Please request a new one.")
            return redirect("/accounts/login/")
        # Use constant-time comparison to prevent timing attacks
        if not constant_time_compare(otp_data.get("otp", ""), otp_entered):
            log_failed_login(request, student_id, "otp_incorrect")
            messages.error(request, "Incorrect OTP. Please check your email and try again.")
            return redirect("/accounts/login/")

        del request.session["login_otp_data"]
        user = authenticate(request, username=student_id)
        if user is not None:
            request.session["otp_login_verified"] = True
            login(request, user, backend="app.backends.StudentIDBackend")
            log_security_event("successful_login", request, {"student_id": student_id}, level="info")
            return redirect("/")
        log_failed_login(request, student_id, "user_not_found")
        messages.error(request, "Student ID not found or not yet approved. Please check and try again.")
    return redirect("/accounts/login/")


@rate_limit_otp
@require_POST
def send_login_otp(request):
    student_id = sanitize_string(request.POST.get("student_id", ""), max_length=50)
    
    # Validate student_id format
    if not student_id or not validate_student_id(student_id):
        return JsonResponse({"error": "Please enter a valid Student ID."}, status=400)

    try:
        user = User.objects.get(username=student_id)
    except User.DoesNotExist:
        # Return generic error to prevent user enumeration
        return JsonResponse({"error": "If this Student ID exists, an OTP will be sent."}, status=200)

    email = user.email
    if not email:
        return JsonResponse({"error": "No email on file. Please contact health@au.edu."}, status=400)

    otp = generate_secure_otp(6)
    request.session["login_otp_data"] = {
        "student_id": student_id,
        "otp":        otp,
        "expires":    time.time() + 600,
    }

    plain_text = (
        "Hi {name}!\n\n"
        "Your AUdoc login verification code is: {otp}\n\n"
        "This code is valid for 10 minutes.\n\n"
        "If you did not try to log in, please ignore this email.\n\n"
        "-- The AUdoc Team"
    ).format(name=user.first_name or student_id, otp=otp)

    html_body = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
</head>
<body style="margin:0;padding:0;background:#e8f0fe;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#e8f0fe;padding:40px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(26,92,150,.18);">

        <tr>
          <td style="background:linear-gradient(135deg,#1a5c96 0%,#134a7a 100%);padding:36px 40px;text-align:center;">
            <div style="display:inline-block;background:rgba(255,255,255,.15);border-radius:14px;padding:12px 18px;margin-bottom:14px;">
              <span style="font-size:2rem;">&#128274;</span>
            </div>
            <h1 style="margin:0;color:#ffffff;font-size:1.6rem;font-weight:700;letter-spacing:-.5px;">AUdoc Campus Health</h1>
            <p style="margin:6px 0 0;color:#c0d8f0;font-size:.9rem;">Login Verification</p>
          </td>
        </tr>

        <tr>
          <td style="padding:40px 40px 32px;">
            <p style="margin:0 0 8px;font-size:1.5rem;">&#128075; Hey, {name}!</p>
            <p style="margin:0 0 24px;color:#555;font-size:.97rem;line-height:1.6;">
              Someone (hopefully you &#128521;) is trying to log in to
              <strong style="color:#1a5c96;">AUdoc Campus Health</strong>
              using Student ID <strong style="font-family:'Courier New',monospace;">{sid}</strong>.
              Here is your one-time login code:
            </p>

            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td align="center" style="padding:8px 0 28px;">
                  <div style="display:inline-block;background:linear-gradient(135deg,#eef4ff,#ddeaff);border:2px dashed #1a5c96;border-radius:16px;padding:28px 48px;text-align:center;">
                    <p style="margin:0 0 6px;font-size:.78rem;text-transform:uppercase;letter-spacing:2px;color:#1a5c96;font-weight:700;">Your Login OTP</p>
                    <p style="margin:0;font-size:2.8rem;font-weight:800;letter-spacing:10px;color:#134a7a;font-family:'Courier New',monospace;">{otp}</p>
                  </div>
                </td>
              </tr>
            </table>

            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
              <tr>
                <td style="background:#fff8e1;border-left:4px solid #f9a825;border-radius:0 10px 10px 0;padding:14px 16px;">
                  <p style="margin:0;font-size:.88rem;color:#7a5800;">
                    &#9200; This code expires in <strong>10 minutes</strong>.
                    After that it turns into a pumpkin &#127814;
                    (well, it just stops working &mdash; but you get the idea).
                  </p>
                </td>
              </tr>
            </table>

            <p style="margin:0;color:#777;font-size:.85rem;line-height:1.6;">
              &#128274; If you did <strong>not</strong> try to log in, please ignore this email.
              No doctors were harmed in the sending of this message. &#128522;
            </p>
          </td>
        </tr>

        <tr>
          <td style="background:#f4f8fc;padding:20px 40px;text-align:center;border-top:1px solid #e5edf5;">
            <p style="margin:0;font-size:.8rem;color:#999;">
              &#169; 2026 <strong style="color:#1a5c96;">AUdoc</strong> &mdash; Assam University Silchar Campus Health<br/>
              Academic Block C, Room 101 &nbsp;|&nbsp; health@au.edu
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>""".replace("{otp}", otp).replace("{name}", user.first_name or student_id).replace("{sid}", student_id)

    try:
        msg = EmailMultiAlternatives(
            subject="🔐 Your AUdoc Login Verification Code",
            body=plain_text,
            from_email=None,
            to=[email],
        )
        msg.attach_alternative(html_body, "text/html")
        send_email_async(msg)
        at      = email.index("@")
        masked  = email[:2] + ("*" * (at - 2)) + email[at:]
        return JsonResponse({"success": True, "email": masked})
    except Exception as e:
        return JsonResponse({"error": "Could not send email: " + str(e)}, status=500)


@rate_limit_otp
@require_POST
def send_otp(request):
    email = sanitize_string(request.POST.get("email", ""), max_length=254)

    if not email or not validate_email_format(email):
        return JsonResponse({"error": "Please enter a valid email address."}, status=400)

    if StudentRegistration.objects.filter(email=email).exists():
        return JsonResponse({"error": "This email is already registered."}, status=400)

    otp = generate_secure_otp(6)
    request.session["otp_data"] = {
        "email": email,
        "otp":   otp,
        "expires": time.time() + 600,   # valid for 10 minutes
    }

    plain_text = (
        "Your AUdoc email verification code is: {otp}\n\n"
        "This code is valid for 10 minutes.\n\n"
        "If you did not request this, you can safely ignore this email.\n\n"
        "-- The AUdoc Team"
    ).format(otp=otp)

    html_body = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
</head>
<body style="margin:0;padding:0;background:#e8f0fe;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#e8f0fe;padding:40px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(26,92,150,.18);">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a5c96 0%,#134a7a 100%);padding:36px 40px;text-align:center;">
            <div style="display:inline-block;background:rgba(255,255,255,.15);border-radius:14px;padding:12px 18px;margin-bottom:14px;">
              <span style="font-size:2rem;">&#127973;</span>
            </div>
            <h1 style="margin:0;color:#ffffff;font-size:1.6rem;font-weight:700;letter-spacing:-.5px;">AUdoc Campus Health</h1>
            <p style="margin:6px 0 0;color:#c0d8f0;font-size:.9rem;">Email Verification</p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:40px 40px 32px;">
            <p style="margin:0 0 8px;font-size:1.5rem;">&#128075; Hey there!</p>
            <p style="margin:0 0 24px;color:#555;font-size:.97rem;line-height:1.6;">
              Someone (hopefully you &#128521;) just asked to verify this email address for
              <strong style="color:#1a5c96;">AUdoc Campus Health</strong>.
              Here is your one-time verification code:
            </p>

            <!-- OTP box -->
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td align="center" style="padding:8px 0 28px;">
                  <div style="display:inline-block;background:linear-gradient(135deg,#eef4ff,#ddeaff);border:2px dashed #1a5c96;border-radius:16px;padding:28px 48px;text-align:center;">
                    <p style="margin:0 0 6px;font-size:.78rem;text-transform:uppercase;letter-spacing:2px;color:#1a5c96;font-weight:700;">Your OTP Code</p>
                    <p style="margin:0;font-size:2.8rem;font-weight:800;letter-spacing:10px;color:#134a7a;font-family:'Courier New',monospace;">{otp}</p>
                  </div>
                </td>
              </tr>
            </table>

            <!-- Timer info -->
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
              <tr>
                <td style="background:#fff8e1;border-left:4px solid #f9a825;border-radius:0 10px 10px 0;padding:14px 16px;">
                  <p style="margin:0;font-size:.88rem;color:#7a5800;">
                    &#9200; This code expires in <strong>10 minutes</strong>.
                    After that it turns into a pumpkin &#127814;
                    (well, it just stops working &mdash; but you get the idea).
                  </p>
                </td>
              </tr>
            </table>

            <p style="margin:0;color:#777;font-size:.85rem;line-height:1.6;">
              &#128274; If you did <strong>not</strong> request this, you can safely ignore this email.
              No doctors were harmed in the sending of this message. &#128522;
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f4f8fc;padding:20px 40px;text-align:center;border-top:1px solid #e5edf5;">
            <p style="margin:0;font-size:.8rem;color:#999;">
              &#169; 2026 <strong style="color:#1a5c96;">AUdoc</strong> &mdash; Assam University Silchar Campus Health<br/>
              Academic Block C, Room 101 &nbsp;|&nbsp; health@au.edu
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>""".replace("{otp}", otp)

    try:
        msg = EmailMultiAlternatives(
            subject="🔐 Your AUdoc Email Verification Code",
            body=plain_text,
            from_email=None,
            to=[email],
        )
        msg.attach_alternative(html_body, "text/html")
        send_email_async(msg)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": "Could not send email: " + str(e)}, status=500)


def register(request):
    form = StudentRegistrationForm(request.POST or None)
    otp_error = None

    if request.method == "POST" and form.is_valid():
        email       = form.cleaned_data["email"]
        otp_entered = sanitize_string(request.POST.get("otp", ""), max_length=10)
        otp_data    = request.session.get("otp_data", {})

        if not otp_entered:
            otp_error = "Please verify your email before submitting."
        elif otp_data.get("email") != email:
            otp_error = "OTP was sent to a different email. Please re-verify."
        elif time.time() > otp_data.get("expires", 0):
            otp_error = "Your OTP has expired. Please request a new one."
        elif not constant_time_compare(otp_data.get("otp", ""), otp_entered):
            otp_error = "Incorrect OTP. Please check your email and try again."
        else:
            # OTP valid — clear it and save registration
            del request.session["otp_data"]
            cd = form.cleaned_data
            StudentRegistration.objects.create(
                first_name=cd["first_name"],
                last_name=cd["last_name"],
                email=cd["email"],
                student_id=cd["student_id"],
                phone=cd["phone"],
                emergency_contact=cd["emergency_contact"],
                department=cd["department"],
                blood_group=cd["blood_group"],
                home_address=cd["home_address"],
                present_address=cd["present_address"],
            )
            messages.success(
                request,
                "Registration submitted successfully! The admin team will review your application.",
            )
            return redirect("register")

    return render(request, "registration/register.html", {
        "form": form,
        "otp_error": otp_error,
    })


def home(request):
    doctors = Doctor.objects.filter(is_available=True).order_by("specialized_in", "name")
    return render(request, "app/home.html", {"doctors": doctors})


@login_required
def appointment(request):
    today = timezone.localtime()
    today_date = today.date()

    # Resolve the student_id for this user
    student_id = None
    initial = {}
    try:
        profile = request.user.student_profile
        student_id = profile.student_id
        initial = {
            "student_id":         profile.student_id,
            "student_name":       request.user.get_full_name(),
            "phone":              profile.phone,
            "email":              request.user.email,
            "student_department": profile.department,
        }
    except Exception:
        pass

    # Auto-complete any past PENDING/CONFIRMED appointments for this student
    if student_id:
        Appointment.objects.filter(
            student_id=student_id,
            appointment_date__lt=today_date,
            status__in=["PENDING", "CONFIRMED"],
        ).update(status="COMPLETED")

    # Check if student is restricted from booking due to no-shows
    restriction_info = {"is_restricted": False}
    if student_id:
        from app.no_show_helper import is_student_restricted_from_booking
        restriction_info = is_student_restricted_from_booking(student_id)

    # Split this user's appointments into upcoming and history
    base_qs = Appointment.objects.filter(student_id=student_id) if student_id else Appointment.objects.none()
    upcoming_appointments = (
        base_qs
        .filter(appointment_date__gte=today_date)
        .exclude(status__in=["REJECTED", "CANCELLED", "COMPLETED"])
        .order_by("appointment_date", "appointment_time")
    )
    history_appointments = (
        base_qs
        .filter(Q(appointment_date__lt=today_date) | Q(status__in=["REJECTED", "CANCELLED", "COMPLETED"]))
        .order_by("-appointment_date", "-appointment_time")
    )

    form = AppointmentForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        # Check restriction again before creating
        if student_id:
            restriction_check = is_student_restricted_from_booking(student_id)
            if restriction_check["is_restricted"]:
                messages.error(request, restriction_check["reason"])
                return redirect("appointment")

        cd = form.cleaned_data
        Appointment.objects.create(
            student_id=cd["student_id"],
            student_name=cd["student_name"],
            phone=cd["phone"],
            email=cd["email"],
            student_department=cd["student_department"],
            medical_department=cd["medical_department"],
            doctor=cd.get("doctor"),
            appointment_date=cd["appointment_date"],
            appointment_time=cd["appointment_time"],
            problem_description=cd["problem_description"],
            status="CONFIRMED",
        )
        messages.success(
            request,
            "Your appointment has been booked and confirmed!",
        )
        return redirect("appointment")

    doctors = Doctor.objects.filter(is_available=True).order_by("specialized_in", "name")
    return render(request, "app/appointment.html", {
        "form": form,
        "doctors": doctors,
        "today_str": today_date.isoformat(),
        "upcoming_appointments": upcoming_appointments,
        "history_appointments": history_appointments,
        "is_restricted": restriction_info["is_restricted"],
        "restriction_reason": restriction_info.get("reason", ""),
        "total_no_shows": restriction_info.get("total_no_shows", 0),
    })


def donation(request):
    form = DonationForm()
    return render(
        request,
        "app/donation.html",
        {
            "form": form,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        },
    )


@require_POST
def donation_create_order(request):
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return JsonResponse(
            {"error": "Payment gateway is not configured. Please contact support."},
            status=500,
        )

    form = DonationForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": form.errors.as_text()}, status=400)

    cd = form.cleaned_data
    amount = cd["amount"]

    student_id, name, email = "", "", ""
    if request.user.is_authenticated:
        try:
            profile = request.user.student_profile
            student_id = profile.student_id
        except Exception:
            pass
        name = request.user.get_full_name()
        email = request.user.email

    razorpay_client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
    amount_paise = int((amount * Decimal("100")).quantize(Decimal("1")))
    order_payload = {
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1,
    }
    razorpay_order = razorpay_client.order.create(data=order_payload)

    donation_obj = Donation.objects.create(
        student_id=student_id,
        name=name,
        email=email,
        amount=amount,
        is_paid=False,
        razorpay_order_id=razorpay_order["id"],
    )

    return JsonResponse(
        {
            "order_id": razorpay_order["id"],
            "amount": amount_paise,
            "currency": "INR",
            "key_id": settings.RAZORPAY_KEY_ID,
            "donation_id": donation_obj.id,
            "donor_name": name,
            "donor_email": email,
            "description": "AUdoc Campus Health Donation",
        }
    )


@require_POST
def donation_verify_payment(request):
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return JsonResponse(
            {"error": "Payment gateway is not configured. Please contact support."},
            status=500,
        )

    donation_id = request.POST.get("donation_id", "").strip()
    razorpay_payment_id = request.POST.get("razorpay_payment_id", "").strip()
    razorpay_order_id = request.POST.get("razorpay_order_id", "").strip()
    razorpay_signature = request.POST.get("razorpay_signature", "").strip()

    if not all([donation_id, razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        return JsonResponse({"error": "Missing payment verification data."}, status=400)

    try:
        donation_obj = Donation.objects.get(pk=int(donation_id))
    except (Donation.DoesNotExist, ValueError):
        return JsonResponse({"error": "Donation record not found."}, status=404)

    if donation_obj.razorpay_order_id != razorpay_order_id:
        return JsonResponse({"error": "Order ID mismatch."}, status=400)

    razorpay_client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
    try:
        razorpay_client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"error": "Payment signature verification failed."}, status=400)

    donation_obj.razorpay_payment_id = razorpay_payment_id
    donation_obj.razorpay_signature = razorpay_signature
    donation_obj.is_paid = True
    donation_obj.save(
        update_fields=["razorpay_payment_id", "razorpay_signature", "is_paid"]
    )

    return JsonResponse({"success": True, "message": "Payment successful."})


def blood_donors_list(request):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect("home")

    blood_group_filter = request.GET.get("blood_group", "")
    donors = BloodDonation.objects.filter(status="APPROVED")
    if blood_group_filter:
        donors = donors.filter(blood_group=blood_group_filter)

    return render(request, "app/blood_donors_list.html", {
        "donors": donors,
        "blood_group_filter": blood_group_filter,
        "blood_groups": BLOOD_GROUP_CHOICES,
    })


def blood_bank(request):
    """Unified Blood Bank page with both donation and request forms."""
    form_donate = BloodDonationForm(request.POST or None)
    form_request = BloodRequestForm(request.POST or None)
    active_tab = request.GET.get("tab", "donate")

    # Check if the logged-in user is already registered as a donor
    existing_donation = None
    blood_requests = []

    # Get initial data for both forms if user is authenticated
    initial_donate = {}
    initial_request = {}
    if request.user.is_authenticated:
        initial_donate = {
            "donor_name": request.user.get_full_name(),
            "email": request.user.email,
        }
        initial_request = {
            "requester_name": request.user.get_full_name(),
            "email": request.user.email,
        }
        try:
            profile = request.user.student_profile
            initial_donate["phone"] = profile.phone
            initial_donate["blood_group"] = profile.blood_group
            initial_request["phone"] = profile.phone
        except Exception:
            pass

        # Check if this user has already registered as a donor
        existing_donation = BloodDonation.objects.filter(email=request.user.email).first()
        if existing_donation:
            urgency_order = Case(
                When(urgency="URGENT", then=Value(1)),
                When(urgency="HIGH",   then=Value(2)),
                When(urgency="MEDIUM", then=Value(3)),
                When(urgency="LOW",    then=Value(4)),
                default=Value(5),
                output_field=IntegerField(),
            )
            blood_requests = (
                BloodRequest.objects
                .filter(status__in=["PENDING", "APPROVED"])
                .annotate(urgency_order=urgency_order)
                .order_by("urgency_order", "required_date")
            )

    if request.method == "GET":
        initial_request["required_date"] = timezone.localdate()
        form_donate = BloodDonationForm(initial=initial_donate)
        form_request = BloodRequestForm(initial=initial_request)

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # Handle donation form submission
        if form_type == "donate" and form_donate.is_valid():
            cd = form_donate.cleaned_data

            # Block duplicate registration
            if BloodDonation.objects.filter(email=cd["email"]).exists():
                messages.error(request, "You have already registered as a blood donor.")
                return redirect("blood_bank")

            # Resolve student_id if user is authenticated
            student_id = ""
            if request.user.is_authenticated:
                try:
                    profile = request.user.student_profile
                    student_id = profile.student_id
                except Exception:
                    pass

            BloodDonation.objects.create(
                student_id=student_id,
                donor_name=cd["donor_name"],
                email=cd["email"],
                phone=cd["phone"],
                blood_group=cd["blood_group"],
                date_of_birth=cd["date_of_birth"],
                weight=cd["weight"],
                previous_donation=cd["previous_donation"],
                health_condition=cd["health_condition"],
                message=cd["message"],
                status="PENDING",
            )
            messages.success(
                request,
                "Thank you for registering as a blood donor! The health center will review your application and contact you soon.",
            )
            return redirect("blood_bank")

        # Handle request form submission
        elif form_type == "request" and form_request.is_valid():
            cd = form_request.cleaned_data

            # Resolve student_id if user is authenticated
            student_id = ""
            if request.user.is_authenticated:
                try:
                    profile = request.user.student_profile
                    student_id = profile.student_id
                except Exception:
                    pass

            blood_req = BloodRequest.objects.create(
                student_id=student_id,
                requester_name=cd["requester_name"],
                email=cd["email"],
                phone=cd["phone"],
                blood_group=cd["blood_group"],
                units_required=cd["units_required"],
                reason=cd["reason"],
                urgency=cd["urgency"],
                required_date=cd["required_date"],
                hospital_name=cd["hospital_name"],
                hospital_contact=cd["hospital_contact"],
                notes=cd["notes"],
                status="PENDING",
            )

            # Notify all approved donors with matching blood group via email
            # Exclude the requester themselves — no point asking someone to donate to themselves
            matching_donors = BloodDonation.objects.filter(
                blood_group=cd["blood_group"], status="APPROVED"
            ).exclude(email=cd["email"])
            for donor in matching_donors:
                dr, _ = DonorResponse.objects.get_or_create(blood_request=blood_req, donor=donor)
                _send_donor_request_email(request, blood_req, donor, dr.token)

            messages.success(
                request,
                "Your blood request has been submitted! Matching donors have been notified by email.",
            )
            return redirect("blood_bank")

        # If form is invalid, set active_tab to show which form had errors
        if form_type == "donate":
            active_tab = "donate"
        elif form_type == "request":
            active_tab = "request"

    return render(request, "app/blood_bank.html", {
        "form_donate":        form_donate,
        "form_request":       form_request,
        "active_tab":         active_tab,
        "existing_donation":  existing_donation,
        "blood_requests":     blood_requests,
    })


def _send_donor_request_email(request, blood_req, donor, token):
    """Send a blood donation request notification email to a single donor."""
    accept_url  = request.build_absolute_uri(
        reverse("donor_respond", args=[str(token), "accept"])
    )
    decline_url = request.build_absolute_uri(
        reverse("donor_respond", args=[str(token), "decline"])
    )

    urgency_colours = {
        "URGENT": "#c41e3a",
        "HIGH":   "#e67e22",
        "MEDIUM": "#f39c12",
        "LOW":    "#27ae60",
    }
    urgency_colour = urgency_colours.get(blood_req.urgency, "#1a5c96")

    plain_text = (
        f"Dear {donor.donor_name},\n\n"
        f"A student at Assam University needs {blood_req.blood_group} blood.\n\n"
        f"Requester : {blood_req.requester_name}\n"
        f"Blood Type: {blood_req.blood_group}\n"
        f"Units     : {blood_req.units_required}\n"
        f"Urgency   : {blood_req.get_urgency_display()}\n"
        f"Needed By : {blood_req.required_date}\n"
        f"Hospital  : {blood_req.hospital_name}\n"
        f"Contact   : {blood_req.hospital_contact}\n\n"
        f"To ACCEPT  : {accept_url}\n"
        f"To DECLINE : {decline_url}\n\n"
        "Your contact details will only be shared with the requester after you accept.\n\n"
        "-- AUdoc Campus Health"
    )

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
</head>
<body style="margin:0;padding:0;background:#fef0f0;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#fef0f0;padding:40px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(196,30,58,.15);">

        <tr>
          <td style="background:linear-gradient(135deg,#c41e3a 0%,#8b0000 100%);padding:36px 40px;text-align:center;">
            <div style="display:inline-block;background:rgba(255,255,255,.15);border-radius:14px;padding:12px 18px;margin-bottom:14px;">
              <span style="font-size:2rem;">&#129656;</span>
            </div>
            <h1 style="margin:0;color:#ffffff;font-size:1.6rem;font-weight:700;">Blood Donation Request</h1>
            <p style="margin:6px 0 0;color:#f5c6cb;font-size:.9rem;">AUdoc Campus Health – Assam University</p>
          </td>
        </tr>

        <tr>
          <td style="padding:36px 40px 28px;">
            <p style="margin:0 0 6px;font-size:1.4rem;">&#128075; Dear {donor.donor_name},</p>
            <p style="margin:0 0 24px;color:#555;font-size:.97rem;line-height:1.6;">
              A fellow student urgently needs <strong style="color:#c41e3a;">{blood_req.blood_group}</strong> blood.
              As a registered donor with the same blood type, you can make a real difference.
            </p>

            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;background:#fff5f5;border-radius:12px;overflow:hidden;border:1px solid #f5c6cb;">
              <tr><td style="padding:20px 24px;">
                <table width="100%" cellpadding="4" cellspacing="0">
                  <tr>
                    <td style="font-size:.85rem;color:#888;width:38%;">Requester</td>
                    <td style="font-size:.92rem;color:#333;font-weight:600;">{blood_req.requester_name}</td>
                  </tr>
                  <tr>
                    <td style="font-size:.85rem;color:#888;">Blood Type Needed</td>
                    <td><span style="background:#c41e3a;color:#fff;padding:3px 12px;border-radius:20px;font-size:.85rem;font-weight:700;">{blood_req.blood_group}</span></td>
                  </tr>
                  <tr>
                    <td style="font-size:.85rem;color:#888;">Units Required</td>
                    <td style="font-size:.92rem;color:#333;font-weight:600;">{blood_req.units_required}</td>
                  </tr>
                  <tr>
                    <td style="font-size:.85rem;color:#888;">Urgency</td>
                    <td><span style="background:{urgency_colour};color:#fff;padding:3px 12px;border-radius:20px;font-size:.85rem;font-weight:700;">{blood_req.get_urgency_display()}</span></td>
                  </tr>
                  <tr>
                    <td style="font-size:.85rem;color:#888;">Date Needed By</td>
                    <td style="font-size:.92rem;color:#333;font-weight:600;">{blood_req.required_date}</td>
                  </tr>
                  <tr>
                    <td style="font-size:.85rem;color:#888;">Hospital</td>
                    <td style="font-size:.92rem;color:#333;font-weight:600;">{blood_req.hospital_name}</td>
                  </tr>
                  <tr>
                    <td style="font-size:.85rem;color:#888;">Hospital Contact</td>
                    <td style="font-size:.92rem;color:#333;font-weight:600;">{blood_req.hospital_contact}</td>
                  </tr>
                </table>
              </td></tr>
            </table>

            <p style="margin:0 0 20px;color:#555;font-size:.9rem;line-height:1.6;">
              Please respond using one of the buttons below. Your personal contact details
              will <strong>not</strong> be visible to anyone — they are kept private at all times.
            </p>

            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
              <tr>
                <td align="center" style="padding-right:8px;">
                  <a href="{accept_url}"
                     style="display:inline-block;background:linear-gradient(135deg,#27ae60,#1e8449);color:#fff;text-decoration:none;padding:14px 32px;border-radius:50px;font-size:1rem;font-weight:700;letter-spacing:.3px;">
                    &#10003;&nbsp; Accept Request
                  </a>
                </td>
                <td align="center" style="padding-left:8px;">
                  <a href="{decline_url}"
                     style="display:inline-block;background:#f8f9fa;color:#555;text-decoration:none;padding:14px 32px;border-radius:50px;font-size:1rem;font-weight:700;border:2px solid #dee2e6;">
                    &#10007;&nbsp; Decline
                  </a>
                </td>
              </tr>
            </table>

            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="background:#e8f5e9;border-left:4px solid #27ae60;border-radius:0 10px 10px 0;padding:14px 16px;">
                  <p style="margin:0;font-size:.85rem;color:#1b5e20;line-height:1.5;">
                    &#128274; <strong>Privacy note:</strong> These links are unique to you.
                    No other user can see your name, phone, or email. Only the health center
                    administration has access to donor records.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <tr>
          <td style="background:#f4f8fc;padding:20px 40px;text-align:center;border-top:1px solid #e5edf5;">
            <p style="margin:0;font-size:.8rem;color:#999;">
              &#169; 2026 <strong style="color:#c41e3a;">AUdoc</strong> &mdash; Assam University Silchar Campus Health<br/>
              Academic Block C, Room 101 &nbsp;|&nbsp; health@au.edu
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    try:
        msg = EmailMultiAlternatives(
            subject=f"[AUdoc] Blood Request — {blood_req.blood_group} ({blood_req.get_urgency_display()})",
            body=plain_text,
            from_email=None,
            to=[donor.email],
        )
        msg.attach_alternative(html_body, "text/html")
        send_email_async(msg)
    except Exception:
        pass


def donor_respond(request, token, action):
    """Handle a donor's accept/decline response from the email link."""
    try:
        dr = DonorResponse.objects.select_related("blood_request", "donor").get(token=token)
    except DonorResponse.DoesNotExist:
        return render(request, "app/donor_response_confirm.html", {"error": True})

    if dr.response != "PENDING":
        return render(request, "app/donor_response_confirm.html", {
            "already_responded": True,
            "response": dr.response,
        })

    if action == "accept":
        dr.response = "ACCEPTED"
        dr.blood_request.status = "APPROVED"
        dr.blood_request.save(update_fields=["status"])
    elif action == "decline":
        dr.response = "DECLINED"
    else:
        return render(request, "app/donor_response_confirm.html", {"error": True})

    dr.responded_at = timezone.now()
    dr.save(update_fields=["response", "responded_at"])

    return render(request, "app/donor_response_confirm.html", {
        "action": action,
        "blood_request": dr.blood_request,
        "donor": dr.donor,
    })


def appointment_confirm(request, token, action):
    """Handle appointment confirmation from email link."""
    from .models import TodaysAppointment

    try:
        today_appt = TodaysAppointment.objects.select_related("appointment").get(confirmation_token=token)
    except TodaysAppointment.DoesNotExist:
        return render(request, "app/appointment_confirm.html", {"error": True})

    # Check if already responded
    if today_appt.status != "PENDING":
        return render(request, "app/appointment_confirm.html", {
            "already_responded": True,
            "status": today_appt.status,
            "appointment": today_appt.appointment,
        })

    # Check if expired
    if today_appt.is_expired():
        today_appt.status = "EXPIRED"
        today_appt.save(update_fields=["status"])
        return render(request, "app/appointment_confirm.html", {
            "expired": True,
            "appointment": today_appt.appointment,
        })

    # Process the action
    if action == "accept":
        today_appt.status = "CONFIRMED"
        today_appt.responded_at = timezone.now()

        # Assign FCFS queue position based on appointment booking time (created_at)
        # Count how many confirmed appointments for the same date were booked earlier
        earlier_confirmed = TodaysAppointment.objects.filter(
            status="CONFIRMED",
            appointment__appointment_date=today_appt.appointment.appointment_date,
            appointment__created_at__lt=today_appt.appointment.created_at
        ).count()

        # Queue position = number of earlier bookings + 1
        today_appt.queue_position = earlier_confirmed + 1

        # Update the main appointment status
        today_appt.appointment.status = "CONFIRMED"
        today_appt.appointment.save(update_fields=["status"])

    elif action == "decline":
        today_appt.status = "DECLINED"
        today_appt.responded_at = timezone.now()

        # Update the main appointment status
        today_appt.appointment.status = "CANCELLED"
        today_appt.appointment.save(update_fields=["status"])
    else:
        return render(request, "app/appointment_confirm.html", {"error": True})

    today_appt.save()

    return render(request, "app/appointment_confirm.html", {
        "action": action,
        "appointment": today_appt.appointment,
        "queue_position": today_appt.queue_position if action == "accept" else None,
    })


# ══════════════════════════════════════════════════════════════════
#  CUSTOM ADMIN PANEL
# ══════════════════════════════════════════════════════════════════

def _admin_required(view_func):
    """Decorator: must be authenticated + is_staff / is_superuser."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/')
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def post_login_redirect(request):
    """
    Redirect target after Django's built-in login view.
    Admins → custom admin panel.  Everyone else → home.
    """
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    return redirect('home')


@_admin_required
def admin_dashboard(request):
    # Query data for the dashboard
    todays_appointments = TodaysAppointment.objects.select_related(
        'appointment', 'appointment__doctor'
    ).filter(
        appointment__appointment_date=date.today()
    ).order_by('appointment__created_at')  # FCFS order

    blood_donations = BloodDonation.objects.order_by('-created_at')
    blood_requests = BloodRequest.objects.order_by('-created_at')
    all_appointments = Appointment.objects.select_related('doctor').order_by('-created_at')
    doctors = Doctor.objects.all().order_by('name')

    context = {
        # ── Main dashboard data for new template ──────────
        'todays_appointments': todays_appointments,
        'blood_donations': blood_donations,
        'blood_requests': blood_requests,
        'appointments': all_appointments,
        'doctors': doctors,

        # ── stat cards for dashboard ──────────────────────
        'stat_pending_reg':       StudentRegistration.objects.filter(status='PENDING').count(),
        'stat_pending_appts':     Appointment.objects.filter(status='PENDING').count(),
        'stat_pending_blooddon':  BloodDonation.objects.filter(status='PENDING').count(),
        'stat_pending_bloodreq':  BloodRequest.objects.filter(status='PENDING').count(),
        'stat_active_doctors':    Doctor.objects.filter(is_available=True).count(),
        'stat_feedback':          HelpDesk.objects.count(),
        'stat_staff':             StaffProfile.objects.count(),
        'stat_todays_pending':    TodaysAppointment.objects.filter(status='PENDING').count(),
        'stat_todays_confirmed':  TodaysAppointment.objects.filter(status='CONFIRMED').count(),

        # ── Legacy table data (preserved for compatibility) ──
        'registrations':  StudentRegistration.objects.order_by('-registered_at'),
        'blood_donations': BloodDonation.objects.order_by('-created_at'),
        'donations':      Donation.objects.order_by('-donated_at'),
        'feedback':       HelpDesk.objects.order_by('-submitted_at'),
        'login_logs':     LoginLog.objects.order_by('-date', '-time')[:100],
        'staff_members':  StaffProfile.objects.order_by('name'),

        # ── misc ────────────────────────────────────────────
        'active_tab':    request.GET.get('tab', 'dashboard'),
        'dept_choices':  MEDICAL_DEPT_CHOICES,
        'day_choices':   DAY_CHOICES,
    }
    return render(request, 'app/admin_panel.html', context)


@_admin_required
def admin_dashboard_stats(request):
    """AJAX endpoint for real-time dashboard statistics"""
    # Calculate statistics
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Today's stats
    todays_appointments = TodaysAppointment.objects.filter(appointment__appointment_date=today).count()
    todays_confirmed = TodaysAppointment.objects.filter(appointment__appointment_date=today, status='CONFIRMED').count()
    todays_pending = TodaysAppointment.objects.filter(appointment__appointment_date=today, status='PENDING').count()

    # Yesterday's stats for comparison
    yesterdays_appointments = TodaysAppointment.objects.filter(appointment__appointment_date=yesterday).count()

    # Calculate percentage changes
    def calc_percentage_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 1)

    appt_change = calc_percentage_change(todays_appointments, yesterdays_appointments)

    # Blood donations and requests
    total_donors = BloodDonation.objects.count()
    total_requests = BloodRequest.objects.count()
    active_doctors = Doctor.objects.filter(is_available=True).count()

    return JsonResponse({
        'todays_appointments': {
            'count': todays_appointments,
            'change': appt_change
        },
        'blood_donors': {
            'count': total_donors,
            'change': 8  # Mock data - could be calculated based on weekly/monthly trends
        },
        'blood_requests': {
            'count': total_requests,
            'change': -3  # Mock data
        },
        'active_doctors': {
            'count': active_doctors,
            'change': 5  # Mock data
        },
        'queue_stats': {
            'confirmed': todays_confirmed,
            'pending': todays_pending,
            'cancelled': todays_appointments - todays_confirmed - todays_pending
        }
    })


@_admin_required
def admin_chart_data(request):
    """AJAX endpoint for chart data"""
    from django.http import JsonResponse
    from datetime import date, timedelta
    from django.db.models import Count

    chart_type = request.GET.get('type', 'appointments')

    if chart_type == 'appointments':
        # Get last 7 days appointment data
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(6, -1, -1)]

        appointment_data = []
        for day in dates:
            count = Appointment.objects.filter(appointment_date=day).count()
            appointment_data.append(count)

        return JsonResponse({
            'labels': [day.strftime('%a') for day in dates],
            'data': appointment_data
        })

    elif chart_type == 'blood_groups':
        # Get blood group distribution
        blood_groups = ['O+', 'A+', 'B+', 'AB+', 'O-', 'A-', 'B-', 'AB-']
        blood_data = []

        for group in blood_groups:
            count = BloodDonation.objects.filter(blood_group=group).count()
            blood_data.append(count)

        return JsonResponse({
            'labels': blood_groups,
            'data': blood_data
        })

    return JsonResponse({'error': 'Invalid chart type'})


@_admin_required
@require_http_methods(["POST"])
def admin_registration_action(request, pk):
    reg = get_object_or_404(StudentRegistration, pk=pk)
    action = request.POST.get('action')

    if action == 'approve' and reg.status != 'APPROVED':
        if User.objects.filter(username=reg.student_id).exists():
            messages.warning(request, f"Student ID '{reg.student_id}' already has an account — skipped.")
        else:
            user = User.objects.create_user(
                username=reg.student_id,
                email=reg.email,
                first_name=reg.first_name,
                last_name=reg.last_name,
            )
            user.set_unusable_password()
            user.save()

            StudentProfile.objects.create(
                user=user,
                student_id=reg.student_id,
                phone=reg.phone,
                emergency_contact=reg.emergency_contact,
                department=reg.department,
                blood_group=reg.blood_group,
                home_address=reg.home_address,
                present_address=reg.present_address,
            )
            reg.status = 'APPROVED'
            reg.save()

            try:
                subject = f"✅ Approved, {reg.first_name}! AUdoc just unlocked for you"
                plain = (
                    f"Hey {reg.first_name}! 👋\n\n"
                    f"Great news: your AUdoc registration is APPROVED. 🎉\n"
                    f"Our admin team reviewed your form and gave it a very confident head nod.\n\n"
                    f"--- HOW TO LOG IN ---\n"
                    f"1. 🌐 Visit: /accounts/login/\n"
                    f"2. 🎓 Click the 'Student' tab\n"
                    f"3. 🔑 Enter your Student ID: {reg.student_id}\n"
                    f"4. 🚀 Hit Login (no password needed)\n\n"
                    f"That is all. You are now officially in the AUdoc healthy-humans club.\n"
                    f"Please celebrate responsibly (water is recommended). 😄\n\n"
                    f"Stay healthy,\n"
                    f"The AUdoc Team 🏥"
                )
                login_url = request.build_absolute_uri('/accounts/login/')
                html_body = """
                <!DOCTYPE html>
                <html>
                <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                body {{ margin: 0; padding: 0; background-color: #e8f0fe; font-family: 'Segoe UI', Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 20px; box-shadow: 0 8px 32px rgba(26,92,150,.18); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #1a5c96 0%, #134a7a 100%); color: #ffffff; padding: 42px 20px; text-align: center; }}
                .header h1 {{ margin: 10px 0; font-size: 28px; font-weight: bold; }}
                .header .badge {{ background: rgba(255,255,255,0.22); color: #ffffff; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-top: 10px; font-size: 14px; }}
                .content {{ padding: 30px 25px; background: linear-gradient(180deg, #ffffff 0%, #f4f8fc 100%); }}
                .content p {{ color: #1f2a44; line-height: 1.6; margin: 0 0 15px 0; }}
                .section-title {{ font-weight: bold; color: #1a5c96; margin-top: 20px; margin-bottom: 15px; font-size: 16px; }}
                .login-box {{ background-color: #eef4ff; border: 2px solid #1a5c96; border-radius: 16px; padding: 20px; margin: 20px 0; }}
                .step {{ margin: 12px 0; display: flex; align-items: flex-start; }}
                .step-number {{ background-color: #1a5c96; color: #ffffff; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 12px; flex-shrink: 0; }}
                .step-text {{ color: #1f2a44; flex: 1; }}
                .student-id {{ background-color: #ddeaff; color: #134a7a; padding: 4px 10px; border-radius: 4px; font-family: monospace; font-weight: bold; }}
                .footer {{ background-color: #f4f8fc; border-top: 1px solid #e5edf5; padding: 20px; text-align: center; }}
                .footer p {{ margin: 5px 0; color: #51607a; font-size: 14px; }}
                a {{ color: #1a5c96; text-decoration: none; font-weight: 600; }}
                </style>
                </head>
                <body>
                <div class="container">
                    <div class="header">
                        <div style="font-size: 32px; margin-bottom: 10px;">🎉</div>
                        <h1>Congratulations, {name}!</h1>
                        <div class="badge">✅ YOUR REGISTRATION IS APPROVED</div>
                    </div>
                    <div class="content">
                        <p><strong>Big News! 🎉</strong></p>
                        <p>Your registration has been approved. The admin team reviewed your application, did a dramatic nod, and stamped it with a glorious blue tick ✅. Welcome to the <strong style="color: #1a5c96;">AUdoc</strong> family!</p>
                        <div class="login-box">
                            <p class="section-title">🔒 How to log in (easy peasy)</p>
                            <div class="step">
                                <div class="step-number">1</div>
                                <div class="step-text">Go to the <a href="{login_url}">AUdoc Login Page</a> 🚀</div>
                            </div>
                            <div class="step">
                                <div class="step-number">2</div>
                                <div class="step-text">Click the <strong>Student</strong> tab 🎓</div>
                            </div>
                            <div class="step">
                                <div class="step-number">3</div>
                                <div class="step-text">Enter your Student ID: <span class="student-id">{sid}</span></div>
                            </div>
                            <div class="step">
                                <div class="step-number">4</div>
                                <div class="step-text">Hit <strong>Login</strong> — and boom, you're in. 👍 No password needed.</div>
                            </div>
                        </div>
                        <p>Questions? Reach us at <a href="mailto:health@au.edu">health@au.edu</a> — we reply faster than campus gossip. 😊</p>
                    </div>
                    <div class="footer">
                        <p><strong>Stay healthy out there, {name}! 💪</strong></p>
                        <p style="color: #999;">© 2026 <strong style="color: #1a5c96;">AUdoc</strong> — Assam University Silchar Campus Health</p>
                    </div>
                </div>
                </body>
                </html>""".format(name=reg.first_name, sid=reg.student_id, login_url=login_url)
                msg = EmailMultiAlternatives(subject, plain, None, [reg.email])
                msg.attach_alternative(html_body, "text/html")
                send_email_async(msg)
            except Exception:
                pass

            messages.success(request, f"🎉 {reg.get_full_name()} is officially in! Account created & approval email fired off.")

    elif action == 'reject':
        reg.status = 'REJECTED'
        reg.save()
        messages.success(request, f"Registration for {reg.get_full_name()} has been rejected.")

    return redirect(f"{reverse('admin_dashboard')}?tab=registrations")


@_admin_required
@require_http_methods(["POST"])
def admin_appointment_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    new_status = request.POST.get('status')
    if new_status in ('PENDING', 'CONFIRMED', 'COMPLETED', 'NO_SHOW', 'REJECTED', 'CANCELLED'):
        appt.status = new_status
        
        # Handle no-show marking
        if new_status == 'NO_SHOW':
            from app.no_show_helper import mark_appointment_as_no_show
            mark_appointment_as_no_show(pk, reason="Marked by admin")
            messages.success(request, f"Appointment #{pk} marked as NO_SHOW. Student restrictions updated if applicable.")
        # Handle completion
        elif new_status == 'COMPLETED':
            from app.no_show_helper import mark_appointment_as_completed
            mark_appointment_as_completed(pk)
            messages.success(request, f"Appointment #{pk} marked as COMPLETED.")
        else:
            appt.save()
            messages.success(request, f"Appointment #{pk} updated to {new_status}.")
    
    return redirect(f"{reverse('admin_dashboard')}?tab=appointments")


@_admin_required
@require_http_methods(["POST"])
def admin_blood_donation_status(request, pk):
    don = get_object_or_404(BloodDonation, pk=pk)
    new_status = request.POST.get('status')
    if new_status in ('PENDING', 'APPROVED', 'COMPLETED', 'REJECTED'):
        don.status = new_status
        don.save()
        messages.success(request, f"Blood donation #{pk} updated to {new_status}.")
    return redirect(f"{reverse('admin_dashboard')}?tab=blood-donations")


@_admin_required
@require_http_methods(["POST"])
def admin_blood_request_status(request, pk):
    req = get_object_or_404(BloodRequest, pk=pk)
    new_status = request.POST.get('status')
    if new_status in ('PENDING', 'APPROVED', 'FULFILLED', 'REJECTED'):
        req.status = new_status
        req.save()
        messages.success(request, f"Blood request #{pk} updated to {new_status}.")
    return redirect(f"{reverse('admin_dashboard')}?tab=blood-requests")


@_admin_required
@require_http_methods(["POST"])
def admin_donation_toggle_paid(request, pk):
    don = get_object_or_404(Donation, pk=pk)
    don.is_paid = not don.is_paid
    don.save()
    return redirect(f"{reverse('admin_dashboard')}?tab=donations")


@_admin_required
@require_POST
def admin_doctor_save(request):
    pk             = request.POST.get('pk')
    name           = request.POST.get('name', '').strip()
    email          = request.POST.get('email', '').strip()
    phone          = request.POST.get('phone', '').strip()
    specialized_in = request.POST.get('specialized_in', '').strip()
    available_days = request.POST.get('available_days', '').strip()
    available_time = request.POST.get('available_time', '').strip()
    is_available   = request.POST.get('is_available') == 'on'

    if not name:
        messages.error(request, "Doctor name is required.")
        return redirect(f"{reverse('admin_dashboard')}?tab=doctors")

    if pk:
        doc = get_object_or_404(Doctor, pk=pk)
        doc.name = name; doc.email = email; doc.phone = phone
        doc.specialized_in = specialized_in
        doc.available_days = available_days
        doc.available_time = available_time
        doc.is_available = is_available
        photo = request.FILES.get('photo')
        if photo:
            doc.photo = photo
        doc.save()
        messages.success(request, f"Doctor '{name}' updated.")
    else:
        Doctor.objects.create(
            name=name, email=email, phone=phone,
            specialized_in=specialized_in,
            available_days=available_days,
            available_time=available_time,
            is_available=is_available,
            photo=request.FILES.get('photo'),
        )
        messages.success(request, f"Doctor '{name}' added.")

    return redirect(f"{reverse('admin_dashboard')}?tab=doctors")


@_admin_required
@require_POST
def admin_doctor_delete(request, pk):
    doc = get_object_or_404(Doctor, pk=pk)
    name = doc.name
    doc.delete()
    messages.success(request, f"Doctor '{name}' deleted.")
    return redirect(f"{reverse('admin_dashboard')}?tab=doctors")


@_admin_required
@require_POST
def admin_staff_save(request):
    pk          = request.POST.get('pk') or None
    staff_id    = request.POST.get('staff_id', '').strip()
    name        = request.POST.get('name', '').strip()
    email       = request.POST.get('email', '').strip()
    phone       = request.POST.get('phone', '').strip()
    password    = request.POST.get('password', '').strip()
    is_doctor   = request.POST.get('is_doctor') == 'on'

    if not staff_id or not name:
        messages.error(request, "Staff ID and Name are required.")
        return redirect(f"{reverse('admin_dashboard')}?tab=staff-members")

    if pk:
        staff = get_object_or_404(StaffProfile, pk=pk)
        staff.staff_id  = staff_id
        staff.name      = name
        staff.email     = email
        staff.phone     = phone
        staff.is_doctor = is_doctor
        if password:
            staff.password = make_password(password)
        staff.save()
        messages.success(request, f"Staff member '{name}' updated.")
    else:
        if not password:
            messages.error(request, "Password is required when adding a new staff member.")
            return redirect(f"{reverse('admin_dashboard')}?tab=staff-members")
        StaffProfile.objects.create(
            staff_id=staff_id, name=name, email=email,
            phone=phone, password=make_password(password), is_doctor=is_doctor,
        )
        messages.success(request, f"Staff member '{name}' added.")

    return redirect(f"{reverse('admin_dashboard')}?tab=staff-members")


@_admin_required
@require_POST
def admin_staff_delete(request, pk):
    staff = get_object_or_404(StaffProfile, pk=pk)
    name = staff.name
    staff.delete()
    messages.success(request, f"Staff member '{name}' deleted.")
    return redirect(f"{reverse('admin_dashboard')}?tab=staff-members")


@_admin_required
@require_POST
def admin_blood_request_delete(request, pk):
    blood_request = get_object_or_404(BloodRequest, pk=pk)
    requester_name = blood_request.requester_name
    blood_request.delete()
    messages.success(request, f"Blood request from '{requester_name}' deleted.")
    return redirect(f"{reverse('admin_dashboard')}?tab=blood-requests")


@_admin_required
def admin_clear_all_data(request):
    """
    DANGER ZONE: Irreversibly deletes all student-related data.
    Keeps: Doctor records, staff/superuser User accounts.
    """
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        if confirmation == 'DELETE_ALL_STUDENT_DATA':
            try:
                # Count records before deletion for detailed feedback
                counts = {
                    'student_registrations': StudentRegistration.objects.count(),
                    'student_profiles': StudentProfile.objects.count(),
                    'appointments': Appointment.objects.count(),
                    'todays_appointments': TodaysAppointment.objects.count(),
                    'blood_donations': BloodDonation.objects.count(),
                    'blood_requests': BloodRequest.objects.count(),
                    'donor_responses': DonorResponse.objects.count(),
                    'donations': Donation.objects.count(),
                    'feedback': HelpDesk.objects.count(),
                    'login_logs': LoginLog.objects.count(),
                }

                # Delete in FK-safe order
                DonorResponse.objects.all().delete()
                TodaysAppointment.objects.all().delete()
                BloodRequest.objects.all().delete()
                BloodDonation.objects.all().delete()
                Appointment.objects.all().delete()
                Donation.objects.all().delete()
                HelpDesk.objects.all().delete()
                LoginLog.objects.all().delete()
                StudentRegistration.objects.all().delete()
                StudentProfile.objects.all().delete()

                # Remove only non-admin user accounts (student accounts)
                from django.contrib.auth.models import User
                student_users = User.objects.filter(is_staff=False, is_superuser=False)
                student_count = student_users.count()
                student_users.delete()

                total_deleted = sum(counts.values()) + student_count

                messages.success(
                    request,
                    f"🗑️ STUDENT DATA PURGED: {total_deleted:,} records permanently deleted! "
                    f"Details: {counts['student_registrations']} registrations, "
                    f"{counts['appointments']} appointments, {counts['blood_donations']} blood donations, "
                    f"{counts['blood_requests']} blood requests, {student_count} user accounts, "
                    f"{counts['feedback']} feedback entries, and {counts['login_logs']} login logs."
                )

            except Exception as e:
                messages.error(request, f"❌ Critical error during data purge: {str(e)}")
        else:
            messages.error(request, "❌ Incorrect confirmation phrase. Data purge cancelled for safety.")

    return redirect(f"{reverse('admin_dashboard')}?tab=danger-zone")


# ── AI Chatbot ────────────────────────────────────────────────────────────────

@require_POST
def chat_api(request):
    """Stateless AI chat endpoint powered by Groq (free tier)."""
    import urllib.request as _urllib
    import urllib.error as _urlerr

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid request"}, status=400)

    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return JsonResponse({"error": "No message provided"}, status=400)

    api_key = os.environ.get("GROQ_API_KEY") or getattr(settings, "GROQ_API_KEY", "")
    if not api_key:
        return JsonResponse({"error": "Chatbot not configured — add GROQ_API_KEY to .env"}, status=503)

    system_prompt = (
        "You are a friendly health assistant for AUdoc — the Assam University Silchar Campus Health Center portal. "
        "Help students with health questions, appointment booking guidance, blood donation registration, "
        "and navigating the portal services. Be concise, warm, and supportive. "
        "Campus emergency contact: 0389-2330931. Clinic hours: Monday–Saturday, 9 AM–4 PM. "
        "Available services: Appointment booking, Blood Bank, Donor Network, Monetary Donations, Help Desk. "
        "For serious medical emergencies, always advise calling the emergency number immediately. "
        "Keep responses under 150 words."
    )

    messages_payload = [{"role": "system", "content": system_prompt}]
    for turn in history[-10:]:
        if turn.get("role") in ("user", "assistant") and turn.get("content"):
            messages_payload.append({"role": turn["role"], "content": turn["content"]})
    messages_payload.append({"role": "user", "content": message})

    payload = json.dumps({
        "model": "llama-3.1-8b-instant",
        "messages": messages_payload,
        "max_tokens": 512,
        "temperature": 0.7,
    }).encode("utf-8")

    req = _urllib.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "AUdoc-HealthPortal/1.0",
        },
        method="POST",
    )

    try:
        with _urllib.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except _urlerr.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            err_msg = json.loads(body).get("error", {}).get("message", body[:200])
        except Exception:
            err_msg = body[:200]
        if e.code == 401:
            return JsonResponse({"error": "Invalid Groq API key — check your GROQ_API_KEY in .env."}, status=500)
        if e.code == 429:
            return JsonResponse({"error": "Groq rate limit reached. Please wait a moment and try again."}, status=500)
        return JsonResponse({"error": f"API error {e.code}: {err_msg}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Could not reach AI service: {e}"}, status=500)

    try:
        reply = json.loads(raw)["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, json.JSONDecodeError):
        reply = "I received a response but couldn't read it. Please try again."

    return JsonResponse({"response": reply})


# ── Flutter App REST API ───────────────────────────────────────────────────────

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout as auth_logout

# Note: API endpoints use @csrf_exempt because Flutter app uses session-based auth
# with OTP verification. Rate limiting provides protection against abuse.


@csrf_exempt
@rate_limit_otp
@require_POST
def api_send_login_otp(request):
    """API: Send login OTP for Flutter app."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    student_id = sanitize_string(data.get("student_id", ""), max_length=50)
    if not student_id or not validate_student_id(student_id):
        return JsonResponse({"error": "Please enter a valid Student ID"}, status=400)

    try:
        user = User.objects.get(username=student_id)
    except User.DoesNotExist:
        # Return generic response to prevent user enumeration
        log_security_event("api_otp_nonexistent_user", request, {"student_id": student_id})
        return JsonResponse({"success": True, "message": "If this Student ID exists, an OTP will be sent"})

    email = user.email
    if not email:
        return JsonResponse({"error": "No email on file. Please contact health@au.edu"}, status=400)

    otp = generate_secure_otp(6)
    request.session["login_otp_data"] = {
        "student_id": student_id,
        "otp": otp,
        "expires": time.time() + 600,
    }

    # Send OTP email
    plain_text = f"Your AUdoc login code is: {otp}\nValid for 10 minutes."
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 400px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #1a5c96;">AUdoc Login Verification</h2>
        <p>Hi {user.first_name or student_id}!</p>
        <p>Your verification code is:</p>
        <div style="background: #f0f7ff; padding: 15px; text-align: center; font-size: 28px; font-weight: bold; color: #1a5c96; border-radius: 8px; letter-spacing: 4px;">
            {otp}
        </div>
        <p style="color: #666; font-size: 12px; margin-top: 15px;">This code expires in 10 minutes.</p>
    </div>
    """
    try:
        msg = EmailMultiAlternatives(
            subject="AUdoc Login Code",
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_body, "text/html")
        send_email_async(msg)
    except Exception as e:
        log_security_event("api_email_send_failed", request, {"error": str(e)}, level="error")
        return JsonResponse({"error": "Failed to send email. Please try again later."}, status=500)

    at = email.index("@")
    masked_email = email[:2] + ("*" * max(at - 2, 1)) + email[at:]
    return JsonResponse({
        "success": True,
        "message": f"OTP sent to {masked_email}",
        "email": masked_email,
    })


@csrf_exempt
@rate_limit_login
@require_POST
def api_student_login(request):
    """API: Verify OTP and login for Flutter app."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    student_id = sanitize_string(data.get("student_id", ""), max_length=50)
    otp_entered = sanitize_string(data.get("otp", ""), max_length=10)

    if not student_id or not validate_student_id(student_id):
        log_failed_login(request, student_id, "api_invalid_student_id")
        return JsonResponse({"error": "Invalid Student ID format"}, status=400)
    
    if not otp_entered:
        return JsonResponse({"error": "OTP is required"}, status=400)

    otp_data = request.session.get("login_otp_data", {})

    if otp_data.get("student_id") != student_id:
        log_failed_login(request, student_id, "api_otp_mismatch")
        return JsonResponse({"error": "OTP was sent for a different Student ID"}, status=400)
    if time.time() > otp_data.get("expires", 0):
        log_failed_login(request, student_id, "api_otp_expired")
        return JsonResponse({"error": "OTP has expired. Please request a new one"}, status=400)
    # Use constant-time comparison
    if not constant_time_compare(otp_data.get("otp", ""), otp_entered):
        log_failed_login(request, student_id, "api_otp_incorrect")
        return JsonResponse({"error": "Incorrect OTP"}, status=400)

    del request.session["login_otp_data"]

    user = authenticate(request, username=student_id)
    if user is None:
        log_failed_login(request, student_id, "api_user_not_found")
        return JsonResponse({"error": "Student ID not found or not approved"}, status=400)

    request.session["otp_login_verified"] = True
    login(request, user, backend="app.backends.StudentIDBackend")
    log_security_event("api_successful_login", request, {"student_id": student_id}, level="info")

    # Build profile data for Flutter User model
    try:
        profile = StudentProfile.objects.get(user=user)
        profile_data = {
            "student_id": user.username,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email,
            "phone": profile.phone,
            "blood_group": profile.blood_group,
            "department": profile.department,
            "home_address": profile.home_address,
            "present_address": profile.present_address,
            "emergency_contact": profile.emergency_contact,
            "is_verified": profile.is_verified,
        }
    except StudentProfile.DoesNotExist:
        profile_data = {
            "student_id": user.username,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email,
            "phone": "",
            "blood_group": "",
            "department": "",
            "home_address": "",
            "present_address": "",
            "emergency_contact": "",
            "is_verified": True,
        }

    return JsonResponse({
        "success": True,
        "message": "Login successful",
        "user": profile_data,
    })


@csrf_exempt
@rate_limit_otp
@require_POST
def api_send_register_otp(request):
    """API: Send registration OTP for Flutter app."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = sanitize_string(data.get("email", ""), max_length=254)
    if not email or not validate_email_format(email):
        return JsonResponse({"error": "Please enter a valid email address"}, status=400)

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "This email is already registered"}, status=400)

    otp = generate_secure_otp(6)
    request.session["register_otp_data"] = {
        "email": email,
        "otp": otp,
        "expires": time.time() + 600,
    }

    plain_text = f"Your AUdoc registration code is: {otp}\nValid for 10 minutes."
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 400px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #1a5c96;">AUdoc Registration</h2>
        <p>Your verification code is:</p>
        <div style="background: #f0f7ff; padding: 15px; text-align: center; font-size: 28px; font-weight: bold; color: #1a5c96; border-radius: 8px; letter-spacing: 4px;">
            {otp}
        </div>
        <p style="color: #666; font-size: 12px; margin-top: 15px;">This code expires in 10 minutes.</p>
    </div>
    """
    try:
        msg = EmailMultiAlternatives(
            subject="AUdoc Registration Code",
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_body, "text/html")
        send_email_async(msg)
    except Exception as e:
        log_security_event("api_register_email_failed", request, {"error": str(e)}, level="error")
        return JsonResponse({"error": "Failed to send email. Please try again later."}, status=500)

    return JsonResponse({"success": True, "message": "OTP sent to your email"})


@csrf_exempt
@rate_limit_login
@require_POST
def api_register(request):
    """API: Register new student for Flutter app."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    required_fields = [
        "first_name",
        "last_name",
        "email",
        "student_id",
        "phone",
        "emergency_contact",
        "department",
        "blood_group",
        "home_address",
        "present_address",
        "otp",
    ]
    for field in required_fields:
        if not data.get(field):
            return JsonResponse({"error": f"{field} is required"}, status=400)

    # Sanitize inputs
    student_id = sanitize_string(data.get("student_id", ""), max_length=50)
    email = sanitize_string(data.get("email", ""), max_length=254)
    otp_entered = sanitize_string(data.get("otp", ""), max_length=10)

    # Validate formats
    if not validate_student_id(student_id):
        return JsonResponse({"error": "Invalid Student ID format"}, status=400)
    if not validate_email_format(email):
        return JsonResponse({"error": "Invalid email format"}, status=400)

    # Verify OTP
    otp_data = request.session.get("register_otp_data", {})
    if otp_data.get("email") != email:
        return JsonResponse({"error": "OTP was sent for a different email"}, status=400)
    if time.time() > otp_data.get("expires", 0):
        return JsonResponse({"error": "OTP has expired. Please request a new one"}, status=400)
    if not constant_time_compare(otp_data.get("otp", ""), otp_entered):
        return JsonResponse({"error": "Incorrect OTP"}, status=400)

    del request.session["register_otp_data"]

    # Check if student ID already exists
    if User.objects.filter(username=student_id).exists():
        return JsonResponse({"error": "This Student ID is already registered"}, status=400)
    if StudentRegistration.objects.filter(student_id=student_id).exists():
        return JsonResponse({"error": "A registration with this Student ID is pending approval"}, status=400)

    registration = StudentRegistration.objects.create(
        student_id=student_id,
        first_name=sanitize_string(data["first_name"], max_length=150),
        last_name=sanitize_string(data["last_name"], max_length=150),
        email=email,
        phone=sanitize_string(data["phone"], max_length=20),
        emergency_contact=sanitize_string(data["emergency_contact"], max_length=20),
        blood_group=sanitize_string(data["blood_group"], max_length=10),
        department=sanitize_string(data["department"], max_length=20),
        home_address=sanitize_string(data["home_address"], max_length=500),
        present_address=sanitize_string(data["present_address"], max_length=500),
    )

    log_security_event("api_registration_submitted", request, {"student_id": student_id}, level="info")
    return JsonResponse({
        "success": True,
        "message": "Registration submitted. Awaiting admin approval.",
        "registration_id": registration.id,
    })


@rate_limit_api
def api_doctors(request):
    """API: Get list of doctors for Flutter app."""
    doctors = Doctor.objects.filter(is_available=True).order_by("specialized_in", "name")
    
    doctor_list = []
    for doc in doctors:
        doctor_list.append({
            "id": doc.id,
            "name": doc.name,
            "email": doc.email,
            "phone": doc.phone,
            "specialized_in": doc.specialized_in,
            "specialized_in_display": doc.get_specialized_in_display(),
            "available_days": doc.available_days_list,
            "available_time": doc.available_time,
            "is_available": doc.is_available,
            "photo_url": doc.photo.url if doc.photo else None,
        })

    return JsonResponse(doctor_list, safe=False)


@csrf_exempt
@rate_limit_api
def api_appointments(request):
    """API: Get or create appointments for Flutter app."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    student_id = request.user.username

    if request.method == "GET":
        appointments = Appointment.objects.filter(student_id=student_id).select_related("doctor").order_by("-created_at")
        apt_list = []
        for apt in appointments:
            queue_position = None
            today_appt = apt.todays_appointments.filter(status="CONFIRMED").first()
            if today_appt:
                queue_position = today_appt.queue_position

            apt_list.append({
                "id": apt.id,
                "student_id": apt.student_id,
                "student_name": apt.student_name,
                "phone": apt.phone,
                "email": apt.email,
                "student_department": apt.student_department,
                "medical_department": apt.medical_department,
                "medical_department_display": apt.get_medical_department_display(),
                "doctor_id": apt.doctor_id,
                "doctor_name": apt.doctor.name if apt.doctor else None,
                "appointment_date": apt.appointment_date.isoformat() if apt.appointment_date else None,
                "appointment_time": apt.appointment_time,
                "problem_description": apt.problem_description,
                "status": apt.status,
                "created_at": apt.created_at.isoformat(),
                "queue_position": queue_position,
            })

        return JsonResponse(apt_list, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        required = ["student_name", "phone", "email", "medical_department", "appointment_date", "appointment_time", "problem_description"]
        for field in required:
            if data.get(field) in [None, ""]:
                return JsonResponse({"error": f"{field} is required"}, status=400)

        try:
            apt_date = date.fromisoformat(data["appointment_date"])
        except ValueError:
            return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        if apt_date < date.today():
            return JsonResponse({"error": "Cannot book appointments in the past"}, status=400)

        doctor = None
        doctor_id = data.get("doctor_id")
        if doctor_id is not None:
            try:
                doctor = Doctor.objects.get(id=doctor_id, is_available=True)
            except Doctor.DoesNotExist:
                return JsonResponse({"error": "Doctor not found"}, status=404)

        student_department = data.get("student_department")
        if not student_department:
            try:
                student_department = request.user.student_profile.department
            except StudentProfile.DoesNotExist:
                return JsonResponse({"error": "student_department is required"}, status=400)

        # Check for existing appointment
        existing = Appointment.objects.filter(
            student_id=student_id,
            doctor=doctor,
            appointment_date=apt_date,
            appointment_time=data["appointment_time"],
        ).exclude(status="CANCELLED").first()

        if existing:
            return JsonResponse({"error": "You already have an appointment at this time"}, status=400)

        # Create appointment
        appointment = Appointment.objects.create(
            student_id=student_id,
            student_name=data["student_name"],
            phone=data["phone"],
            email=data["email"],
            student_department=student_department,
            medical_department=data["medical_department"],
            doctor=doctor,
            appointment_date=apt_date,
            appointment_time=data["appointment_time"],
            problem_description=data["problem_description"],
            status="PENDING",
        )

        return JsonResponse({
            "success": True,
            "message": "Appointment booked successfully",
            "appointment": {
                "id": appointment.id,
                "doctor_name": doctor.name if doctor else None,
                "appointment_date": apt_date.isoformat(),
                "appointment_time": appointment.appointment_time,
                "status": appointment.status,
            }
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
@rate_limit_api
def api_blood_donations(request):
    """API: Get or create blood donations for Flutter app."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    student_id = request.user.username
    user_email = request.user.email

    if request.method == "GET":
        donation = BloodDonation.objects.filter(Q(student_id=student_id) | Q(email=user_email)).order_by("-created_at").first()

        if not donation:
            return JsonResponse(None, safe=False)

        return JsonResponse({
            "id": donation.id,
            "student_id": donation.student_id,
            "donor_name": donation.donor_name,
            "email": donation.email,
            "phone": donation.phone,
            "blood_group": donation.blood_group,
            "date_of_birth": donation.date_of_birth.isoformat(),
            "weight": donation.weight,
            "previous_donation": donation.previous_donation,
            "health_condition": donation.health_condition,
            "message": donation.message,
            "status": donation.status,
            "created_at": donation.created_at.isoformat(),
        })

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        required = ["donor_name", "email", "phone", "blood_group", "date_of_birth", "weight"]
        for field in required:
            if data.get(field) in [None, ""]:
                return JsonResponse({"error": f"{field} is required"}, status=400)

        existing = BloodDonation.objects.filter(Q(student_id=student_id) | Q(email=data.get("email", ""))).first()
        if existing:
            return JsonResponse({"error": "You are already registered as a blood donor"}, status=400)

        try:
            dob = date.fromisoformat(data["date_of_birth"])
        except ValueError:
            return JsonResponse({"error": "Invalid date_of_birth format. Use YYYY-MM-DD"}, status=400)

        # Sanitize inputs
        donor_name = sanitize_string(data["donor_name"], max_length=150)
        email = sanitize_string(data["email"], max_length=254)
        phone = sanitize_string(data["phone"], max_length=20)

        # Create new donor registration
        donation = BloodDonation.objects.create(
            student_id=sanitize_string(data.get("student_id", ""), max_length=50) or student_id,
            donor_name=donor_name,
            email=email,
            phone=phone,
            blood_group=sanitize_string(data["blood_group"], max_length=10),
            date_of_birth=dob,
            weight=int(data["weight"]),
            previous_donation=bool(data.get("previous_donation", False)),
            health_condition=sanitize_string(data.get("health_condition", ""), max_length=200),
            message=sanitize_string(data.get("message", ""), max_length=500),
        )

        return JsonResponse({
            "success": True,
            "message": "Registered as blood donor",
            "donation_id": donation.id,
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
@rate_limit_api
def api_blood_requests(request):
    """API: Get or create blood requests for Flutter app."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    student_id = request.user.username

    if request.method == "GET":
        requests_list = BloodRequest.objects.filter(student_id=student_id).order_by("-created_at")

        req_list = []
        for req in requests_list:
            req_list.append({
                "id": req.id,
                "student_id": req.student_id,
                "requester_name": req.requester_name,
                "email": req.email,
                "phone": req.phone,
                "blood_group": req.blood_group,
                "units_required": req.units_required,
                "reason": req.reason,
                "urgency": req.urgency,
                "required_date": req.required_date.isoformat(),
                "hospital_name": req.hospital_name,
                "hospital_contact": req.hospital_contact,
                "notes": req.notes,
                "status": req.status,
                "created_at": req.created_at.isoformat(),
            })

        return JsonResponse(req_list, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        required = [
            "requester_name",
            "email",
            "phone",
            "blood_group",
            "units_required",
            "reason",
            "required_date",
            "hospital_name",
            "hospital_contact",
        ]
        for field in required:
            if data.get(field) in [None, ""]:
                return JsonResponse({"error": f"{field} is required"}, status=400)

        try:
            required_date = date.fromisoformat(data["required_date"])
        except ValueError:
            return JsonResponse({"error": "Invalid required_date format. Use YYYY-MM-DD"}, status=400)

        blood_request = BloodRequest.objects.create(
            student_id=data.get("student_id") or student_id,
            requester_name=data["requester_name"],
            email=data["email"],
            phone=data["phone"],
            blood_group=sanitize_string(data["blood_group"], max_length=10),
            units_required=int(data["units_required"]),
            urgency=sanitize_string(data.get("urgency", "MEDIUM"), max_length=10),
            hospital_name=sanitize_string(data["hospital_name"], max_length=200),
            hospital_contact=sanitize_string(data["hospital_contact"], max_length=200),
            reason=sanitize_string(data["reason"], max_length=200),
            required_date=required_date,
            notes=sanitize_string(data.get("notes", ""), max_length=500),
        )

        return JsonResponse({
            "success": True,
            "message": "Blood request submitted",
            "request_id": blood_request.id,
        })

    return JsonResponse({"error": "Method not allowed"}, status=405)


@rate_limit_api
def api_profile(request):
    """API: Get user profile for Flutter app."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    user = request.user

    try:
        profile = StudentProfile.objects.get(user=user)
        profile_data = {
            "student_id": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": profile.phone,
            "blood_group": profile.blood_group,
            "department": profile.department,
            "home_address": profile.home_address,
            "present_address": profile.present_address,
            "emergency_contact": profile.emergency_contact,
            "is_verified": profile.is_verified,
        }
    except StudentProfile.DoesNotExist:
        profile_data = {
            "student_id": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": "",
            "blood_group": "",
            "department": "",
            "home_address": "",
            "present_address": "",
            "emergency_contact": "",
            "is_verified": True,
        }

    return JsonResponse(profile_data)


@csrf_exempt
@require_POST
def api_logout(request):
    """API: Logout user for Flutter app."""
    if request.user.is_authenticated:
        log_security_event("api_logout", request, {"student_id": request.user.username}, level="info")
    auth_logout(request)
    return JsonResponse({"success": True, "message": "Logged out successfully"})


# ═══════════════════════════════════════════════════════════════════════════════
#  APPOINTMENT SLOT FILTERING (AJAX) - Dynamic slot availability
# ═══════════════════════════════════════════════════════════════════════════════

@require_http_methods(["GET"])
def api_appointment_slots(request):
    """
    AJAX endpoint to get available appointment slots based on doctor and date.
    
    Query parameters:
        - doctor_id: ID of doctor (optional, for filtering)
        - appointment_date: Date in YYYY-MM-DD format (required)
    
    Returns:
        JSON: {
            'success': bool,
            'slots': [('09:00 AM', '09:00 AM'), ...],
            'doctor_available': bool,
            'message': str
        }
    """
    try:
        from app.doctor_availability import get_available_time_slots, is_doctor_available_on_date
        
        appointment_date_str = request.GET.get('appointment_date')
        doctor_id = request.GET.get('doctor_id')
        
        if not appointment_date_str:
            return JsonResponse({
                'success': False,
                'message': 'appointment_date is required'
            }, status=400)
        
        try:
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid date format. Use YYYY-MM-DD'
            }, status=400)
        
        # If doctor_id is provided, get slots for that doctor
        if doctor_id:
            try:
                doctor = Doctor.objects.get(id=doctor_id)
                
                # Check if doctor is available on this date
                if not is_doctor_available_on_date(doctor_id, appointment_date):
                    return JsonResponse({
                        'success': True,
                        'slots': [],
                        'doctor_available': False,
                        'message': f'{doctor.name} is not available on {appointment_date_str}'
                    })
                
                slots = get_available_time_slots(doctor_id, appointment_date)
                
                return JsonResponse({
                    'success': True,
                    'slots': slots,
                    'doctor_available': True,
                    'message': f'Found {len(slots)} available slots'
                })
            
            except Doctor.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Doctor not found'
                }, status=404)
        
        # Otherwise return default time slots (all available)
        return JsonResponse({
            'success': True,
            'slots': list(TIME_SLOT_CHOICES),
            'doctor_available': True,
            'message': 'All time slots available'
        })
    
    except Exception as e:
        logger.error(f"Error in api_appointment_slots: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def api_doctor_availability(request):
    """
    AJAX endpoint to check doctor availability and get next available date.
    
    Query parameters:
        - doctor_id: ID of doctor (required)
        - start_date: Start date for search in YYYY-MM-DD format (optional)
    
    Returns:
        JSON: {
            'success': bool,
            'doctor': {'id', 'name', 'specialized_in', ...},
            'is_available_today': bool,
            'next_available_date': YYYY-MM-DD or None,
            'leaves': [...],
            'message': str
        }
    """
    try:
        from app.doctor_availability import (
            is_doctor_available_on_date,
            get_doctor_next_available_date
        )
        
        doctor_id = request.GET.get('doctor_id')
        start_date_str = request.GET.get('start_date')
        
        if not doctor_id:
            return JsonResponse({
                'success': False,
                'message': 'doctor_id is required'
            }, status=400)
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Doctor not found'
            }, status=404)
        
        # Parse start_date if provided
        start_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD'
                }, status=400)
        else:
            start_date = date.today()
        
        # Check today's availability
        is_available_today = is_doctor_available_on_date(doctor_id, start_date)
        
        # Get next available date
        next_available = get_doctor_next_available_date(doctor_id, start_date)
        
        # Get active leaves
        leaves = DoctorLeave.objects.filter(
            doctor_id=doctor_id,
            is_active=True,
            leave_date_from__gte=start_date
        ).order_by('leave_date_from').values('leave_date_from', 'leave_date_to', 'leave_type', 'reason')
        
        return JsonResponse({
            'success': True,
            'doctor': {
                'id': doctor.id,
                'name': doctor.name,
                'email': doctor.email,
                'specialized_in': doctor.get_specialized_in_display(),
                'available_days': doctor.available_days,
                'available_time': doctor.available_time,
                'is_available': doctor.is_available,
            },
            'is_available_today': is_available_today,
            'next_available_date': next_available.isoformat() if next_available else None,
            'leaves': list(leaves),
            'message': 'Doctor availability retrieved'
        })
    
    except Exception as e:
        logger.error(f"Error in api_doctor_availability: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)

