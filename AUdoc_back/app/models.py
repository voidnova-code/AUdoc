import uuid
import secrets
import string

from django.db import models
from django.conf import settings


STUDENT_DEPT_CHOICES = [
    # Language & Literature
    ("LING",    "Linguistics"),
    ("BEN",     "Bengali"),
    ("HINDI",   "Hindi"),
    ("MANI",    "Manipuri"),
    ("SANS",    "Sanskrit"),
    ("ASM",     "Assamese"),
    ("ENG",     "English"),
    ("ARAB",    "Arabic"),
    ("FREN",    "French"),
    # Social Sciences
    ("ECON",    "Economics"),
    ("COM",     "Commerce"),
    ("POLSCI",  "Political Science"),
    ("HIST",    "History"),
    ("SOCIO",   "Sociology"),
    ("SWRK",    "Social Work"),
    # Arts, Media & Humanities
    ("MASSCOM", "Mass Communication"),
    ("VISART",  "Visual Arts"),
    ("PERART",  "Performing Arts"),
    ("PHIL",    "Philosophy"),
    # Education & Management
    ("EDU",     "Education"),
    ("BBA",     "Business Administration"),
    ("LIS",     "Library & Information Science"),
    # Physical & Mathematical Sciences
    ("PHY",     "Physics"),
    ("CHEM",    "Chemistry"),
    ("MATH",    "Mathematics"),
    ("STAT",    "Statistics"),
    ("CSE",     "Computer Science"),
    # Life Sciences
    ("LSBIO",   "Life Science & Bioinformatics"),
    ("MICRO",   "Microbiology"),
    ("BIOTECH", "Biotechnology"),
    # Engineering, Technology & Applied Sciences
    ("MECH",   "Mechanical Engineering"),
    ("CIVIL",  "Civil Engineering"),
    ("CSC",    "Computer Science Engineering"),
    ("IT",      "Information Technology"),
    ("ECE",     "Electronics & Telecommunication"),
    ("AGENG",   "Agricultural Engineering"),
    # Environment & Earth Sciences
    ("ECO",     "Ecology & Environmental Science"),
    ("EARTH",   "Earth Sciences"),
    # Professional Programs
    ("LAW",     "Law"),
    ("PHARMA",  "Pharmaceutical Sciences"),
    ("OTHER",   "Other"),
]

MEDICAL_DEPT_CHOICES = [
    ("GENERAL",  "General Physician"),
    ("DENTAL",   "Dental Care"),
    ("EYE",      "Eye Care"),
    ("MENTAL",   "Mental Health & Counseling"),
    ("ORTHO",    "Orthopedics"),
    ("DERM",     "Dermatology"),
    ("GYNAE",    "Gynecology"),
    ("PHYSIO",   "Physiotherapy"),
]

DAY_CHOICES = [
    ("MON", "Monday"),
    ("TUE", "Tuesday"),
    ("WED", "Wednesday"),
    ("THU", "Thursday"),
    ("FRI", "Friday"),
    ("SAT", "Saturday"),
    ("SUN", "Sunday"),
]

BLOOD_GROUP_CHOICES = [
    ("A+",  "A+"),
    ("A-",  "A-"),
    ("B+",  "B+"),
    ("B-",  "B-"),
    ("AB+", "AB+"),
    ("AB-", "AB-"),
    ("O+",  "O+"),
    ("O-",  "O-"),
]


class StudentProfile(models.Model):
    user              = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        verbose_name="User",
    )
    is_verified       = models.BooleanField(default=True, verbose_name="Verified")
    student_id        = models.CharField(
        max_length=50, blank=True, verbose_name="Student ID",
        help_text="Leave blank if this user is not a student",
    )
    phone             = models.CharField(max_length=20, verbose_name="Phone No.")
    emergency_contact = models.CharField(max_length=20, verbose_name="Emergency Contact No.")
    home_address      = models.TextField(verbose_name="Home Address")
    present_address   = models.TextField(verbose_name="Present Address")
    department        = models.CharField(
        max_length=10,
        choices=STUDENT_DEPT_CHOICES,
        verbose_name="Department",
    )
    blood_group       = models.CharField(
        max_length=4,
        choices=BLOOD_GROUP_CHOICES,
        verbose_name="Blood Group",
    )
    oauth_provider    = models.CharField(
        max_length=20,
        choices=[("password", "Password"), ("google", "Google")],
        default="password",
        verbose_name="OAuth Provider",
        help_text="Login method used",
    )
    oauth_id          = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="OAuth ID",
        help_text="Google unique ID (sub claim) for OAuth logins",
    )

    class Meta:
        ordering = ["user__username"]
        verbose_name = "Registered Student"
        verbose_name_plural = "Registered Students"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.student_id or 'Non-student'})"


