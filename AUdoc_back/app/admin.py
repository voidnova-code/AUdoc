from django.contrib import admin, messages
from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from .models import (
    BloodRequest, BloodDonation, DonorResponse, HelpDesk, LoginLog, 
    Doctor, Appointment, Donation, StudentProfile, StaffProfile, 
    StudentRegistration, TodaysAppointment, DoctorLeave, StudentNoShowRecord
)


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
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id", "student_id", "get_full_name", "get_email",
        "phone", "emergency_contact", "department",
    )
    list_filter      = ("department", "blood_group", "is_verified")
    search_fields    = (
        "student_id", "user__first_name", "user__last_name",
        "user__email", "phone", "emergency_contact",
    )
    ordering         = ("user__first_name", "user__last_name")
    readonly_fields  = ("id",)
    fieldsets = (
        ("Account & ID", {
            "fields": ("id", "user", "student_id", "is_verified"),
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
        "doctor_id", "name", "email", "phone",
        "specialized_in", "is_available",
    )
    list_filter  = ("specialized_in", "is_available")
    search_fields = ("doctor_id", "name", "email", "phone")
    ordering     = ("name",)
    list_editable = ("is_available",)
    readonly_fields = ("doctor_id",)
    fieldsets = (
        ("Doctor Information", {
            "fields": ("doctor_id", "name", "email", "phone", "specialized_in"),
        }),
        ("Photo (Optional)", {
            "fields": ("photo",),
            "classes": ("collapse",),
            "description": "Upload a doctor profile photo (optional)",
        }),
        ("Availability", {
            "fields": ("available_days", "available_time", "is_available"),
            "description": "Enter days as comma-separated (e.g., 'Monday, Tuesday, Wednesday')",
        }),
        ("Working Hours (Optional - for advanced scheduling)", {
            "fields": ("working_hours_start", "working_hours_end", "lunch_break_start", "lunch_break_end"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "student_id", "student_name", "phone", "email",
        "medical_department", "doctor", "appointment_date", "appointment_time",
        "status", "was_no_show", "created_at",
    )
    list_filter  = ("status", "was_no_show", "medical_department", "student_department", "appointment_date")
    search_fields = ("student_id", "student_name", "email", "phone")
    ordering     = ("-appointment_date", "-appointment_time")
    readonly_fields = ("created_at", "reminder_24h_sent_at", "reminder_2h_sent_at", "actual_completion_date")
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
            "fields": ("problem_description", "status", "was_no_show", "actual_completion_date", "created_at"),
        }),
        ("Reminders Sent", {
            "fields": ("reminder_24h_sent", "reminder_24h_sent_at", "reminder_2h_sent", "reminder_2h_sent_at"),
            "classes": ("collapse",),
        }),
    )



@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display  = ("id", "student_id", "name", "email", "amount", "is_paid", "razorpay_order_id", "donated_at")
    list_filter   = ("is_paid", "donated_at")
    search_fields = ("student_id", "name", "email", "razorpay_order_id", "razorpay_payment_id")
    ordering      = ("-donated_at",)
    readonly_fields = ("id", "donated_at", "razorpay_order_id", "razorpay_payment_id", "razorpay_signature")
    list_editable = ("is_paid",)
    date_hierarchy  = "donated_at"
    fieldsets = (
        ("ID & Donor Information", {
            "fields": ("id", "student_id", "name", "email"),
        }),
        ("Donation Details", {
            "fields": ("amount", "is_paid", "razorpay_order_id", "razorpay_payment_id", "razorpay_signature", "donated_at"),
        }),
    )


@admin.register(BloodDonation)
class BloodDonationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "student_id", "donor_name", "blood_group", "phone", "email",
        "date_of_birth", "weight", "status", "created_at",
    )
    list_filter  = ("status", "blood_group", "previous_donation", "created_at")
    search_fields = ("student_id", "donor_name", "email", "phone")
    ordering     = ("-created_at",)
    readonly_fields = ("id", "created_at")
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
        "student_id", "requester_name", "email", "phone", "blood_group",
        "units_required", "reason", "urgency", "required_date",
        "hospital_name", "hospital_contact", "requested_donor", "status", "created_at",
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
            "fields": ("notes", "requested_donor", "status", "created_at"),
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


@admin.register(DonorResponse)
class DonorResponseAdmin(admin.ModelAdmin):
    list_display  = ("donor", "blood_request", "response", "responded_at")
    list_filter   = ("response",)
    search_fields = ("donor__donor_name", "donor__email", "blood_request__requester_name")
    ordering      = ("-blood_request__created_at",)
    readonly_fields = ("token", "responded_at")

    def has_add_permission(self, request):
        return False


@admin.register(HelpDesk)
class HelpDeskAdmin(admin.ModelAdmin):
    list_display  = ("name", "stars", "short_message", "submitted_at")
    list_filter   = ("stars", "submitted_at")
    search_fields = ("name", "message")
    ordering      = ("-submitted_at",)
    readonly_fields = ("submitted_at",)
    date_hierarchy  = "submitted_at"
    fieldsets = (
        ("Feedback", {
            "fields": ("name", "stars", "message"),
        }),
        ("Meta", {
            "fields": ("submitted_at",),
        }),
    )

    @admin.display(description="Message Preview")
    def short_message(self, obj):
        return (obj.message[:60] + "…") if len(obj.message) > 60 else (obj.message or "—")

    def has_add_permission(self, request):
        return False


@admin.register(TodaysAppointment)
class TodaysAppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "get_student_name", "get_student_id", "get_appointment_date",
        "get_appointment_time", "status", "queue_position", "email_sent_at",
        "response_deadline", "responded_at",
    )
    list_filter = ("status", "appointment__appointment_date", "email_sent_at")
    search_fields = (
        "appointment__student_name", "appointment__student_id",
        "appointment__email", "appointment__phone",
    )
    ordering = ("queue_position", "responded_at", "-created_at")
    readonly_fields = (
        "confirmation_token", "email_sent_at", "responded_at",
        "created_at", "queue_position",
    )
    list_editable = ("status",)
    date_hierarchy = "created_at"
    fieldsets = (
        ("Appointment Details", {
            "fields": ("appointment",),
        }),
        ("Confirmation Status", {
            "fields": (
                "status", "confirmation_token", "email_sent_at",
                "response_deadline", "responded_at",
            ),
        }),
        ("Queue Information", {
            "fields": ("queue_position", "created_at"),
        }),
    )

    @admin.display(description="Student Name", ordering="appointment__student_name")
    def get_student_name(self, obj):
        return obj.appointment.student_name

    @admin.display(description="Student ID", ordering="appointment__student_id")
    def get_student_id(self, obj):
        return obj.appointment.student_id

    @admin.display(description="Appointment Date", ordering="appointment__appointment_date")
    def get_appointment_date(self, obj):
        return obj.appointment.appointment_date

    @admin.display(description="Appointment Time", ordering="appointment__appointment_time")
    def get_appointment_time(self, obj):
        return obj.appointment.appointment_time

    def has_add_permission(self, request):
        # Prevent manual creation - should be created automatically
        return False


