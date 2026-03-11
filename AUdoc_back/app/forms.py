from django import forms
from django.utils import timezone

from .models import (
    BLOOD_GROUP_CHOICES, MEDICAL_DEPT_CHOICES, STUDENT_DEPT_CHOICES,
    TIME_SLOT_CHOICES, Appointment, BloodRequest, BloodDonation, Doctor, Donation, StudentRegistration,
)


class StudentRegistrationForm(forms.Form):
    # ── Personal information ─────────────────────────────────
    first_name = forms.CharField(
        max_length=150,
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your first name"}),
    )
    last_name = forms.CharField(
        max_length=150,
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your last name"}),
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your university email"}),
    )

    # ── Student details ──────────────────────────────────────
    student_id = forms.CharField(
        max_length=50,
        label="Student ID",
        widget=forms.TextInput(attrs={"placeholder": "e.g. AU2021050123"}),
    )
    phone = forms.CharField(
        max_length=20,
        label="Phone Number",
        widget=forms.TextInput(attrs={"placeholder": "e.g. 01XXXXXXXXX"}),
    )
    emergency_contact = forms.CharField(
        max_length=20,
        label="Emergency Contact Number",
        widget=forms.TextInput(attrs={"placeholder": "Guardian/emergency contact"}),
    )
    department = forms.ChoiceField(
        choices=[("", "— Select your department —")] + list(STUDENT_DEPT_CHOICES),
        label="Academic Department",
    )
    blood_group = forms.ChoiceField(
        choices=[("", "— Select blood group —")] + list(BLOOD_GROUP_CHOICES),
        label="Blood Group",
    )
    home_address = forms.CharField(
        label="Home Address",
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Permanent / home address"}),
    )
    present_address = forms.CharField(
        label="Present Address",
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Current / on-campus address"}),
    )

    # ── Validation ───────────────────────────────────────────
    def clean_email(self):
        email = self.cleaned_data["email"]
        if StudentRegistration.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_student_id(self):
        student_id = self.cleaned_data["student_id"]
        if StudentRegistration.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("This Student ID is already registered.")
        return student_id

    def clean_department(self):
        dept = self.cleaned_data["department"]
        if not dept:
            raise forms.ValidationError("Please select your department.")
        return dept

    def clean_blood_group(self):
        bg = self.cleaned_data["blood_group"]
        if not bg:
            raise forms.ValidationError("Please select your blood group.")
        return bg


class AppointmentForm(forms.Form):
    student_id = forms.CharField(
        max_length=50,
        label="Student ID",
        widget=forms.TextInput(attrs={"placeholder": "e.g. AU2021050123"}),
    )
    student_name = forms.CharField(
        max_length=150,
        label="Full Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your full name"}),
    )
    phone = forms.CharField(
        max_length=20,
        label="Phone Number",
        widget=forms.TextInput(attrs={"placeholder": "e.g. 01XXXXXXXXX"}),
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )
    student_department = forms.ChoiceField(
        choices=[("", "— Select your department —")] + list(STUDENT_DEPT_CHOICES),
        label="Your Department",
    )
    medical_department = forms.ChoiceField(
        choices=[("", "— Select medical department —")] + list(MEDICAL_DEPT_CHOICES),
        label="Medical Department",
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_available=True),
        required=False,
        empty_label="— Any available doctor —",
        label="Preferred Doctor",
        help_text="Optional — leave blank and we will assign an available doctor.",
    )
    appointment_date = forms.DateField(
        label="Preferred Date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    appointment_time = forms.ChoiceField(
        choices=[("", "— Select a time slot —")] + list(TIME_SLOT_CHOICES),
        label="Preferred Time Slot",
    )
    problem_description = forms.CharField(
        label="Description of Problem",
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Briefly describe your symptoms or reason for visit"}),
    )

    def clean_student_department(self):
        dept = self.cleaned_data["student_department"]
        if not dept:
            raise forms.ValidationError("Please select your department.")
        return dept

    def clean_medical_department(self):
        dept = self.cleaned_data["medical_department"]
        if not dept:
            raise forms.ValidationError("Please select a medical department.")
        return dept

    def clean_appointment_date(self):
        date = self.cleaned_data["appointment_date"]
        if date < timezone.localdate():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return date

    def clean_appointment_time(self):
        slot = self.cleaned_data["appointment_time"]
        if not slot:
            raise forms.ValidationError("Please select a time slot.")
        return slot

    def clean(self):
        cleaned = super().clean()
        student_id = cleaned.get("student_id")
        appointment_date = cleaned.get("appointment_date")

        if student_id and appointment_date:
            if Appointment.objects.filter(
                student_id=student_id,
                appointment_date=appointment_date,
            ).exclude(status__in=["REJECTED", "CANCELLED"]).exists():
                self.add_error(
                    "appointment_date",
                    "You already have an appointment on this date. "
                    "Only one appointment per day is allowed.",
                )
        return cleaned


AMOUNT_CHOICES = [
    ("10",    "Rs 10"),
    ("25",    "Rs 25"),
    ("50",    "Rs 50"),
    ("75",    "Rs 75"),
    ("100",   "Rs 100"),
    ("other", "Other amount"),
]