class StaffProfile(models.Model):
    staff_id  = models.CharField(
        max_length=50, unique=True, verbose_name="Staff ID",
        help_text='e.g. "STAFF-001"',
    )
    name      = models.CharField(max_length=150, verbose_name="Name")
    email     = models.EmailField(unique=True, verbose_name="Email")
    phone     = models.CharField(max_length=20, verbose_name="Phone No.")
    password  = models.CharField(max_length=128, verbose_name="Password")
    is_doctor = models.BooleanField(default=False, verbose_name="Is Doctor")

    class Meta:
        ordering = ["name"]
        verbose_name = "Registered Staff"
        verbose_name_plural = "Registered Staff"

    def __str__(self):
        role = "Doctor" if self.is_doctor else "Staff"
        return f"{self.name} ({self.staff_id}) — {role}"


def generate_default_doctor_id():
    import secrets
    import string
    random_suffix = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))
    return f"DOC{random_suffix}"


class Doctor(models.Model):
    doctor_id       = models.CharField(
        max_length=20, unique=True, editable=False, verbose_name="Doctor ID",
        default=generate_default_doctor_id,
        help_text='Auto-generated ID (e.g., DOC4yt253)',
    )
    name            = models.CharField(max_length=150, verbose_name="Doctor Name")
    email           = models.EmailField(unique=True)
    phone           = models.CharField(max_length=20, verbose_name="Phone No.")
    specialized_in  = models.CharField(
        max_length=20,
        choices=MEDICAL_DEPT_CHOICES,
        verbose_name="Specialized In",
    )
    available_days  = models.CharField(
        max_length=200,
        verbose_name="Available Days",
        help_text="Hold Ctrl / Cmd to select multiple days (e.g., 'Monday, Tuesday, Wednesday, Thursday, Friday')",
    )
    available_time  = models.CharField(
        max_length=100,
        verbose_name="Available Time",
        help_text='e.g. "9:00 AM – 5:00 PM"',
    )
    working_hours_start = models.TimeField(null=True, blank=True, verbose_name="Working Hours Start")
    working_hours_end = models.TimeField(null=True, blank=True, verbose_name="Working Hours End")
    lunch_break_start = models.TimeField(null=True, blank=True, verbose_name="Lunch Break Start")
    lunch_break_end = models.TimeField(null=True, blank=True, verbose_name="Lunch Break End")
    is_available    = models.BooleanField(default=True, verbose_name="Available")
    photo           = models.ImageField(
        upload_to='doctors/',
        blank=True,
        null=True,
        verbose_name="Profile Photo",
    )

    @property
    def available_days_list(self):
        if self.available_days:
            return [d.strip() for d in self.available_days.split(',') if d.strip()]
        return []

    def save(self, *args, **kwargs):
        if not self.doctor_id:
            while True:
                random_suffix = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))
                self.doctor_id = f"DOC{random_suffix}"
                if not Doctor.objects.filter(doctor_id=self.doctor_id).exists():
                    break
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]
        verbose_name = "Doctor"
        verbose_name_plural = "Doctor List"

    def __str__(self):
        return f"{self.name} ({self.get_specialized_in_display()})"