@admin.register(DoctorLeave)
class DoctorLeaveAdmin(admin.ModelAdmin):
    list_display = (
        "doctor", "leave_date_from", "leave_date_to", "leave_type", "is_active", "created_at",
    )
    list_filter = ("is_active", "leave_type", "leave_date_from")
    search_fields = ("doctor__name", "reason")
    ordering = ("-leave_date_from",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "leave_date_from"
    fieldsets = (
        ("Doctor Leave Details", {
            "fields": ("doctor", "leave_date_from", "leave_date_to", "leave_type", "is_active"),
        }),
        ("Leave Information", {
            "fields": ("reason",),
        }),
        ("System", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(StudentNoShowRecord)
class StudentNoShowRecordAdmin(admin.ModelAdmin):
    list_display = (
        "get_student_id", "get_student_name", "total_no_shows", 
        "last_no_show_date", "is_restricted", "restriction_until",
    )
    list_filter = ("is_restricted", "last_no_show_date")
    search_fields = ("student__student_id", "student__user__first_name", "student__user__last_name")
    ordering = ("-total_no_shows",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Student Information", {
            "fields": ("student",),
        }),
        ("No-Show Statistics", {
            "fields": ("total_no_shows", "last_no_show_date"),
        }),
        ("Booking Restriction", {
            "fields": ("is_restricted", "restriction_until"),
        }),
        ("System", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Student ID", ordering="student__student_id")
    def get_student_id(self, obj):
        return obj.student.student_id

    @admin.display(description="Student Name", ordering="student__user__first_name")
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.student_id

