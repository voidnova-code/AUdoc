# AUdoc Campus Healthcare Portal Workflow

This document provides a structured workflow and architectural overview of the **AUdoc** project based on the codebase analysis. AUdoc is a campus health management system designed for Assam University Silchar, built with a Django backend and a Flutter frontend.

## 🏗️ Architecture Overview

The system operates on a client-server architecture:
- **Backend**: Django 6.0.3 providing a REST API (via Django REST Framework) and server-side rendered pages for the admin panel and public web interface.
- **Frontend**: A Flutter cross-platform mobile application (currently under development for deep integration) that communicates with the Django backend.
- **Database**: PostgreSQL for production (deployed on Render) and SQLite for local development.

### Core Technologies
- **Auth**: Passwordless OTP authentication via email (Resend).
- **Payment**: Razorpay integration for monetary donations.
- **AI**: Groq API integration for the healthcare chatbot.
- **Background Tasks**: Scheduled management commands for daily operations.

---

## 🔄 Core Workflows

### 1. Authentication & Registration Workflow
The system employs a passwordless, OTP-based authentication model to enhance user experience and security.

1. **New User Registration**:
   - Student submits their details (ID, Name, Dept, Blood Group, etc.).
   - An OTP is generated (`security.py`) and sent to their email.
   - Upon OTP verification, the registration enters a `PENDING` state.
   - Admin reviews the application in the dashboard and approves it.
   - A `StudentProfile` is created, and a welcome email is dispatched.

2. **Login Flow**:
   - Student enters their Student ID or Email.
   - System validates the user and sends a cryptographically secure OTP via email.
   - Student enters the OTP within the 5-minute validity window.
   - System verifies the OTP (using constant-time comparison to prevent timing attacks) and establishes a secure session or returns a JWT for the mobile app.

### 2. Doctor Appointment Workflow (FCFS)
The appointment system uses a First-Come, First-Serve (FCFS) queue mechanism for fair daily scheduling.

1. **Booking**:
   - Student selects a medical department (e.g., General, Dental) and a specific doctor.
   - Student chooses a preferred date and time slot and submits the problem description.
   - Appointment is created with a `PENDING` status.

2. **Daily Confirmation (Background Task)**:
   - At 8:00 AM every day, a cron job (`send_appointment_confirmations.py`) runs.
   - It identifies all pending appointments for the current day.
   - An email is sent to patients with a unique confirmation link (valid for a 2-hour window).

3. **Queue Assignment**:
   - Patients click the link to confirm or decline.
   - Upon confirmation, they are assigned a `queue_position` in the `TodaysAppointment` record based on who confirmed first (FCFS).

4. **No-Show Handling**:
   - If a student misses a confirmed appointment, they are marked as a no-show.
   - A `StudentNoShowRecord` tracks offenses, eventually restricting booking privileges if abused.

### 3. Blood Bank Workflow
The blood bank module acts as a decentralized registry connecting donors with those in need.

1. **Donation Pledge**:
   - Students register as donors (`BloodDonation`), providing blood group, weight, and health conditions.
   - The admin reviews and approves the donor profile.

2. **Blood Request**:
   - A user submits a `BloodRequest` specifying the required blood group, urgency level (Low to Urgent), and hospital details.
   - The request can be broadcasted or targeted at a specific registered donor.

3. **Fulfillment**:
   - Matched donors receive an email notification about the request.
   - Donors can accept or decline the request via a secure token link (`DonorResponse`).
   - Once a donor accepts, contact details are shared to facilitate the actual donation.

### 4. Monetary Donation Workflow
Allows users to financially support the health center.

1. **Initiation**: User specifies an amount in INR.
2. **Order Creation**: Backend creates a Razorpay order via the Razorpay API.
3. **Payment Processing**: The client processes the payment using the Razorpay checkout interface.
4. **Verification**: Backend verifies the Razorpay signature to ensure payment authenticity and marks the `Donation` record as `Paid`.

### 5. Admin & Management Workflow
The admin panel is a custom-built, modern dashboard replacing the default Django admin.

- **Real-time Monitoring**: Admins can view live statistics, appointment trends, and blood group distributions.
- **Quick Actions**: One-click approval/rejection for student registrations and blood requests.
- **Staff/Doctor Management**: Add, update, and manage doctor availability, leave periods, and staff access.
- **Data Export**: Export records (appointments, users, donations) to CSV/Excel formats for external reporting.

---

## 🗄️ Key Data Models
- `StudentProfile`: Extended user data linked to Django's Auth User.
- `Doctor` & `StaffProfile`: Management of medical and administrative personnel.
- `Appointment` & `TodaysAppointment`: Core scheduling and FCFS queue management.
- `BloodDonation`, `BloodRequest`, `DonorResponse`: The blood bank ecosystem.
- `Donation`: Tracks financial contributions.
- `HelpDesk`: User feedback and ratings.

## 🚀 Deployment Pipeline
1. **Source Control**: GitHub repository with main branch tracking production.
2. **Hosting**: Render Web Services.
3. **Build Step**: Executes `render_build.sh` (installs dependencies via `pip`, runs `collectstatic`).
4. **Start Step**: Executes `render_start.sh` (runs database migrations, creates default superuser, and starts Gunicorn server).