TIME_SLOT_CHOICES = [
    # Morning OPD (9:00 AM – 1:00 PM)
    ("09:00 AM", "09:00 AM"), ("09:30 AM", "09:30 AM"),
    ("10:00 AM", "10:00 AM"), ("10:30 AM", "10:30 AM"),
    ("11:00 AM", "11:00 AM"), ("11:30 AM", "11:30 AM"),
    ("12:00 PM", "12:00 PM"), ("12:30 PM", "12:30 PM"),
    # Lunch break: 1:00 PM – 2:00 PM
    # Afternoon OPD (2:00 PM – 5:00 PM)
    ("02:00 PM", "02:00 PM"), ("02:30 PM", "02:30 PM"),
    ("03:00 PM", "03:00 PM"), ("03:30 PM", "03:30 PM"),
    ("04:00 PM", "04:00 PM"), ("04:30 PM", "04:30 PM"),
]


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("PENDING",   "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("COMPLETED", "Completed"),
        ("NO_SHOW",   "No-Show"),
        ("REJECTED",  "Rejected"),
        ("CANCELLED", "Cancelled"),
    ]

    student_id          = models.CharField(max_length=50, verbose_name="Student ID")
    student_name        = models.CharField(max_length=150, verbose_name="Student Name")
    phone               = models.CharField(max_length=20, verbose_name="Phone No.")
    email               = models.EmailField(verbose_name="Email")
    student_department  = models.CharField(
        max_length=10,
        choices=STUDENT_DEPT_CHOICES,
        verbose_name="Student Department",
    )
    medical_department  = models.CharField(
        max_length=20,
        choices=MEDICAL_DEPT_CHOICES,
        verbose_name="Medical Department",
    )
    doctor              = models.ForeignKey(
        "Doctor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Preferred Doctor",
        related_name="appointments",
    )
    appointment_date    = models.DateField(null=True, blank=True, verbose_name="Appointment Date")
    appointment_time    = models.CharField(
        max_length=20,
        choices=TIME_SLOT_CHOICES,
        null=True,
        blank=True,
        verbose_name="Preferred Time Slot",
    )
    problem_description = models.TextField(verbose_name="Description of Problem")
    status              = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="Status",
    )
    created_at          = models.DateTimeField(auto_now_add=True, verbose_name="Submitted At")
    # Reminder tracking fields
    reminder_24h_sent   = models.BooleanField(default=False, verbose_name="24-Hour Reminder Sent")
    reminder_2h_sent    = models.BooleanField(default=False, verbose_name="2-Hour Reminder Sent")
    reminder_24h_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="24H Reminder Sent At")
    reminder_2h_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="2H Reminder Sent At")
    # No-show tracking
    was_no_show         = models.BooleanField(default=False, verbose_name="No-Show")
    actual_completion_date = models.DateTimeField(null=True, blank=True, verbose_name="Actual Completion Time")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Appointment"
        verbose_name_plural = "Appointment List"

    def __str__(self):
        return (
            f"{self.student_name} ({self.student_id}) — "
            f"{self.get_medical_department_display()} on {self.appointment_date}"
        )


class StudentRegistration(models.Model):
    STATUS_CHOICES = [
        ("PENDING",  "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    first_name        = models.CharField(max_length=150, verbose_name="First Name")
    last_name         = models.CharField(max_length=150, verbose_name="Last Name")
    email             = models.EmailField(verbose_name="Email")
    student_id        = models.CharField(max_length=50, unique=True, verbose_name="Student ID")
    phone             = models.CharField(max_length=20, verbose_name="Phone No.")
    emergency_contact = models.CharField(max_length=20, verbose_name="Emergency Contact No.")
    department        = models.CharField(
        max_length=10,
        choices=STUDENT_DEPT_CHOICES,
        verbose_name="Department",
    )
    blood_group       = models.CharField(
        max_length=4,
        choices=BLOOD_GROUP_CHOICES,
        verbose_name="Blood Group",
    )
    home_address      = models.TextField(verbose_name="Home Address")
    present_address   = models.TextField(verbose_name="Present Address")
    registered_at     = models.DateTimeField(auto_now_add=True, verbose_name="Registered At")
    status            = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="Status",
    )

    class Meta:
        ordering = ["-registered_at"]
        verbose_name = "Student Registration"
        verbose_name_plural = "Student Registrations"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Donation(models.Model):
    student_id = models.CharField(max_length=50, blank=True, verbose_name="Student ID")
    name       = models.CharField(max_length=150, blank=True, verbose_name="Donor Name")
    email      = models.EmailField(blank=True, verbose_name="Email")
    amount     = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Amount (BDT)"
    )
    is_paid    = models.BooleanField(default=False, verbose_name="Paid")
    razorpay_order_id   = models.CharField(max_length=120, blank=True, verbose_name="Razorpay Order ID")
    razorpay_payment_id = models.CharField(max_length=120, blank=True, verbose_name="Razorpay Payment ID")
    razorpay_signature  = models.CharField(max_length=255, blank=True, verbose_name="Razorpay Signature")
    donated_at = models.DateTimeField(auto_now_add=True, verbose_name="Submitted At")

    class Meta:
        ordering = ["-donated_at"]
        verbose_name = "Donation"
        verbose_name_plural = "Donation List"

    def __str__(self):
        status = "Paid" if self.is_paid else "Pending"
        return f"{self.name} ({self.student_id}) — BDT {self.amount} [{status}]"