class DonationForm(forms.Form):
    preset_amount = forms.ChoiceField(
        choices=[("", "— Select an amount —")] + AMOUNT_CHOICES,
        required=False,
        label="Donation Amount",
    )
    custom_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Custom Amount (Rs)",
        widget=forms.NumberInput(attrs={"placeholder": "Enter amount (Rs 10 – 100)", "min": "10", "max": "100", "step": "0.01"}),
    )
    message = forms.CharField(
        required=False,
        label="Message (optional)",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Leave a kind note…"}),
    )

    def clean(self):
        cleaned = super().clean()
        preset = cleaned.get("preset_amount")
        custom = cleaned.get("custom_amount")

        if not preset and not custom:
            raise forms.ValidationError("Please select or enter a donation amount.")

        if preset == "other":
            if not custom or custom <= 0:
                raise forms.ValidationError("Please enter a valid custom amount.")
            amount = custom
        elif preset:
            amount = forms.DecimalField().to_python(preset)
        else:
            if not custom or custom <= 0:
                raise forms.ValidationError("Please enter a valid custom amount.")
            amount = custom

        from decimal import Decimal
        if amount < Decimal("10"):
            raise forms.ValidationError("Minimum donation amount is Rs 10.")
        if amount > Decimal("100"):
            raise forms.ValidationError("Maximum donation amount is Rs 100.")

        cleaned["amount"] = amount
        return cleaned


class BloodDonationForm(forms.Form):
    donor_name = forms.CharField(
        max_length=150,
        label="Full Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your full name"}),
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )
    phone = forms.CharField(
        max_length=20,
        label="Phone Number",
        widget=forms.TextInput(attrs={"placeholder": "e.g. 01XXXXXXXXX"}),
    )
    blood_group = forms.ChoiceField(
        choices=[("", "— Select blood group —")] + list(BLOOD_GROUP_CHOICES),
        label="Blood Group",
    )
    date_of_birth = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    weight = forms.IntegerField(
        label="Weight (kg)",
        widget=forms.NumberInput(attrs={"placeholder": "e.g. 65", "min": "50"}),
        help_text="Minimum 50 kg required for blood donation",
    )
    previous_donation = forms.BooleanField(
        required=False,
        label="Have you donated blood before?",
    )
    health_condition = forms.CharField(
        max_length=200,
        required=False,
        label="Any Medical Conditions?",
        widget=forms.TextInput(attrs={"placeholder": "e.g., diabetes, heart disease, allergies, etc."}),
        help_text="Please mention if you have any health conditions",
    )
    message = forms.CharField(
        required=False,
        label="Additional Message (optional)",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Any additional information you'd like to share…"}),
    )

    def clean_blood_group(self):
        bg = self.cleaned_data["blood_group"]
        if not bg:
            raise forms.ValidationError("Please select your blood group.")
        return bg

    def clean_weight(self):
        weight = self.cleaned_data["weight"]
        if weight < 50:
            raise forms.ValidationError("Minimum weight required for blood donation is 50 kg.")
        return weight


class BloodRequestForm(forms.Form):
    requester_name = forms.CharField(
        max_length=150,
        label="Your Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your full name"}),
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )
    phone = forms.CharField(
        max_length=20,
        label="Phone Number",
        widget=forms.TextInput(attrs={"placeholder": "e.g. 01XXXXXXXXX"}),
    )
    blood_group = forms.ChoiceField(
        choices=[("", "— Select blood group needed —")] + list(BLOOD_GROUP_CHOICES),
        label="Blood Group Required",
    )
    units_required = forms.IntegerField(
        label="Units Required",
        widget=forms.NumberInput(attrs={"placeholder": "e.g. 1", "min": "1"}),
        help_text="Number of blood units needed",
    )
    reason = forms.CharField(
        max_length=200,
        label="Reason for Request",
        widget=forms.TextInput(attrs={"placeholder": "e.g., Surgery, Accident, Transfusion"}),
    )
    urgency = forms.ChoiceField(
        choices=[
            ("LOW",    "Low"),
            ("MEDIUM", "Medium"),
            ("HIGH",   "High"),
            ("URGENT", "Urgent"),
        ],
        label="Urgency Level",
        initial="MEDIUM",
    )
    required_date = forms.DateField(
        label="Date Needed By",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    hospital_name = forms.CharField(
        max_length=200,
        label="Hospital/Clinic Name",
        widget=forms.TextInput(attrs={"placeholder": "Name of the hospital or medical facility"}),
    )
    hospital_contact = forms.CharField(
        max_length=200,
        label="Hospital Contact/Address",
        widget=forms.TextInput(attrs={"placeholder": "Phone number or address"}),
    )
    notes = forms.CharField(
        required=False,
        label="Additional Notes (optional)",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Any additional information…"}),
    )

    def clean_blood_group(self):
        bg = self.cleaned_data["blood_group"]
        if not bg:
            raise forms.ValidationError("Please select the blood group required.")
        return bg

    def clean_units_required(self):
        units = self.cleaned_data["units_required"]
        if units < 1:
            raise forms.ValidationError("At least 1 unit is required.")
        return units

    def clean_required_date(self):
        date = self.cleaned_data["required_date"]
        if date < timezone.localdate():
            raise forms.ValidationError("Required date cannot be in the past.")
        return date
