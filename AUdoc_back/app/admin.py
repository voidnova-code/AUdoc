from django.contrib import admin, messages
from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from .models import BloodRequest, BloodDonation, LoginLog, Doctor, Appointment, Donation, StudentProfile, StaffProfile, StudentRegistration


# ── Staff admin form with password hashing ──────────────────────────────────

class StaffAdminForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text="Leave blank when editing to keep the current password.",
    )

    class Meta:
        model  = StaffProfile
        fields = "__all__"


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    form = StaffAdminForm
    list_display  = ("staff_id", "name", "email", "phone", "is_doctor")
    list_filter   = ("is_doctor",)
    search_fields = ("staff_id", "name", "email", "phone")
    ordering      = ("name",)
    list_editable = ("is_doctor",)
    fieldsets = (
        ("Staff Information", {
            "fields": ("staff_id", "name", "email", "phone", "is_doctor"),
        }),
        ("Security", {
            "fields": ("password",),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Password is required only when creating a new record
        form.base_fields["password"].required = (obj is None)
        return form

    def save_model(self, request, obj, form, change):
        raw = form.cleaned_data.get("password")
        if raw:
            obj.password = make_password(raw)
        elif change:
            # Keep the existing hashed password if field left blank on edit
            obj.password = StaffProfile.objects.get(pk=obj.pk).password
        super().save_model(request, obj, form, change)


@admin.register(StudentRegistration)
class StudentRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "student_id", "get_full_name", "email",
        "phone", "department", "blood_group", "registered_at", "status",
    )
    list_filter      = ("status", "department", "blood_group", "registered_at")
    search_fields    = ("student_id", "first_name", "last_name", "email", "phone")
    ordering         = ("-registered_at",)
    readonly_fields  = ("registered_at",)
    list_editable    = ("status",)
    date_hierarchy   = "registered_at"
    fieldsets = (
        ("Personal Information", {
            "fields": ("first_name", "last_name", "email"),
        }),
        ("Student Details", {
            "fields": ("student_id", "department", "blood_group", "phone", "emergency_contact"),
        }),
        ("Address", {
            "fields": ("home_address", "present_address"),
        }),
        ("Application", {
            "fields": ("status", "registered_at"),
        }),
    )

    @admin.display(description="Full Name", ordering="first_name")
    def get_full_name(self, obj):
        return obj.get_full_name()

    def save_model(self, request, obj, form, change):
        # Capture old status before saving
        was_approved = False
        if change:
            try:
                was_approved = StudentRegistration.objects.get(pk=obj.pk).status == "APPROVED"
            except StudentRegistration.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

        # Only act when transitioning TO approved for the first time
        if obj.status == "APPROVED" and not was_approved:
            if User.objects.filter(username=obj.student_id).exists():
                self.message_user(
                    request,
                    f"'{obj.student_id}' already has an account — skipped account creation.",
                    level=messages.WARNING,
                )
                return

            # Create Django User — no password, students log in by Student ID only
            user = User.objects.create_user(
                username=obj.student_id,
                email=obj.email,
                first_name=obj.first_name,
                last_name=obj.last_name,
            )
            user.set_unusable_password()
            user.save()

            # Create StudentProfile (appears in Registered Students table)
            StudentProfile.objects.create(
                user=user,
                student_id=obj.student_id,
                phone=obj.phone,
                emergency_contact=obj.emergency_contact,
                department=obj.department,
                blood_group=obj.blood_group,
                home_address=obj.home_address,
                present_address=obj.present_address,
            )

            # Send approval email — no password, just Student ID needed to log in
            subject = "\U0001f389 You're In! Your AUdoc Registration is Approved"
            plain_text = (
                "Hey {name}!\n\n"
                "BIG NEWS -- your AUdoc registration has been APPROVED!\n\n"
                "Log in at: http://localhost:8000/accounts/login/\n"
                "Use the 'Student' tab and enter your Student ID: {sid}\n"
                "No password needed!\n\n"
                "Stay healthy,\nThe AUdoc Team"
            ).format(name=obj.first_name, sid=obj.student_id)

            html_body = (
                "<!DOCTYPE html>"
                "<html lang='en'>"
                "<head><meta charset='UTF-8'/><meta name='viewport' content='width=device-width,initial-scale=1.0'/></head>"
                "<body style='margin:0;padding:0;background:#e8f5e9;font-family:Segoe UI,Arial,sans-serif;'>"
                "<table width='100%' cellpadding='0' cellspacing='0' style='background:#e8f5e9;padding:40px 0;'>"
                "<tr><td align='center'>"
                "<table width='560' cellpadding='0' cellspacing='0' style='background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(29,131,72,.18);'>"

                # Header
                "<tr><td style='background:linear-gradient(135deg,#1d8348 0%,#145a32 100%);padding:36px 40px;text-align:center;'>"
                "<div style='display:inline-block;background:rgba(255,255,255,.15);border-radius:14px;padding:12px 18px;margin-bottom:14px;'>"
                "<span style='font-size:2.4rem;'>&#127881;</span>"
                "</div>"
                "<h1 style='margin:0;color:#ffffff;font-size:1.6rem;font-weight:700;letter-spacing:-.5px;'>Congratulations, {name}!</h1>"
                "<p style='margin:6px 0 0;color:#a9dfbf;font-size:.9rem;'>Your AUdoc registration has been approved</p>"
                "</td></tr>"

                # Body
                "<tr><td style='padding:36px 40px 28px;'>"
                "<p style='margin:0 0 6px;font-size:1.4rem;'>&#127775; Big News!</p>"
                "<p style='margin:0 0 24px;color:#555;font-size:.97rem;line-height:1.6;'>"
                "The admin team reviewed your application, had a cup of tea &#9749;, and stamped it with a big green tick. "
                "Welcome to the <strong style='color:#1d8348;'>AUdoc</strong> family! &#128588;"
                "</p>"

                # Login steps box
                "<table width='100%' cellpadding='0' cellspacing='0' style='margin-bottom:28px;'>"
                "<tr><td style='background:#f0faf4;border:1.5px solid #a9dfbf;border-radius:14px;padding:24px 28px;'>"
                "<p style='margin:0 0 14px;font-weight:700;font-size:.95rem;color:#1d8348;text-transform:uppercase;letter-spacing:1px;'>&#128274; How to log in (super easy!)</p>"
                "<table cellpadding='0' cellspacing='0'>"
                "<tr><td style='padding:5px 0;'><span style='display:inline-block;background:#1d8348;color:#fff;border-radius:50%;width:24px;height:24px;text-align:center;line-height:24px;font-size:.8rem;font-weight:700;margin-right:10px;'>1</span>"
                "<span style='color:#333;font-size:.92rem;'>Go to: <a href='http://localhost:8000/accounts/login/' style='color:#1a5c96;'>AUdoc Login Page</a></span></td></tr>"
                "<tr><td style='padding:5px 0;'><span style='display:inline-block;background:#1d8348;color:#fff;border-radius:50%;width:24px;height:24px;text-align:center;line-height:24px;font-size:.8rem;font-weight:700;margin-right:10px;'>2</span>"
                "<span style='color:#333;font-size:.92rem;'>Click the <strong>Student</strong> tab &#127891;</span></td></tr>"
                "<tr><td style='padding:5px 0;'><span style='display:inline-block;background:#1d8348;color:#fff;border-radius:50%;width:24px;height:24px;text-align:center;line-height:24px;font-size:.8rem;font-weight:700;margin-right:10px;'>3</span>"
                "<span style='color:#333;font-size:.92rem;'>Enter your Student ID: <strong style='font-family:Courier New,monospace;background:#eef4ff;color:#134a7a;padding:2px 10px;border-radius:6px;font-size:1rem;'>{sid}</strong></span></td></tr>"
                "<tr><td style='padding:5px 0;'><span style='display:inline-block;background:#1d8348;color:#fff;border-radius:50%;width:24px;height:24px;text-align:center;line-height:24px;font-size:.8rem;font-weight:700;margin-right:10px;'>4</span>"
                "<span style='color:#333;font-size:.92rem;'>Hit <strong>Login</strong> &mdash; that's it! &#129395; No password. Nada. Zero. Zilch.</span></td></tr>"
                "</table>"
                "</td></tr></table>"

                # Features
                "<p style='margin:0 0 12px;font-weight:700;font-size:.92rem;color:#444;'>&#10024; Once you are in, you can:</p>"
                "<table cellpadding='0' cellspacing='0' style='margin-bottom:24px;'>"
                "<tr><td style='padding:4px 0;color:#555;font-size:.9rem;'>&#128197;&nbsp; Book appointments with campus doctors</td></tr>"
                "<tr><td style='padding:4px 0;color:#555;font-size:.9rem;'>&#128203;&nbsp; Check doctor availability &amp; schedules</td></tr>"
                "<tr><td style='padding:4px 0;color:#555;font-size:.9rem;'>&#129657;&nbsp; Stop Googling symptoms at 2&nbsp;AM and see a real doctor</td></tr>"
                "</table>"

                "<p style='margin:0;color:#888;font-size:.85rem;line-height:1.6;'>"
                "Questions? Stuck? Just say hi at <a href='mailto:health@au.edu' style='color:#1d8348;'>health@au.edu</a> &mdash; we are a friendly bunch. &#128522;"
                "</p>"
                "</td></tr>"

                # Footer
                "<tr><td style='background:#f4faf6;padding:20px 40px;text-align:center;border-top:1px solid #d5ead8;'>"
                "<p style='margin:0 0 6px;font-size:.95rem;'>Stay healthy out there! &#128170;&#127995;</p>"
                "<p style='margin:0;font-size:.8rem;color:#999;'>"
                "&#169; 2026 <strong style='color:#1d8348;'>AUdoc</strong> &mdash; Ahsanullah University Campus Health<br/>"
                "Academic Block C, Room 101&nbsp;|&nbsp;health@au.edu"
                "</p>"
                "</td></tr>"

                "</table>"
                "</td></tr></table>"
                "</body></html>"
            ).format(name=obj.first_name, sid=obj.student_id)

            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_text,
                    from_email=None,
                    to=[obj.email],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
                self.message_user(
                    request,
                    f"Account created and approval email sent to {obj.email}.",
                    level=messages.SUCCESS,
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"Account created but email failed to send: {e}",
                    level=messages.WARNING,
                )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "student_id", "get_full_name", "get_email",
        "phone", "emergency_contact", "department", "blood_group",
    )
    list_filter      = ("department", "blood_group", "is_verified")
    search_fields    = (
        "student_id", "user__first_name", "user__last_name",
        "user__email", "phone", "emergency_contact",
    )
    ordering         = ("user__first_name", "user__last_name")
    readonly_fields  = ()
    fieldsets = (
        ("Account", {
            "fields": ("user", "is_verified", "student_id"),
        }),
        ("Personal Information", {
            "fields": ("phone", "emergency_contact", "department", "blood_group"),
        }),
        ("Address", {
            "fields": ("present_address", "home_address"),
        }),
    )

    @admin.display(description="Name", ordering="user__first_name")
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description="Email", ordering="user__email")
    def get_email(self, obj):
        return obj.user.email


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "email", "phone",
        "specialized_in", "available_days", "available_time", "is_available",
    )
    list_filter  = ("specialized_in", "is_available")
    search_fields = ("name", "email", "phone")
    ordering     = ("name",)
    list_editable = ("is_available",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "student_id", "student_name", "phone", "email",
        "medical_department", "doctor", "appointment_date", "appointment_time",
        "status", "created_at",
    )
    list_filter  = ("status", "medical_department", "student_department", "appointment_date")
    search_fields = ("student_id", "student_name", "email", "phone")
    ordering     = ("-appointment_date", "-appointment_time")
    readonly_fields = ("created_at",)
    list_editable = ("status",)
    date_hierarchy  = "appointment_date"
    fieldsets = (
        ("Student Information", {
            "fields": ("student_id", "student_name", "phone", "email", "student_department"),
        }),
        ("Appointment Details", {
            "fields": ("medical_department", "doctor", "appointment_date", "appointment_time"),
        }),
        ("Problem & Status", {
            "fields": ("problem_description", "status", "created_at"),
        }),
    )