class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ("PENDING",    "Pending"),
        ("APPROVED",   "Approved"),
        ("FULFILLED",  "Fulfilled"),
        ("REJECTED",   "Rejected"),
    ]

    student_id        = models.CharField(max_length=50, blank=True, verbose_name="Student ID")
    requester_name    = models.CharField(max_length=150, verbose_name="Requester Name")
    email             = models.EmailField(verbose_name="Email")
    phone             = models.CharField(max_length=20, verbose_name="Phone No.")
    blood_group       = models.CharField(
        max_length=4,
        choices=BLOOD_GROUP_CHOICES,
        verbose_name="Blood Group Needed",
    )
    units_required    = models.PositiveIntegerField(
        default=1,
        verbose_name="Units Required",
        help_text="Number of blood units needed"
    )
    reason            = models.CharField(
        max_length=200,
        verbose_name="Reason for Request",
        help_text="e.g., Surgery, Accident, Transfusion, etc."
    )
    urgency           = models.CharField(
        max_length=10,
        choices=[
            ("LOW",    "Low"),
            ("MEDIUM", "Medium"),
            ("HIGH",   "High"),
            ("URGENT", "Urgent"),
        ],
        default="MEDIUM",
        verbose_name="Urgency Level",
    )
    required_date     = models.DateField(verbose_name="Date Needed By")
    hospital_name     = models.CharField(
        max_length=200,
        verbose_name="Hospital/Clinic Name",
        help_text="Where the blood is needed"
    )
    hospital_contact  = models.CharField(
        max_length=200,
        verbose_name="Hospital Contact/Address",
    )
    requested_donor   = models.ForeignKey(
        'BloodDonation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests_received",
        verbose_name="Requested From Donor",
        help_text="If requesting from a specific donor"
    )
    notes             = models.TextField(
        blank=True,
        verbose_name="Additional Notes",
    )
    status            = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="Status",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Requested At")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Blood Request"
        verbose_name_plural = "Blood Requests"

    def __str__(self):
        return f"{self.requester_name} needs {self.blood_group} ({self.required_date})"


class BloodDonation(models.Model):
    STATUS_CHOICES = [
        ("PENDING",   "Pending"),
        ("APPROVED",  "Approved"),
        ("COMPLETED", "Completed"),
        ("REJECTED",  "Rejected"),
    ]

    student_id        = models.CharField(max_length=50, blank=True, verbose_name="Student ID")
    donor_name        = models.CharField(max_length=150, verbose_name="Donor Name")
    email             = models.EmailField(verbose_name="Email")
    phone             = models.CharField(max_length=20, verbose_name="Phone No.")
    blood_group       = models.CharField(
        max_length=4,
        choices=BLOOD_GROUP_CHOICES,
        verbose_name="Blood Group",
    )
    date_of_birth     = models.DateField(verbose_name="Date of Birth")
    weight            = models.PositiveIntegerField(verbose_name="Weight (kg)", help_text="Minimum 50 kg required")
    previous_donation = models.BooleanField(
        default=False,
        verbose_name="Have you donated blood before?",
    )
    health_condition  = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Any medical conditions?",
        help_text="e.g., diabetes, heart disease, etc."
    )
    message           = models.TextField(
        blank=True,
        verbose_name="Additional Message",
    )
    status            = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="Status",
    )
    created_at        = models.DateTimeField(auto_now_add=True, verbose_name="Submitted At")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Blood Donation"
        verbose_name_plural = "Blood Donations"

    def __str__(self):
        return f"{self.donor_name} ({self.blood_group}) — {self.created_at.strftime('%d %b %Y')}"


class LoginLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="login_logs",
    )
    username = models.CharField(max_length=150)
    date = models.DateField()
    time = models.TimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_verified = models.BooleanField(default=False, verbose_name="Verified")

    class Meta:
        ordering = ["-date", "-time"]
        verbose_name = "Login Log"
        verbose_name_plural = "Login Logs"

    def __str__(self):
        return f"{self.username} — {self.date} {self.time}"


