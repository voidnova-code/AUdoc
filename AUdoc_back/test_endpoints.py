import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AUdoc_back.settings")
django.setup()

from django.test import Client
from django.urls import reverse
import uuid

def run_tests():
    client = Client()
    print("Testing endpoints...")
    
    # Static GET endpoints
    get_urls = [
        ('home', {}),
        ('register', {}),
        ('student_login', {}),
        # appointment requires login, so it should redirect to login (302)
        ('appointment', {}),
        ('donation', {}),
        ('blood_bank', {}),
        ('about', {}),
        ('admin_dashboard', {}), # likely redirect or 403
    ]
    
    for url_name, kwargs in get_urls:
        try:
            url = reverse(url_name, kwargs=kwargs)
            response = client.get(url, SERVER_NAME='127.0.0.1')
            print(f"OK GET {url} -> {response.status_code}")
        except Exception as e:
            print(f"ERROR GET {url_name} -> ERROR: {e}")

    # Test dynamic endpoints
    try:
        # Generate a dummy UUID token for testing the confirmation endpoint
        dummy_token = uuid.uuid4()
        url = reverse('appointment_confirm', kwargs={'token': dummy_token, 'action': 'accept'})
        response = client.get(url, SERVER_NAME='127.0.0.1')
        print(f"OK GET {url} -> {response.status_code}")
    except Exception as e:
        print(f"ERROR GET appointment_confirm -> ERROR: {e}")

if __name__ == "__main__":
    from django.conf import settings
    settings.ALLOWED_HOSTS.append('127.0.0.1')
    run_tests()
