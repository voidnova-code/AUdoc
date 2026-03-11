import random
import time

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, When, Value, IntegerField, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AppointmentForm, BloodDonationForm, BloodRequestForm, DonationForm, StudentRegistrationForm
from .models import Appointment, BloodDonation, BloodRequest, Doctor, Donation, StudentRegistration, BLOOD_GROUP_CHOICES


def student_login(request):
    if request.method == "POST":
        student_id  = request.POST.get("student_id", "").strip()
        otp_entered = request.POST.get("otp", "").strip()
        otp_data    = request.session.get("login_otp_data", {})

        if not otp_entered:
            messages.error(request, "Please verify your Student ID with OTP before logging in.")
            return redirect("/accounts/login/")
        if otp_data.get("student_id") != student_id:
            messages.error(request, "OTP was sent for a different Student ID. Please re-send.")
            return redirect("/accounts/login/")
        if time.time() > otp_data.get("expires", 0):
            messages.error(request, "Your OTP has expired. Please request a new one.")
            return redirect("/accounts/login/")
        if otp_data.get("otp") != otp_entered:
            messages.error(request, "Incorrect OTP. Please check your email and try again.")
            return redirect("/accounts/login/")

        del request.session["login_otp_data"]
        user = authenticate(request, username=student_id)
        if user is not None:
            request.session["otp_login_verified"] = True
            login(request, user, backend="app.backends.StudentIDBackend")
            return redirect("/")
        messages.error(request, "Student ID not found or not yet approved. Please check and try again.")
    return redirect("/accounts/login/")


@require_POST
def send_login_otp(request):
    from django.contrib.auth.models import User
    from django.core.mail import EmailMultiAlternatives

    student_id = request.POST.get("student_id", "").strip()
    if not student_id:
        return JsonResponse({"error": "Please enter your Student ID first."}, status=400)

    try:
        user = User.objects.get(username=student_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "No approved account found for this Student ID."}, status=400)

    email = user.email
    if not email:
        return JsonResponse({"error": "No email on file. Please contact health@au.edu."}, status=400)

    otp = str(random.randint(100000, 999999))
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
              &#169; 2026 <strong style="color:#1a5c96;">AUdoc</strong> &mdash; Ahsanullah University Campus Health<br/>
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
            subject="\U0001f510 Your AUdoc Login Verification Code",
            body=plain_text,
            from_email=None,
            to=[email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        at      = email.index("@")
        masked  = email[:2] + ("*" * (at - 2)) + email[at:]
        return JsonResponse({"success": True, "email": masked})
    except Exception as e:
        return JsonResponse({"error": "Could not send email: " + str(e)}, status=500)


@require_POST
def send_otp(request):
    email = request.POST.get("email", "").strip()

    if not email:
        return JsonResponse({"error": "Please enter an email address first."}, status=400)

    if StudentRegistration.objects.filter(email=email).exists():
        return JsonResponse({"error": "This email is already registered."}, status=400)

    otp = str(random.randint(100000, 999999))
    request.session["otp_data"] = {
        "email": email,
        "otp":   otp,
        "expires": time.time() + 600,   # valid for 10 minutes
    }

    from django.core.mail import EmailMultiAlternatives
    plain_text = (
        "Hi there!\n\n"
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
              &#169; 2026 <strong style="color:#1a5c96;">AUdoc</strong> &mdash; Ahsanullah University Campus Health<br/>
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
        msg.send(fail_silently=False)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": "Could not send email: " + str(e)}, status=500)


def register(request):
    form = StudentRegistrationForm(request.POST or None)
    otp_error = None

    if request.method == "POST" and form.is_valid():
        email       = form.cleaned_data["email"]
        otp_entered = request.POST.get("otp", "").strip()
        otp_data    = request.session.get("otp_data", {})

        if not otp_entered:
            otp_error = "Please verify your email before submitting."
        elif otp_data.get("email") != email:
            otp_error = "OTP was sent to a different email. Please re-verify."
        elif time.time() > otp_data.get("expires", 0):
            otp_error = "Your OTP has expired. Please request a new one."
        elif otp_data.get("otp") != otp_entered:
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
    today = timezone.localdate()
    first_of_month = today.replace(day=1)

    # Top money donor this month (highest total donation amount)
    top_money_donor = (
        Donation.objects
        .filter(donated_at__date__gte=first_of_month)
        .values("name", "student_id")
        .annotate(total=Sum("amount"))
        .order_by("-total")
        .first()
    )

    # Featured blood donor this month (most recently approved this month)
    top_blood_donor = (
        BloodDonation.objects
        .filter(status="APPROVED", created_at__date__gte=first_of_month)
        .order_by("-created_at")
        .first()
    )
    # Fallback: most recently approved blood donor ever
    if not top_blood_donor:
        top_blood_donor = (
            BloodDonation.objects
            .filter(status="APPROVED")
            .order_by("-created_at")
            .first()
        )

    # Campus medical center departments
    specialties = [
        {"icon": "🩺", "name": "General Physician",          "count": 5},
        {"icon": "🦷", "name": "Dental Care",                "count": 3},
        {"icon": "👁️", "name": "Eye Care",                   "count": 2},
        {"icon": "🧠", "name": "Mental Health & Counseling", "count": 4},
        {"icon": "🦴", "name": "Orthopedics",                "count": 2},
        {"icon": "🧴", "name": "Dermatology",                "count": 2},
        {"icon": "🤰", "name": "Gynecology",                 "count": 2},
        {"icon": "🏃", "name": "Physiotherapy",              "count": 3},
    ]

    # Campus doctors — pulled live from the database
    doctors = Doctor.objects.filter(is_available=True).order_by("specialized_in", "name")

    return render(request, "app/home.html", {
        "specialties":      specialties,
        "doctors":          doctors,
        "top_money_donor":  top_money_donor,
        "top_blood_donor":  top_blood_donor,
        "current_month":    today.strftime("%B %Y"),
    })


@login_required
def appointment(request):
    today = timezone.localdate()

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
            appointment_date__lt=today,
            status__in=["PENDING", "CONFIRMED"],
        ).update(status="COMPLETED")

    # Split this user's appointments into upcoming and history
    base_qs = Appointment.objects.filter(student_id=student_id) if student_id else Appointment.objects.none()
    upcoming_appointments = (
        base_qs
        .filter(appointment_date__gte=today)
        .exclude(status__in=["REJECTED", "CANCELLED", "COMPLETED"])
        .order_by("appointment_date", "appointment_time")
    )
    history_appointments = (
        base_qs
        .filter(Q(appointment_date__lt=today) | Q(status__in=["REJECTED", "CANCELLED", "COMPLETED"]))
        .order_by("-appointment_date", "-appointment_time")
    )

    form = AppointmentForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
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
        "today_str": today.isoformat(),
        "upcoming_appointments": upcoming_appointments,
        "history_appointments": history_appointments,
    })