class HelpDesk(models.Model):
    STAR_CHOICES = [(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]

    name         = models.CharField(max_length=150, verbose_name="Name")
    stars        = models.PositiveSmallIntegerField(
        choices=STAR_CHOICES,
        verbose_name="Rating",
    )
    message      = models.TextField(blank=True, verbose_name="Message")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Submitted At")

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Help Desk Feedback"
        verbose_name_plural = "Help Desk Feedback"

    def __str__(self):
        return f"{self.name} — {self.stars}★ ({self.submitted_at.strftime('%d %b %Y')})"


class DonorResponse(models.Model):
    RESPONSE_CHOICES = [
        ("PENDING",  "Pending"),
        ("ACCEPTED", "Accepted"),
        ("DECLINED", "Declined"),
    ]

    blood_request = models.ForeignKey(
        "BloodRequest",
        on_delete=models.CASCADE,
        related_name="donor_responses",
        verbose_name="Blood Request",
    )
    donor = models.ForeignKey(
        "BloodDonation",
        on_delete=models.CASCADE,
        related_name="responses",
        verbose_name="Donor",
    )
    token        = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    response     = models.CharField(
        max_length=10,
        choices=RESPONSE_CHOICES,
        default="PENDING",
        verbose_name="Response",
    )
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name="Responded At")

    class Meta:
        unique_together = ("blood_request", "donor")
        ordering = ["-blood_request__created_at"]
        verbose_name = "Donor Response"
        verbose_name_plural = "Donor Responses"

    def __str__(self):
        return f"{self.donor.donor_name} → {self.blood_request} [{self.response}]"


class TodaysAppointment(models.Model):
    STATUS_CHOICES = [
        ("PENDING",   "Pending Confirmation"),
        ("CONFIRMED", "Confirmed"),
        ("DECLINED",  "Declined"),
        ("EXPIRED",   "Expired"),
    ]

    appointment         = models.ForeignKey(
        "Appointment",
        on_delete=models.CASCADE,
        related_name="todays_appointments",
        verbose_name="Appointment",
    )
    confirmation_token  = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email_sent_at       = models.DateTimeField(null=True, blank=True, verbose_name="Email Sent At")
    response_deadline   = models.DateTimeField(verbose_name="Response Deadline")
    status              = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="Status",
    )
    responded_at        = models.DateTimeField(null=True, blank=True, verbose_name="Responded At")
    queue_position      = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Queue Position (FCFS)",
        help_text="Position in the queue after confirmation"
    )
    created_at          = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        ordering = ["appointment__created_at"]  # Order by original booking time (FCFS)
        verbose_name = "Today's Appointment"
        verbose_name_plural = "Today's Appointments"

    def __str__(self):
        return f"{self.appointment.student_name} - {self.appointment.appointment_date} [{self.status}]"

    def is_expired(self):
        """Check if the confirmation window has expired"""
        from django.utils import timezone
        return timezone.now() > self.response_deadline and self.status == "PENDING"


class DoctorLeave(models.Model):
    """Model to track doctor leaves and unavailable periods"""
    LEAVE_TYPE_CHOICES = [
        ("PERSONAL", "Personal Leave"),
        ("MEDICAL", "Medical Leave"),
        ("CONFERENCE", "Conference/Training"),
        ("EMERGENCY", "Emergency"),
        ("OTHER", "Other"),
    ]

    doctor = models.ForeignKey(
        "Doctor",
        on_delete=models.CASCADE,
        related_name="leaves",
        verbose_name="Doctor",
    )
    leave_date_from = models.DateField(verbose_name="Leave From")
    leave_date_to = models.DateField(verbose_name="Leave Till")
    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_TYPE_CHOICES,
        default="PERSONAL",
        verbose_name="Leave Type",
    )
    reason = models.TextField(blank=True, verbose_name="Reason")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-leave_date_from"]
        verbose_name = "Doctor Leave"
        verbose_name_plural = "Doctor Leaves"

    def __str__(self):
        return f"{self.doctor.name} - {self.leave_date_from} to {self.leave_date_to} ({self.get_leave_type_display()})"


class StudentNoShowRecord(models.Model):
    """Track no-show appointments for each student"""
    from app.models import StudentProfile

    student = models.OneToOneField(
        "StudentProfile",
        on_delete=models.CASCADE,
        related_name="no_show_record",
        verbose_name="Student",
    )
    total_no_shows = models.PositiveIntegerField(default=0, verbose_name="Total No-Shows")
    last_no_show_date = models.DateTimeField(null=True, blank=True, verbose_name="Last No-Show Date")
    is_restricted = models.BooleanField(default=False, verbose_name="Restricted from Booking")
    restriction_until = models.DateField(null=True, blank=True, verbose_name="Restriction Until")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student No-Show Record"
        verbose_name_plural = "Student No-Show Records"

    def __str__(self):
        return f"{self.student.student_id} - {self.total_no_shows} no-shows"


# Update Appointment model to add no-show tracking fields
# Add these fields to the Appointment model STATUS_CHOICES
