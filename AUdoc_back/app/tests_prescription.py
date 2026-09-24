from django.test import TestCase, Client
from django.urls import reverse
from app.models import (
    Appointment, MedicalHistory, Medicine, MedicineStock, PrescribedMedicine,
    User, Doctor
)
from django.utils import timezone
import json

class PrescriptionDataCaptureTests(TestCase):
    def setUp(self):
        # Create an admin user to access the dashboard
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.client = Client()
        
        # Create doctor
        self.doctor = Doctor.objects.create(
            name="Dr. Smith",
            specialization="General",
            is_available=True
        )
        
        # Create appointment
        self.appointment = Appointment.objects.create(
            student_id="AU123",
            student_name="Test Student",
            phone="1234567890",
            email="test@example.com",
            student_department="CSE",
            medical_department="General",
            appointment_date=timezone.now().date(),
            doctor=self.doctor,
            status="PENDING"
        )
        
        # Create medicine and stock
        self.medicine = Medicine.objects.create(
            name="Paracetamol",
            generic_name="Acetaminophen",
            unit="Tablets",
            pack_size=10
        )
        self.stock = MedicineStock.objects.create(
            medicine=self.medicine,
            batch_number="BATCH001",
            quantity=100,
            expiry_date=timezone.now().date() + timezone.timedelta(days=365)
        )

    def test_modal_renders_with_json_catalog(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('admin_dashboard') + '?tab=todays-appointments')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'rxMedicineCatalog')
        self.assertContains(response, 'Paracetamol')

    def test_full_structured_prescription_saves_and_deducts_stock(self):
        self.client.login(username='admin', password='password123')
        
        prescription_data = [
            {
                "medicine_id": self.medicine.id,
                "quantity": 15,
                "dosage": "500mg",
                "take_morning": True,
                "take_afternoon": False,
                "take_evening": True,
                "take_night": False,
                "food_timing": "AFTER",
                "duration_days": 7,
                "route": "ORAL",
                "instructions": "Take with water"
            }
        ]
        
        post_data = {
            'appointment_id': self.appointment.id,
            'illness': 'Fever',
            'symptoms': 'High temperature',
            'prescription_data': json.dumps(prescription_data)
        }
        
        response = self.client.post(reverse('save_medical_history'), post_data)
        self.assertEqual(response.status_code, 302) # Redirects on success
        
        # Verify history created
        history = MedicalHistory.objects.filter(student_id="AU123").first()
        self.assertIsNotNone(history)
        self.assertEqual(history.illness, 'Fever')
        
        # Verify prescribed medicine
        pm = PrescribedMedicine.objects.filter(medical_history=history).first()
        self.assertIsNotNone(pm)
        self.assertEqual(pm.quantity, 15)
        self.assertEqual(pm.dosage, "500mg")
        self.assertTrue(pm.take_morning)
        self.assertEqual(pm.food_timing, "AFTER")
        self.assertEqual(pm.duration_days, 7)
        self.assertEqual(pm.route, "ORAL")
        
        # Verify stock deducted
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 85) # 100 - 15

    def test_out_of_range_values_clamped(self):
        self.client.login(username='admin', password='password123')
        
        prescription_data = [
            {
                "medicine_id": self.medicine.id,
                "quantity": 5000, # Should clamp to 1000
                "duration_days": 150, # Should clamp to 90
                "food_timing": "INVALID_FOOD", # Should fallback to AFTER
                "route": "INVALID_ROUTE" # Should fallback to ORAL
            }
        ]
        
        post_data = {
            'appointment_id': self.appointment.id,
            'illness': 'Fever',
            'symptoms': 'High temperature',
            'prescription_data': json.dumps(prescription_data)
        }
        
        self.client.post(reverse('save_medical_history'), post_data)
        
        pm = PrescribedMedicine.objects.last()
        self.assertEqual(pm.quantity, 1000)
        self.assertEqual(pm.duration_days, 90)
        self.assertEqual(pm.food_timing, "AFTER")
        self.assertEqual(pm.route, "ORAL")

    def test_unknown_medicine_ids_skipped(self):
        self.client.login(username='admin', password='password123')
        
        prescription_data = [
            {
                "medicine_id": 9999, # Unknown
                "quantity": 10
            },
            {
                "medicine_id": self.medicine.id, # Valid
                "quantity": 5
            }
        ]
        
        post_data = {
            'appointment_id': self.appointment.id,
            'illness': 'Cold',
            'symptoms': 'Cough',
            'prescription_data': json.dumps(prescription_data)
        }
        
        self.client.post(reverse('save_medical_history'), post_data)
        
        history = MedicalHistory.objects.last()
        pms = PrescribedMedicine.objects.filter(medical_history=history)
        
        # Should only have 1 valid prescription
        self.assertEqual(pms.count(), 1)
        self.assertEqual(pms.first().medicine, self.medicine)

    def test_generate_png_and_email(self):
        # Feature C test
        from app.prescription_render import generate_prescription_png
        history = MedicalHistory.objects.create(
            student_id="AU123",
            doctor_name="Dr. Smith",
            illness="Test",
            symptoms="Test"
        )
        PrescribedMedicine.objects.create(
            medical_history=history,
            medicine=self.medicine,
            quantity=5
        )
        png_bytes = generate_prescription_png(history)
        self.assertIsInstance(png_bytes, bytes)
        self.assertTrue(png_bytes.startswith(b'\x89PNG'))