def donation(request):
    form = DonationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data

        # Resolve donor identity from logged-in user if available
        student_id, name, email = "", "", ""
        if request.user.is_authenticated:
            try:
                profile = request.user.student_profile
                student_id = profile.student_id
            except Exception:
                pass
            name  = request.user.get_full_name()
            email = request.user.email

        Donation.objects.create(
            student_id=student_id,
            name=name,
            email=email,
            amount=cd["amount"],
            is_paid=False,
        )
        messages.success(
            request,
            "Thank you for your generous donation! We will process your payment shortly.",
        )
        return redirect("donation")

    return render(request, "app/donation.html", {"form": form})


def blood_donors_list(request):
    blood_group_filter = request.GET.get("blood_group", "")

    # Get all blood donors
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

            BloodRequest.objects.create(
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
            messages.success(
                request,
                "Your blood request has been submitted successfully! We will match it with our donors and contact you shortly.",
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


def request_blood_from_donor(request, donor_id):
    try:
        donor = BloodDonation.objects.get(id=donor_id, status="APPROVED")
    except BloodDonation.DoesNotExist:
        messages.error(request, "Donor not found or is not available.")
        return redirect("blood_donors_list")

    form = BloodRequestForm(request.POST or None)

    # Get initial data
    initial = {
        "blood_group": donor.blood_group,
    }
    if request.user.is_authenticated:
        initial.update({
            "requester_name": request.user.get_full_name(),
            "email": request.user.email,
        })
        try:
            profile = request.user.student_profile
            initial["phone"] = profile.phone
        except Exception:
            pass

    if request.method == "GET":
        form = BloodRequestForm(initial=initial)

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data

        # Resolve student_id if user is authenticated
        student_id = ""
        if request.user.is_authenticated:
            try:
                profile = request.user.student_profile
                student_id = profile.student_id
            except Exception:
                pass

        BloodRequest.objects.create(
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
            requested_donor=donor,
            notes=cd["notes"],
            status="PENDING",
        )
        messages.success(
            request,
            f"Your blood request has been sent to {donor.donor_name}! They will contact you at {cd['phone']} soon.",
        )
        return redirect("blood_donors_list")

    return render(request, "app/request_blood_from_donor.html", {
        "form": form,
        "donor": donor,
    })
