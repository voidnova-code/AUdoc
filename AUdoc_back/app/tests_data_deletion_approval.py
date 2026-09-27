from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.signing import TimestampSigner
from django.core import mail
from app.models import Appointment, StudentRegistration, HelpDesk
import json

class DataDeletionApprovalTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.client = Client()
        self.client.login(username='admin', password='password123')
        
        # Create some test data
        StudentRegistration.objects.create(student_id="AU123", full_name="Test Student", phone="123", gender="Male", department="CSE")
        HelpDesk.objects.create(name="Test", phone="123", email="t@e.com", subject="Test", message="Test")

    def test_selective_delete_sends_email_without_deleting(self):
        post_data = {
            'confirmation': 'CONFIRMED_SELECTIVE_DELETE',
            'selected_data': 'registrations,feedback',
            'admin_password': 'password123',
            'reason': 'Testing selective delete approval'
        }
        
        # Ensure counts are 1
        self.assertEqual(StudentRegistration.objects.count(), 1)
        self.assertEqual(HelpDesk.objects.count(), 1)
        
        response = self.client.post(reverse('admin_clear_all_data'), post_data)
        
        # Verify redirects
        self.assertEqual(response.status_code, 302)
        
        # Row counts unchanged
        self.assertEqual(StudentRegistration.objects.count(), 1)
        self.assertEqual(HelpDesk.objects.count(), 1)
        
        # 1 email sent to the owner
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Data Deletion Confirmation Requested", mail.outbox[0].subject)

    def test_blank_reason_is_rejected(self):
        post_data = {
            'confirmation': 'CONFIRMED_SELECTIVE_DELETE',
            'selected_data': 'registrations',
            'admin_password': 'password123',
            'reason': '   ' # blank reason
        }
        
        response = self.client.post(reverse('admin_clear_all_data'), post_data)
        self.assertEqual(response.status_code, 302)
        
        # No email sent
        self.assertEqual(len(mail.outbox), 0)

    def test_confirm_selective_delete_with_valid_token(self):
        signer = TimestampSigner()
        payload = json.dumps({
            "action": "SELECTIVE_DELETE",
            "categories": ["registrations"],
            "requested_by_id": self.admin_user.id,
            "requested_by_email": self.admin_user.email,
            "reason": "Test"
        })
        token = signer.sign(payload)
        
        response = self.client.get(reverse('admin_confirm_clear_all_data', args=[token]))
        self.assertEqual(response.status_code, 302)
        
        # Registrations deleted, Feedback still exists
        self.assertEqual(StudentRegistration.objects.count(), 0)
        self.assertEqual(HelpDesk.objects.count(), 1)
        
        # Notification email to admin
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("approved", mail.outbox[0].subject)

    def test_expired_token(self):
        signer = TimestampSigner()
        payload = json.dumps({
            "action": "SELECTIVE_DELETE",
            "categories": ["registrations"],
            "requested_by_id": self.admin_user.id,
            "requested_by_email": self.admin_user.email,
            "reason": "Test"
        })
        # Hack to simulate expired token
        import time
        from django.core import signing
        
        # Create a manually signed token that is expired
        value = signing.b64_encode(payload.encode()).decode()
        timestamp = signing.b62_encode(int(time.time()) - 3601)
        val = f"{value}{signer.sep}{timestamp}"
        signature = signer.signature(val)
        token = f"{val}{signer.sep}{signature}"
        
        response = self.client.get(reverse('admin_confirm_clear_all_data', args=[token]))
        self.assertEqual(response.status_code, 302)
        
        # Nothing deleted
        self.assertEqual(StudentRegistration.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_decline_data_action(self):
        signer = TimestampSigner()
        payload = json.dumps({
            "action": "SELECTIVE_DELETE",
            "categories": ["registrations"],
            "requested_by_id": self.admin_user.id,
            "requested_by_email": self.admin_user.email,
            "reason": "Test decline"
        })
        token = signer.sign(payload)
        
        response = self.client.get(reverse('admin_decline_data_action', args=[token]))
        self.assertEqual(response.status_code, 302)
        
        # Nothing deleted
        self.assertEqual(StudentRegistration.objects.count(), 1)
        
        # 1 email sent to notify the requester of decline
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("declined", mail.outbox[0].subject)

    def test_full_wipe_flow_legacy(self):
        # Create student user
        User.objects.create_user(username='student', password='abc', is_staff=False, is_superuser=False)
        self.assertEqual(User.objects.count(), 2) # admin + student
        
        # Legacy bare string token
        signer = TimestampSigner()
        token = signer.sign("DELETE_ALL_STUDENT_DATA")
        
        response = self.client.get(reverse('admin_confirm_clear_all_data', args=[token]))
        
        # Everything deleted
        self.assertEqual(StudentRegistration.objects.count(), 0)
        self.assertEqual(HelpDesk.objects.count(), 0)
        self.assertEqual(User.objects.count(), 1) # only admin remains
