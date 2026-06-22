<div align="center">

```
    ╔═══════════════════════════════════════════════════╗
    ║   █████╗ ██╗   ██╗██████╗  ██████╗  ██████╗      ║
    ║  ██╔══██╗██║   ██║██╔══██╗██╔═══██╗██╔════╝      ║
    ║  ███████║██║   ██║██║  ██║██║   ██║██║           ║
    ║  ██╔══██║██║   ██║██║  ██║██║   ██║██║           ║
    ║  ██║  ██║╚██████╔╝██████╔╝╚██████╔╝╚██████╗      ║
    ║  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝  ╚═════╝      ║
    ╚═══════════════════════════════════════════════════╝
```

# 🏥 AUdoc — Campus Healthcare Portal

### *Because "I Googled my symptoms" is NOT a treatment plan.*
### *(And because voidnova got tired of students calling the health center like it's 1995)*

**The official campus health management system for Assam University Silchar — built by someone who actually cares**

[![Django](https://img.shields.io/badge/Django-6.0.3-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-ff1709?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Dart](https://img.shields.io/badge/Dart-3.x-0175C2?style=for-the-badge&logo=dart&logoColor=white)](https://dart.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Security](https://img.shields.io/badge/Security-Hardened-success?style=for-the-badge&logo=shield&logoColor=white)](#-security)
[![Sleep Deprivation](https://img.shields.io/badge/Sleep-Optional-red?style=for-the-badge)](#-important-notes)

[✨ Features](#-features) · [🛠️ Tech Stack](#️-tech-stack) · [🔒 Security](#-security) · [📁 Structure](#️-project-structure) · [⚡ Quick Start](#-getting-started) · [🗺️ API Routes](#️-url-routes) · [🎛️ Admin Panel](#️-modern-admin-panel)

</div>

---

## 🩺 What Is AUdoc?

**Tired of wandering the hallways looking for the campus doctor while feeling like death warmed over?**

Welcome to the 21st century. 🚀

AUdoc is a full-stack **campus healthcare management system** built for **Assam University Silchar** by someone (voidnova) who realized that making students call the health center on a landline was objectively criminal.

**Features that'll make you wonder why we didn't have this sooner:**
- 📅 Book doctor appointments without a phone call
- 🩸 Donate blood (be a hero, but digitally)
- 💬 AI Chatbot that actually helps (unlike WebMD, which will convince you that you're dying)
- 💸 Donate money to the health center (even ₹10 counts!)
- 📊 Check your appointment history without asking a human

> *"A student needed to book a doctor appointment. The existing system was... a phone call. In 2025.*  
> *No further questions. voidnova took this personally."* — Internal memo, circa 2024

The system has two layers working together:
- 🐍 **Django Web Backend** — Fully functional, actually works, no "brb coffee break" 
- 📱 **Flutter Mobile App** — Beautiful UI that'll make you forget you're sick (almost)

---

## ✨ Features

### For Students 🎓 *(AKA: People Who Don't Want to Call Anyone)*

| Feature | What it does | Status | voidnova's Note |
|---------|-------------|--------|--------------|
| 🔐 **Passwordless Login** | Student ID + OTP to email. No forgotten passwords. Ever. | ✅ Live | Finally, no more "I forgot my password" emails |
| 📋 **Self Registration** | Sign up, verify email via OTP, get approved by admin | ✅ Live | Rejected students cry less this way |
| 📅 **Doctor Appointments** | Book 30-min slots across 8 specialties | ✅ Live | No more "can you squeeze me in?" calls |
| 📧 **Smart Confirmations** | Morning email confirmations with 2-hour response window | ✅ Live | We're not mind readers, please respond |
| 🎫 **FCFS Queue System** | First Come, First Serve queue assignment | ✅ Live | Fairness is underrated, apparently |
| 🩸 **Blood Bank** | Donate blood, request blood, or target a specific donor | ✅ Live | Be a hero (we'll even bribe you... I mean thank you) |
| 💬 **AI Chatbot** | Get instant answers about campus health services | ✅ Live | It won't tell you that you're dying (looking at you, WebMD) |
| 💸 **Donations** | Support the health center financially | ✅ Live | Even ₹10 counts! (voidnova accepts UPI too) |
| 📊 **Appointment History** | Track all past visits | ✅ Live | Proof that you actually went to the doctor |
| ⭐ **Help Desk Feedback** | Rate your experience | ✅ Live | Roast us gently, please |
| 📱 **Mobile App** | Cross-platform app (basically everywhere) | 🚧 In Progress | *voidnova is sleeping more these days* |

### The 8 Medical Specialties 🩺

`General` · `Dental` · `Eye Care` · `Mental Health` · `Orthopedics` · `Dermatology` · `Gynecology` · `Physiotherapy`

*(Yes, Mental Health is on the list. We know voidnova needs it after all-nighters.)*

### For Admins ⚙️ *(AKA: The Brave Souls Managing Everything)*

| Feature | Description | Why You'll Love It |
|---------|-------------|-------------------|
| 🎨 **Modern Admin Panel** | Glass-morphism UI with dark/light mode | Your eyes won't melt at 3 AM |
| 📊 **Interactive Dashboard** | Real-time stats, charts, and indicators | Look important in meetings |
| 📈 **Live Charts** | Appointment & blood group trends | Impress non-technical people |
| ⚡ **Quick Actions** | Priority buttons with keyboard shortcuts | voidnova doesn't believe in mice |
| 🎫 **FCFS Queue View** | Today's appointments in order | No chaos (that comes later) |
| ✅ **Registration Workflow** | Approve/reject with one click | Your approval email is instant, so they can't say "I didn't see it" |
| 👨‍⚕️ **Doctor Management** | Manage docs, specialties, availability | Control the chaos |
| 👥 **Staff Management** | Add and manage staff | No more "who's working today?" calls |
| 🩸 **Blood Bank Admin** | Donor registrations with urgency levels | URGENT = I really need this |
| 📊 **Login Audit Log** | Every login timestamped with IP | Big Brother is watching (jk, it's just logs) |
| 🔍 **Smart Search & Filters** | Instant search across registrations & blood donors | Find any student or donor in real-time |
| 📤 **Export Data** | Download as CSV/Excel | Flex on Excel spreadsheet people |
| 📱 **Mobile Responsive** | Works on all devices | Even your ancient tablet |

---

## 🔐 How the Auth Flow Works

```
  Student                     System                     Admin (voidnova)
    │                            │                          │
    │──── Enter Student ID ─────>│                          │
    │<─── OTP sent to email ─────│                          │ ← This is why your inbox is flooded
    │──── Enter OTP ────────────>│ (rate limited + secure)  │
    │<─── Logged in! ────────────│                          │
    │                            │                          │
    │   (First time? Register!)  │                          │
    │──── Fill reg form ────────>│                          │
    │     + email OTP verify     │                          │
    │                            │──── Pending queue ──────>│ ← voidnova reads this
    │                            │<─── Approve/Reject ───────│ ← voidnova approves this
    │<─── Welcome email! ────────│  (auto-provisions account)│
```

**No passwords.** No "Forgot password?" links at 2 AM. Just vibes and OTPs. ✌️

> 🔒 **Security Note:** OTPs are generated using cryptographically secure random numbers, validated with constant-time comparison (timing-attack resistant), and rate-limited so brute force attackers give up out of sheer frustration.

---

## 🔒 Security *(Because We're Not Monsters)*

AUdoc takes security seriously. The application has been hardened against common web vulnerabilities because voidnova doesn't want to wake up at 3 AM to a data breach notification.

### Security Features

| Feature | Protection Against | Status | voidnova's Confidence Level |
|---------|-------------------|--------|--------------------------|
| 🛡️ **Rate Limiting** | Brute force attacks on login/OTP | ✅ Active | 9/10 (unless someone is REALLY persistent) |
| 🔐 **Secure OTP** | Cryptographically secure random generation | ✅ Active | 10/10 (Python's `secrets` module ftw) |
| ⏱️ **Timing Attack Protection** | Constant-time OTP comparison | ✅ Active | 10/10 (zero nanoseconds given to attackers) |
| 🚫 **SQL Injection** | Parameterized queries via Django ORM | ✅ Protected | 10/10 (Django does the heavy lifting) |
| 🔄 **CSRF Protection** | All state-changing operations require tokens | ✅ Active | 10/10 (automatic, because voidnova is lazy) |
| 🍪 **Secure Cookies** | HttpOnly, SameSite, Secure flags | ✅ Active | 10/10 (cookies are actually secure) |
| 🔒 **Security Headers** | X-Frame-Options, CSP, HSTS, XSS filter | ✅ Active | 9/10 (some configs are still evolving) |
| 🔑 **Argon2 Hashing** | Memory-hard password hashing algorithm | ✅ Active | 10/10 (even quantum computers will struggle) |
| 📝 **Security Logging** | Failed login attempts, rate limit violations | ✅ Active | 8/10 (logs are there, but who reads them?) |

### Rate Limits *(To Stop You From Breaking Things)*

| Endpoint | Limit | Window | Why? |
|----------|-------|--------|------|
| OTP Send | 5 requests | 5 minutes | So you don't spam your inbox with OTPs |
| Login | 10 requests | 5 minutes | Attackers give up. We've seen it happen. |
| API | 100 requests | 1 minute | Be nice to the server. It has feelings. |

### Security Configuration *(DO THIS OR SAYAN WILL CRY)*

For production deployment, ensure these environment variables are set:

```env
# Security (REQUIRED for production — trust us)
DJANGO_SECRET_KEY=<generate-strong-random-key-seriously-not-password123>
DJANGO_DEBUG=False              # If you set this to True in production, we WILL judge you
DJANGO_ALLOWED_HOSTS=yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com
DJANGO_SECURE_SSL_REDIRECT=True
```

> 📄 For complete security documentation, see [`AUdoc_back/SECURITY.md`](AUdoc_back/SECURITY.md)
>
> 💡 **Pro Tip:** Generate your SECRET_KEY with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` — not with "password123"

---

## 🗂️ Project Structure

```
AUdoc/
│
├── 📂 AUdoc_back/                   # 🐍 Django backend (the brain)
│   ├── 📂 AUdoc_back/               # Project configuration
│   │   ├── settings.py              # App settings (secrets via .env 🤫)
│   │   ├── urls.py                  # Root URL router
│   │   └── wsgi.py / asgi.py        # Deployment entry points
│   │
│   ├── 📂 app/                      # The main application
│   │   ├── models.py                # 12 database models
│   │   ├── views.py                 # Views + AJAX endpoints
│   │   ├── forms.py                 # Django forms
│   │   ├── admin.py                 # Customized admin with auto-provisioning
│   │   ├── security.py              # 🔒 Security utilities (rate limiting, OTP)
│   │   ├── backends.py              # Custom OTP authentication backend
│   │   ├── signals.py               # Login audit signal handler
│   │   ├── urls.py                  # App URL routes
│   │   ├── 📂 templates/app/        # HTML templates
│   │   └── 📂 management/commands/  # Custom Django commands
│   │       ├── send_appointment_confirmations.py
│   │       └── cleanup_todays_appointments.py
│   │
│   ├── 📂 media/                    # Uploaded files (doctor photos)
│   ├── SECURITY.md                  # 📄 Security documentation
│   ├── .env.example                 # 👈 Copy this to .env and add your secrets
│   ├── requirements.txt             # Python dependencies
│   ├── manage.py                    # Django management CLI
│   └── db.sqlite3                   # Local database (gitignored)
│
├── 📂 audoc/                        # 📱 Flutter frontend (the face)
│   ├── 📂 lib/
│   │   ├── main.dart                # App entry point
│   │   └── 📂 student_pages/
│   │       ├── home_page.dart       # Home with doctors & specialties
│   │       ├── appointment_page.dart         # Tabbed appointment list
│   │       └── book_appointment_page.dart    # Booking flow
│   └── pubspec.yaml                 # Flutter dependency manifest
│
├── .gitignore                       # What stays local, stays local 🤫
└── README.md                        # You are here 📍
```

---

## 🛠️ Tech Stack *(Or: How voidnova Stayed Awake)*

```
┌──────────────────┬──────────────────────────────────────────────┐
│  Backend         │  Django 6.0.3  ·  Python 3.12                │
│  API Framework   │  Django REST Framework 3.16.1                │
│  Mobile/Desktop  │  Flutter  ·  Dart SDK ^3.11.1                │
│  Database        │  PostgreSQL (Render)  ·  SQLite (dev)        │
│  Authentication  │  Custom OTP-based (no passwords = less pain)  │
│  Email           │  Resend  ·  TLS  ·  Free tier + custom domain│
│  Charts          │  Chart.js (make stats look pretty)           │
│  UI Theme        │  Material Design 3  ·  Glass-morphism vibes  │
│  Admin Panel     │  Custom UI (voidnova's pride and joy)           │
│  AI Chatbot      │  Groq API (free, surprisingly good)          │
│  Payments        │  Razorpay (accepts money, ironically)        │
└──────────────────┴──────────────────────────────────────────────┘
```

---

## 🏛️ Database Models

| Model | Purpose |
|-------|---------|
| `StudentProfile` | Approved student records linked to auth users |
| `StaffProfile` | Campus staff & doctor directory |
| `Doctor` | Doctors with specialties, availability slots & profile photos |
| `Appointment` | Bookings (PENDING → CONFIRMED → COMPLETED) |
| `TodaysAppointment` | Daily confirmations with FCFS queue positions |
| `StudentRegistration` | Applications awaiting admin approval |
| `Donation` | Monetary donation pledges (INR) |
| `BloodDonation` | Blood donor registry with health screening |
| `BloodRequest` | Blood requests with urgency (LOW / MEDIUM / HIGH / URGENT) |
| `DonorResponse` | Track donor accept/decline responses |
| `HelpDesk` | User feedback with star ratings |
| `LoginLog` | Security audit trail — every login, timestamped |

---

## 🌐 URL Routes

> Django serves server-side rendered HTML. Several endpoints are AJAX (return JSON).

### Public Routes

| Method | URL | Description |
|--------|-----|-------------|
| `GET/POST` | `/` | Home — top doctors, donor spotlights |
| `GET/POST` | `/register/` | Student registration + email OTP verification |
| `POST` | `/send-otp/` | **[AJAX]** Send OTP for registration |
| `POST` | `/student-login/` | Validate OTP and log student in |
| `POST` | `/send-login-otp/` | **[AJAX]** Send OTP for login |
| `GET/POST` | `/donation/` | Submit a monetary donation |
| `GET/POST` | `/blood-bank/` | Blood donation or request (tabbed UI) |
| `GET` | `/blood-donors/` | Filterable blood donor directory |
| `GET` | `/blood/respond/<token>/<action>/` | Donor accept/decline blood request |
| `GET` | `/about/` | About page |

### Authenticated Routes

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| `GET/POST` | `/appointment/` | ✅ Login | Book & view appointments |
| `GET` | `/appointment/confirm/<token>/<action>/` | ✅ | Confirm/decline appointment |
| `POST` | `/chat/` | ✅ | **[AJAX]** AI Chatbot API |

### Admin Panel Routes

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/manage/` | Modern admin dashboard |
| `GET` | `/manage/stats/` | **[AJAX]** Real-time statistics |
| `GET` | `/manage/chart-data/` | **[AJAX]** Chart data (appointments/blood groups) |
| `POST` | `/manage/registration/<pk>/action/` | Approve/reject registration |
| `POST` | `/manage/appointment/<pk>/status/` | Update appointment status |
| `POST` | `/manage/blood-donation/<pk>/status/` | Update blood donation status |
| `POST` | `/manage/blood-request/<pk>/status/` | Update blood request status |
| `POST` | `/manage/donation/<pk>/toggle-paid/` | Toggle donation paid status |
| `POST` | `/manage/doctor/save/` | Add/edit doctor |
| `DELETE` | `/manage/doctor/<pk>/delete/` | Delete doctor |
| `POST` | `/manage/staff/save/` | Add/edit staff |
| `DELETE` | `/manage/staff/<pk>/delete/` | Delete staff |
| `POST` | `/manage/clear-all-data/` | Clear all data (danger!) |

---

## ⚡ Getting Started

### Prerequisites *(No Excuses)*

Make sure you have these installed — no "I don't have Python" allowed:

- 🐍 **Python 3.12+** — [python.org](https://python.org) — If you don't have it, your computer is outdated
- 🐦 **Flutter 3.x** — [flutter.dev](https://flutter.dev/docs/get-started/install) — Optional if you only want the web version
- 📧 **Gmail with App Password** — [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) — No, you can't use your main password (don't be silly)
- **Git** — You clearly already have it if you're reading this 😄

---

### 🐍 Backend Setup (Django) *(The Actual Work Begins)*

```bash
# 1. Clone the repo
git clone https://github.com/voidnova-code/AUdoc.git
cd AUdoc/AUdoc_back

# 2. Create and activate a virtual environment
python -m venv myenv
myenv\Scripts\activate      # Windows (if you're one of those people)
source myenv/bin/activate   # macOS / Linux (the superior choice)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your secrets
cp .env.example .env
# Open .env and fill in your Django secret key + Gmail credentials
# (Yes, that DJANGO_SECRET_KEY thing is important. Very important.)

# 5. Apply database migrations
python manage.py migrate

# 6. Create a superuser (for the admin panel)
python manage.py createsuperuser
# Username: admin
# Password: Make it stronger than "password123"

# 7. Start the server!
python manage.py runserver
```

Visit 👉 `http://127.0.0.1:8000` — if you see a page, congratulations. You didn't break anything.

Admin panel 👉 `http://127.0.0.1:8000/manage/` (Modern UI designed by voidnova who probably needs sleep)

Django admin 👉 `http://127.0.0.1:8000/admin/` (The boring one, but it works)

---

### 📱 Flutter App Setup

```bash
cd AUdoc/audoc

# Get dependencies
flutter pub get

# Run on your connected device or emulator
flutter run
```

---

### 🔑 Environment Variables

Create the file `AUdoc_back/.env` (it's in `.gitignore`, your secrets are safe):

#### For Development (SQLite):
```env
DJANGO_SECRET_KEY=your-super-long-random-secret-key-here
RESEND_API_KEY=re_your_resend_api_key_here
DEFAULT_FROM_EMAIL=onboarding@resend.dev
GROQ_API_KEY=your_groq_api_key_for_chatbot
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

#### For Production (PostgreSQL on Render):
```env
DJANGO_SECRET_KEY=your-super-long-random-secret-key-here
DJANGO_DEBUG=False
DATABASE_URL=postgresql://user:password@host:5432/dbname
RESEND_API_KEY=re_your_resend_api_key_here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
GROQ_API_KEY=your_groq_api_key_for_chatbot
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

> ⚠️ **Never commit `.env` to git.** It's gitignored for a reason. We are not animals.
>
> 💡 **Resend API Key:** Get it from [resend.com/api-keys](https://resend.com/api-keys)
>
> 💡 **Groq API Key:** Get free tier at [console.groq.com](https://console.groq.com)

---

## 🎛️ Modern Admin Panel

The admin panel has been completely redesigned with a modern glass-morphism UI!

### ✨ Features

| Feature | Description |
|---------|-------------|
| 🎨 **Glass-morphism UI** | Modern translucent interface with backdrop blur |
| 🌗 **Dark/Light Mode** | Toggle button with smooth transitions |
| 📊 **Interactive Charts** | Line charts & doughnut charts with real data |
| 📈 **Real-time Stats** | Auto-refresh every 30 seconds |
| 🎫 **FCFS Queue View** | Today's appointments in queue order |
| 🔍 **Smart Search & Filters** | Instant client-side search for registrations & blood donors |
| ⚡ **Quick Actions** | Priority-based action buttons with stats and keyboard shortcuts |
| 📱 **Mobile Responsive** | Works on all devices |

### Quick Actions

The enhanced Quick Actions section provides:
- **Priority Alert** — Shows pending registrations and appointments count
- **Primary Actions** — 3 main buttons with gradient backgrounds and live stats:
  - Registrations (green) — View pending student registrations
  - Today's Queue (success green) — Access FCFS queue for today's appointments
  - Blood Bank (red) — Manage blood donations and requests
- **Secondary Actions** — 2x2 grid of quick access buttons for Blood Requests, Doctors, Appointments, and Staff
- **Keyboard Shortcuts** — Use `Alt+R`, `Alt+A`, `Alt+B`, `Alt+D`, `Alt+S` for quick navigation
- **Toast Notifications** — Visual feedback for keyboard shortcuts

### Smart Search & Filtering

Admin panel sections include built-in, instant search bars for quickly locating records:

| Section | Search By | Filter By |
|---------|-----------|----------|
| 📋 **Student Registrations** | Student Name, Student ID | — |
| 🩸 **Blood Donations** | Donor Name, Student ID | Blood Group (A±, B±, AB±, O±) |

- **Instant Results** — Filters as you type, no page reload required
- **Result Counter** — Shows "X of Y shown" while filtering
- **Clear Button** — One-click reset for all active filters
- **Blood Group Dropdown** — Quick filter by any of the 8 blood groups

### Access

Navigate to: `http://localhost:8000/manage/`

*(Staff/admin account required)*

---

## 🎭 Custom Error Pages

### 404 & 500 Error Pages

AUdoc features custom, creatively-styled error pages designed as **"AUdoc Incident Reports"**:

| Error | Features | Status |
|-------|----------|--------|
| **404 Not Found** | Animated incident descriptions, randomized messages, redacted text (click to reveal) | ✅ Live |
| **500 Server Error** | Same creative styling as 404 for consistent branding | ✅ Live |

### Error Page Features

- 📋 **Official Incident Report Style** — Styled like a bureaucratic form letter
- 🎬 **Animated Content** — Incident descriptions rotate every 5 seconds with smooth fade transitions
- 🔓 **Interactive Elements** — Redacted text reveals on hover with quirky messages
- 🎨 **Visual Details** — Includes tape, paperclip, and official stamp for immersion
- ⌚ **Dynamic Data** — Shows current date/time and randomized file paths
- 🏠 **Quick Actions** — "Return to Base" and "Browse Archives" buttons for navigation

### How It Works

```
User visits non-existent URL
    ↓
Django triggers 404/500 error handler
    ↓
Custom page_404/page_500 views render 404.html template
    ↓
User sees creative incident report (and smiles)
```

---

## 🚀 Production Deployment (Render)

AUdoc is deployed on **Render** with the following setup:

### Current Setup

| Component | Service | Status |
|-----------|---------|--------|
| **Backend** | Render Web Service | ✅ Live |
| **Database** | Render PostgreSQL | ✅ Live |
| **Email** | Resend | ✅ Live |
| **Domain** | voiddoc.me | ✅ Live |
| **AI Chatbot** | Groq API | ✅ Live |

### Environment Variables on Render

1. Set `DATABASE_URL` to your Render PostgreSQL connection string
2. Set `RESEND_API_KEY` from https://resend.com
3. Set `DEFAULT_FROM_EMAIL` to your verified domain
4. Set `GROQ_API_KEY` from https://console.groq.com

### Deploy to Render

```bash
# 1. Connect GitHub repo to Render
# 2. Add environment variables in Render dashboard
# 3. Render auto-deploys on git push to main
```

Visit: https://voiddoc.me

---

## ⏰ Scheduled Tasks (Today's Appointments)

The system supports automated daily appointment confirmations:

### How It Works

1. **8:00 AM** — System sends confirmation emails to patients with appointments today
2. **2-Hour Window** — Patients accept or decline via email link
3. **FCFS Queue** — Confirmed patients get queue positions (First Come, First Serve)
4. **Midnight** — Old records are cleaned up automatically

### Setup (Windows Task Scheduler)

```bash
# Send confirmations at 8 AM
python manage.py send_appointment_confirmations

# Cleanup at midnight
python manage.py cleanup_todays_appointments
```

### Setup (Linux/macOS Cron)

```bash
# Add to crontab -e
0 8 * * * cd /path/to/AUdoc_back && python manage.py send_appointment_confirmations
0 0 * * * cd /path/to/AUdoc_back && python manage.py cleanup_todays_appointments
```

---

## 📋 Roadmap

- [x] ~~Flutter app ↔ Django REST API integration~~ ✅ DRF installed
- [x] ~~Modern admin panel with charts~~ ✅ Glass-morphism UI
- [x] ~~Quick Actions section~~ ✅ Enhanced with priority alerts & keyboard shortcuts
- [x] ~~FCFS queue system~~ ✅ Today's Appointments
- [x] ~~AI Chatbot~~ ✅ Groq API integration
- [x] ~~PostgreSQL support for production~~ ✅ Render deployment
- [x] ~~Email with Resend~~ ✅ Custom domain support
- [x] ~~Custom error pages~~ ✅ Creative 404/500 incident report pages
- [ ] Push notifications for appointment confirmations
- [ ] Prescription & medical history records
- [ ] Docker + CI/CD pipeline
- [ ] Dark mode for student portal (admin has it! 🌑)

---

## ⚠️ Important Notes *(Read This Or Your Setup Will Break)*

- **Development:** Uses **SQLite** for quick setup (not recommended for production unless you want catastrophic failure)
- **Production:** Uses **PostgreSQL** on Render (auto-configured via `DATABASE_URL` — you're welcome)
- **Email:** Powered by **Resend** (free tier with custom domain support)
  - Use `onboarding@resend.dev` for testing (it works, trust us)
  - Add your domain in Resend dashboard for production (yes, you have to do this)
- **AI Chatbot:** Uses **Groq API** (free tier, `llama-3.1-8b-instant` model — it's not GPT-4, but it's free)
- **Custom Error Pages:** 404/500 errors display creative incident report-style pages (actually makes errors fun)
- **DEBUG = True** is development-only. Set it to `False` in production, or wake up to a security audit.
- The `myenv/` folder is gitignored. Always create your own virtual environment. (voidnova is tired of debugging envs)
- The Flutter app is a **UI prototype** — backend integration with DRF is in progress (voidnova is working on it, give him a break)
- The modern admin panel is at `/manage/`, not `/admin/`. (We know it's confusing)
- Doctor profile photos are stored in `media/doctors/`. (Yes, they're real photos, not Lorem Ipsum)
- **Never commit `.env`** — it contains secrets and is gitignored. If you commit secrets, voidnova will find you. 👀

---

## 🤝 Contributing *(Help voidnova Stay Awake)*

Contributions are welcome! Found a bug? Have a cool idea? Here's the drill:

```
1. Fork the repo (steal it, but legally)
2. Create your branch:   git checkout -b feat/amazing-feature
3. Commit your changes:  git commit -m "Add some amazing feature"
4. Push to your branch:  git push origin feat/amazing-feature
5. Open a Pull Request   (voidnova will review it eventually)
```

> **Pro Tips:**
> - Write a meaningful PR description. "fixed stuff" will be gently mocked. 😄
> - Don't commit your `.env` file. We've all been there. We've learned. Move on. 🙈
> - If you fix a bug, buy voidnova a coffee (UPI accepted)

---

## 📄 License

MIT License — do whatever you want with it. Just don't blame voidnova if something breaks. 😄

This project was built with love (and coffee) for students at **Assam University Silchar (AUS)**.

---

<div align="center">

Made with ☕ caffeine, 💻 late nights, 😅 existential crisis, and the genuine hope that AUS students stay healthy.

*"May your OTPs arrive fast, your appointments never be cancelled,*  
*your doctors be understanding, and your blood type always be in stock."*

⭐ **Star this repo if AUdoc saved you from a WebMD spiral!** ⭐

💪 **Shoutout to voidnova** — May your compile times be fast and your bugs be obvious.

**Made with ❤️ at Assam University Silchar**

*(If you found this project useful, tell voidnova. He probably needs validation.)*

</div>
