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

**The official campus health management system for Assam University Silchar**

[![Django](https://img.shields.io/badge/Django-6.0.3-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-ff1709?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Dart](https://img.shields.io/badge/Dart-3.x-0175C2?style=for-the-badge&logo=dart&logoColor=white)](https://dart.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Security](https://img.shields.io/badge/Security-Hardened-success?style=for-the-badge&logo=shield&logoColor=white)](#-security)

[✨ Features](#-features) · [🛠️ Tech Stack](#️-tech-stack) · [🔒 Security](#-security) · [📁 Structure](#️-project-structure) · [⚡ Quick Start](#-getting-started) · [🗺️ API Routes](#️-url-routes) · [🎛️ Admin Panel](#️-modern-admin-panel)

</div>

---

## 🩺 What Is AUdoc?

Tired of wandering the hallways looking for the campus doctor while feeling like death warmed over?
**AUdoc has got you covered** — literally.

AUdoc is a full-stack **campus healthcare management system** built for **Assam University Silchar**. From booking doctor appointments to donating blood (heroically), AUdoc is the one-stop-shop for all your campus health needs. No WebMD rabbit holes. No self-diagnosis spirals at 2am. Just real doctors, real appointments, and real OTPs delivered to your inbox.

> *"A student needed to book a doctor appointment. The existing system was... a phone call. In 2025.*
> *No further questions."* — So we built this. You're welcome.

The system has two layers working together:
- 🐍 **Django Web Backend** — Fully functional healthcare portal (the real deal)
- 📱 **Flutter Mobile App** — Polished cross-platform UI prototype (the superstar in training)

---

## ✨ Features

### For Students 🎓

| Feature | What it does | Status |
|---------|-------------|--------|
| 🔐 **Passwordless Login** | Student ID + OTP to email. No forgotten passwords. Ever. | ✅ Live |
| 📋 **Self Registration** | Sign up, verify email via OTP, get approved by admin | ✅ Live |
| 📅 **Doctor Appointments** | Book 30-min slots across 8 specialties | ✅ Live |
| 📧 **Smart Confirmations** | Morning email confirmations with 2-hour response window | ✅ Live |
| 🎫 **FCFS Queue System** | First Come, First Serve queue assignment on confirmation | ✅ Live |
| 🩸 **Blood Bank** | Donate blood, request blood, or target a specific donor. Heroes only. | ✅ Live |
| 💬 **AI Chatbot** | Get instant answers about campus health services | ✅ Live |
| 💸 **Donations** | Support the health center financially. Even ₹10 counts! | ✅ Live |
| 📊 **Appointment History** | Track all past, upcoming, and completed visits | ✅ Live |
| ⭐ **Help Desk Feedback** | Rate your experience and provide feedback | ✅ Live |
| 📱 **Mobile App** | Cross-platform app (Android, iOS, Web, Windows, macOS, Linux) | 🚧 In Progress |

### The 8 Medical Specialties 🩺

`General` · `Dental` · `Eye Care` · `Mental Health` · `Orthopedics` · `Dermatology` · `Gynecology` · `Physiotherapy`

*(Yes, Mental Health is on the list. We take that seriously around here.)*

### For Admins ⚙️

| Feature | Description |
|---------|-------------|
| 🎨 **Modern Admin Panel** | Glass-morphism UI with dark/light mode toggle |
| 📊 **Interactive Dashboard** | Real-time stats, charts, and trend indicators |
| 📈 **Live Charts** | Appointment trends & blood group distribution (Chart.js) |
| ⚡ **Quick Actions** | Priority-based action buttons with live stats & keyboard shortcuts |
| 🎫 **FCFS Queue View** | Today's appointments with queue positions |
| ✅ **Registration Workflow** | Review → Approve/Reject → auto-create user account + send welcome email |
| 👨‍⚕️ **Doctor Management** | Manage doctors, specialties, availability, and time slots |
| 👥 **Staff Management** | Add and manage health center staff |
| 🩸 **Blood Bank Admin** | Handle donor registrations and requests with 4 urgency levels |
| 📊 **Login Audit Log** | Every student login logged with timestamp & IP |
| 🔍 **Advanced Search** | Fast search across all data tables with filtering |
| 📤 **Export Data** | Download data as CSV/Excel files |
| 📱 **Mobile Responsive** | Works perfectly on mobile, tablet, and desktop |

---

## 🔐 How the Auth Flow Works

```
  Student                     System                     Admin
    │                            │                          │
    │──── Enter Student ID ─────>│                          │
    │<─── OTP sent to email ─────│                          │
    │──── Enter OTP ────────────>│ (rate limited + secure)  │
    │<─── Logged in! ────────────│                          │
    │                            │                          │
    │   (First time? Register!)  │                          │
    │──── Fill reg form ────────>│                          │
    │     + email OTP verify     │                          │
    │                            │──── Pending queue ──────>│
    │                            │<─── Approve/Reject ───────│
    │<─── Welcome email! ────────│  (auto-provisions account)│
```

No passwords. No "Forgot password?" links. Just vibes and OTPs. ✌️

> 🔒 **Security Note:** OTPs are generated using cryptographically secure random numbers, validated with constant-time comparison (timing-attack resistant), and all endpoints are rate-limited.

---

## 🔒 Security

AUdoc takes security seriously. The application has been hardened against common web vulnerabilities:

### Security Features

| Feature | Protection Against | Status |
|---------|-------------------|--------|
| 🛡️ **Rate Limiting** | Brute force attacks on login/OTP endpoints | ✅ Active |
| 🔐 **Secure OTP** | Cryptographically secure random generation | ✅ Active |
| ⏱️ **Timing Attack Protection** | Constant-time OTP comparison | ✅ Active |
| 🚫 **SQL Injection** | Parameterized queries via Django ORM | ✅ Protected |
| 🔄 **CSRF Protection** | All state-changing operations require tokens | ✅ Active |
| 🍪 **Secure Cookies** | HttpOnly, SameSite, Secure flags | ✅ Active |
| 🔒 **Security Headers** | X-Frame-Options, CSP, HSTS, XSS filter | ✅ Active |
| 🔑 **Argon2 Hashing** | Memory-hard password hashing algorithm | ✅ Active |
| 📝 **Security Logging** | Failed login attempts, rate limit violations | ✅ Active |

### Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| OTP Send | 5 requests | 5 minutes |
| Login | 10 requests | 5 minutes |
| API | 100 requests | 1 minute |

### Security Configuration

For production deployment, ensure these environment variables are set:

```env
# Security (REQUIRED for production)
DJANGO_SECRET_KEY=<generate-strong-random-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com
DJANGO_SECURE_SSL_REDIRECT=True
```

> 📄 For complete security documentation, see [`AUdoc_back/SECURITY.md`](AUdoc_back/SECURITY.md)

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

## 🛠️ Tech Stack

```
┌──────────────────┬──────────────────────────────────────────────┐
│  Backend         │  Django 6.0.3  ·  Python 3.12                │
│  API Framework   │  Django REST Framework 3.16.1                │
│  Mobile/Desktop  │  Flutter  ·  Dart SDK ^3.11.1                │
│  Database        │  PostgreSQL (Render)  ·  SQLite (dev)        │
│  Authentication  │  Custom OTP-based  (no passwords for students)│
│  Email           │  Resend  ·  TLS  ·  Free tier + custom domain│
│  Charts          │  Chart.js  (interactive dashboards)          │
│  UI Theme        │  Material Design 3  ·  Glass-morphism        │
│  Admin           │  Custom Modern Panel  (dark/light mode)      │
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

### Prerequisites

Make sure you have these installed — no excuses:

- 🐍 **Python 3.12+** — [python.org](https://python.org)
- 🐦 **Flutter 3.x** — [flutter.dev](https://flutter.dev/docs/get-started/install)
- 📧 **Gmail with App Password** — [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
- **Git** — you clearly already have it if you're reading this 😄

---

### 🐍 Backend Setup (Django)

```bash
# 1. Clone the repo
git clone https://github.com/voidnova-code/AUdoc.git
cd AUdoc/AUdoc_back

# 2. Create and activate a virtual environment
python -m venv myenv
myenv\Scripts\activate      # Windows
source myenv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your secrets
cp .env.example .env
# Open .env and fill in your Django secret key + Gmail credentials

# 5. Apply database migrations
python manage.py migrate

# 6. Create a superuser (for the admin panel)
python manage.py createsuperuser

# 7. Start the server!
python manage.py runserver
```

Visit 👉 `http://127.0.0.1:8000` — if you see a page, it worked. Celebrate responsibly. 🎉

Admin panel 👉 `http://127.0.0.1:8000/manage/` (Modern UI)

Django admin 👉 `http://127.0.0.1:8000/admin/` (Default Django)

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
| 🔍 **Advanced Search** | Fast search with DataTables integration |
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

## ⚠️ Important Notes

- **Development:** Uses **SQLite** for quick setup
- **Production:** Uses **PostgreSQL** on Render (auto-configured via `DATABASE_URL`)
- **Email:** Powered by **Resend** (free tier with custom domain support)
  - Use `onboarding@resend.dev` for testing
  - Add your domain in Resend dashboard for production
- **AI Chatbot:** Uses **Groq API** (free tier, `llama-3.1-8b-instant` model)
- **Custom Error Pages:** 404/500 errors display creative incident report-style pages (works in both DEBUG=True and DEBUG=False)
- `DEBUG = True` is development-only. Set it to `False` in production, or regret it deeply.
- The `myenv/` folder is gitignored. Always create your own virtual environment.
- The Flutter app is a **UI prototype** — backend integration with DRF is in progress.
- The modern admin panel is at `/manage/`, not `/admin/`.
- Doctor profile photos are stored in `media/doctors/`.
- **Never commit `.env`** — it contains secrets and is gitignored.

---

## 🤝 Contributing

Contributions are welcome! Found a bug? Have a cool idea? Here's the drill:

```
1. Fork the repo
2. Create your branch:   git checkout -b feat/amazing-feature
3. Commit your changes:  git commit -m "Add some amazing feature"
4. Push to your branch:  git push origin feat/amazing-feature
5. Open a Pull Request
```

> Pro tip: Write a meaningful PR description. "fixed stuff" will be gently declined. 😄
> Also, please don't commit your `.env` file. We've all been there. 🙈

---

## 📄 License

MIT License — do whatever you want with it, just don't blame us if something breaks. 😄

This project was built with love for students at **Assam University Silchar (AUS)**.

---

<div align="center">

Made with ☕ caffeine, 💻 late nights, and the genuine hope that AUS students stay healthy.

*"May your OTPs arrive fast, your appointments never be cancelled,*
*and your blood type always be in stock."*

⭐ **Star this repo if it saved you from a WebMD spiral!** ⭐

**Made with ❤️ at Assam University Silchar**

</div>
