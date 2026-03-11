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

**The official campus health management system for Ahsanullah University**

[![Django](https://img.shields.io/badge/Django-6.0.3-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Dart](https://img.shields.io/badge/Dart-3.x-0175C2?style=for-the-badge&logo=dart&logoColor=white)](https://dart.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)

[✨ Features](#-features) · [🛠️ Tech Stack](#️-tech-stack) · [📁 Structure](#️-project-structure) · [⚡ Quick Start](#-getting-started) · [🗺️ API Routes](#️-url-routes)

</div>

---

## 🩺 What Is AUdoc?

Tired of wandering the hallways looking for the campus doctor while feeling like death warmed over?
**AUdoc has got you covered** — literally.

AUdoc is a full-stack **campus healthcare management system** built for **Ahsanullah University of Science & Technology**. From booking doctor appointments to donating blood (heroically), AUdoc is the one-stop-shop for all your campus health needs. No WebMD rabbit holes. No self-diagnosis spirals at 2am. Just real doctors, real appointments, and real OTPs delivered to your inbox.

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
| 🩸 **Blood Bank** | Donate blood, request blood, or target a specific donor. Heroes only. | ✅ Live |
| 💸 **Donations** | Support the health center financially. Even BDT 10 counts! | ✅ Live |
| 📊 **Appointment History** | Track all past, upcoming, and completed visits | ✅ Live |
| 📱 **Mobile App** | Cross-platform app (Android, iOS, Web, Windows, macOS, Linux) | 🚧 In Progress |

### The 8 Medical Specialties 🩺

`General` · `Dental` · `Eye Care` · `Mental Health` · `Orthopedics` · `Dermatology` · `Gynecology` · `Physiotherapy`

*(Yes, Mental Health is on the list. We take that seriously around here.)*

### For Admins ⚙️

| Feature | Description |
|---------|-------------|
| ✅ **Registration Workflow** | Review → Approve/Reject → auto-create user account + send welcome email |
| 👨‍⚕️ **Doctor Management** | Manage doctors, specialties, availability, and time slots |
| 🩸 **Blood Bank Admin** | Handle donor registrations and requests with 4 urgency levels |
| 📊 **Login Audit Log** | Every student login logged with timestamp & IP. Big Brother mode: ON. |
| 🏥 **Custom Admin Panel** | Django admin with fieldsets, filters, inline editing, and search |

---

## 🔐 How the Auth Flow Works

```
  Student                     System                     Admin
    │                            │                          │
    │──── Enter Student ID ─────>│                          │
    │<─── OTP sent to email ─────│                          │
    │──── Enter OTP ────────────>│                          │
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
│   │   ├── models.py                # 8 database models
│   │   ├── views.py                 # 7 view functions
│   │   ├── forms.py                 # 5 Django forms
│   │   ├── admin.py                 # Customized admin with auto-provisioning
│   │   ├── backends.py              # Custom OTP authentication backend
│   │   ├── signals.py               # Login audit signal handler
│   │   └── 📂 templates/app/        # HTML templates
│   │
│   ├── .env.example                 # 👈 Copy this to .env and add your secrets
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
│  Mobile/Desktop  │  Flutter  ·  Dart SDK ^3.11.1                │
│  Database        │  SQLite3  (swap to PostgreSQL for prod)       │
│  Authentication  │  Custom OTP-based  (no passwords for students)│
│  Email           │  Gmail SMTP  ·  TLS  ·  Port 587             │
│  UI Theme        │  Material Design 3                           │
│  Admin           │  Django Admin  (heavily customized)          │
└──────────────────┴──────────────────────────────────────────────┘
```

---

## 🏛️ Database Models

| Model | Purpose |
|-------|---------|
| `StudentProfile` | Approved student records linked to auth users |
| `StaffProfile` | Campus staff & doctor directory |
| `Doctor` | Doctors with specialties & availability slots |
| `Appointment` | Bookings (PENDING → CONFIRMED → COMPLETED) |
| `StudentRegistration` | Applications awaiting admin approval |
| `Donation` | Monetary donation pledges (BDT) |
| `BloodDonation` | Blood donor registry with health screening |
| `BloodRequest` | Blood requests with urgency (LOW / MEDIUM / HIGH / URGENT) |
| `LoginLog` | Security audit trail — every login, timestamped |

---

## 🌐 URL Routes

> Django serves server-side rendered HTML. Two endpoints are AJAX (return JSON).

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| `GET/POST` | `/` | ❌ | Home — top doctors, donor spotlights |
| `GET/POST` | `/register/` | ❌ | Student registration + email OTP verification |
| `POST` | `/send-otp/` | ❌ | **[AJAX]** Send OTP for registration |
| `POST` | `/student-login/` | ❌ | Validate OTP and log student in |
| `POST` | `/send-login-otp/` | ❌ | **[AJAX]** Send OTP for login |
| `GET/POST` | `/appointment/` | ✅ Login | Book & view appointments |
| `GET/POST` | `/donation/` | ❌ | Submit a monetary donation |
| `GET/POST` | `/blood-bank/` | ❌ | Blood donation or request (tabbed UI) |
| `GET` | `/blood-donors/` | ❌ | Filterable blood donor directory |
| `GET/POST` | `/blood-donors/<id>/request/` | ❌ | Request blood from a specific donor |
| `ANY` | `/admin/` | 🔑 Staff | Full Django admin panel |

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
git clone https://github.com/sayan-does/AUdoc.git
cd AUdoc/AUdoc_back

# 2. Create and activate a virtual environment
python -m venv myenv
myenv\Scripts\activate      # Windows
source myenv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install django

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
Admin panel 👉 `http://127.0.0.1:8000/admin/`

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

```env
DJANGO_SECRET_KEY=your-super-long-random-secret-key-here
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

> ⚠️ **Never commit `.env` to git.** It's gitignored for a reason. We are not animals.
>
> 💡 **Gmail App Password:** Go to Google Account → Security → App Passwords.
> Use your *real* Gmail password here and everyone will know what you did.

---

## 📋 Roadmap

- [ ] Flutter app ↔ Django REST API integration
- [ ] Push notifications for appointment confirmations
- [ ] Prescription & medical history records
- [ ] PostgreSQL support for production
- [ ] Docker + CI/CD pipeline
- [ ] Dark mode (because devs live in the dark 🌑)

---

## ⚠️ Important Notes

- **SQLite** is used for development. Swap to **PostgreSQL** or **MySQL** for production.
- `DEBUG = True` is development-only. Set it to `False` in production, or regret it deeply.
- The `myenv/` folder is gitignored. Always create your own virtual environment.
- The Flutter app is a **UI prototype** — backend integration is coming soon™.

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

This project was built with love for students at **Ahsanullah University of Science & Technology (AUST)**.

---

<div align="center">

Made with ☕ caffeine, 💻 late nights, and the genuine hope that AUST students stay healthy.

*"May your OTPs arrive fast, your appointments never be cancelled,*
*and your blood type always be in stock."*

⭐ **Star this repo if it saved you from a WebMD spiral!** ⭐

</div>