@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display  = ("student_id", "name", "email", "amount", "is_paid", "donated_at")
    list_filter   = ("is_paid", "donated_at")
    search_fields = ("student_id", "name", "email")
    ordering      = ("-donated_at",)
    readonly_fields = ("donated_at",)
    list_editable = ("is_paid",)
    date_hierarchy  = "donated_at"
    fieldsets = (
        ("Donor Information", {
            "fields": ("student_id", "name", "email"),
        }),
        ("Donation Details", {
            "fields": ("amount", "is_paid", "donated_at"),
        }),
    )


@admin.register(BloodDonation)
class BloodDonationAdmin(admin.ModelAdmin):
    list_display = (
        "donor_name", "blood_group", "phone", "email",
        "status", "created_at",
    )
    list_filter  = ("status", "blood_group", "created_at")
    search_fields = ("student_id", "donor_name", "email", "phone")
    ordering     = ("-created_at",)
    readonly_fields = ("created_at",)
    list_editable = ("status",)
    date_hierarchy  = "created_at"
    fieldsets = (
        ("Donor Information", {
            "fields": ("donor_name", "email", "phone", "student_id"),
        }),
        ("Blood & Health", {
            "fields": ("blood_group", "date_of_birth", "weight", "health_condition", "previous_donation"),
        }),
        ("Donation Details", {
            "fields": ("message", "status", "created_at"),
        }),
    )


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = (
        "requester_name", "blood_group", "units_required", "urgency",
        "required_date", "status", "created_at",
    )
    list_filter  = ("status", "blood_group", "urgency", "required_date", "created_at")
    search_fields = ("student_id", "requester_name", "email", "phone", "hospital_name")
    ordering     = ("-created_at",)
    readonly_fields = ("created_at",)
    list_editable = ("status",)
    date_hierarchy  = "required_date"
    fieldsets = (
        ("Requester Information", {
            "fields": ("requester_name", "email", "phone", "student_id"),
        }),
        ("Blood Requirements", {
            "fields": ("blood_group", "units_required", "reason", "urgency", "required_date"),
        }),
        ("Hospital Information", {
            "fields": ("hospital_name", "hospital_contact"),
        }),
        ("Request Details", {
            "fields": ("notes", "status", "created_at"),
        }),
    )


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ("username", "date", "time", "ip_address", "is_verified")
    list_filter = ("date", "is_verified")
    search_fields = ("username", "ip_address")
    readonly_fields = ("user", "username", "date", "time", "ip_address", "is_verified")
    ordering = ("-date", "-time")
    date_hierarchy = "date"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
