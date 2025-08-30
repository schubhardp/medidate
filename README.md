# MediDate – Medical Appointment Scheduling (Django)

Simple, production‑ready-ish appointment scheduling app built with **Django 5**, designed for portfolio/demo use.  
It lets **patients** book and manage appointments and gives **clinic staff** a lightweight dashboard to filter, review, and cancel bookings.

> Screenshots live in `docs/screens/` for quick viewing below.

---

## ✨ Features

### Patient side
- Browse specialties and doctors.
- Book appointments with day/time picker (weekends disabled).
- See “Next appointment” and a count of upcoming visits.
- Manage profile (name, email, phone) and cancel own bookings.
- Friendly UI with status badges (Scheduled, Attended, Canceled).

### Staff side
- **Consultorio** dashboard (permission‑gated).
- KPIs: appointments today / next 7 days / canceled today.
- Filterable list: by specialty, doctor, patient, date range, and status.
- Cancel appointments with a reason (logged via message feedback).
- Clean Bootstrap/Inter design, responsive.

### Under the hood
- Django 5, classically structured app `agenda/`.
- Custom context processor for active nav links and counters.
- AJAX endpoints to populate doctors and available time slots.
- Flatpickr for date picker with Spanish locale.
- Bootstrap 5 UI + custom styles (`static/css/custom.css`).

> **Note:** Email notifications/integrations are not included (see Roadmap).

---

## 🖼️ Screens

<p>
  <img src="docs/screens/01_home_logged_out.png" width="800" alt="Home (logged out)" />
</p>
<p>
  <img src="docs/screens/02_register.png" width="800" alt="Register" />
</p>
<p>
  <img src="docs/screens/03_login.png" width="800" alt="Login" />
</p>
<p>
  <img src="docs/screens/05_patient_dashboard.png" width="800" alt="Patient dashboard" />
</p>
<p>
  <img src="docs/screens/06_profile_edit.png" width="800" alt="Edit profile" />
</p>
<p>
  <img src="docs/screens/04_book_appointment.png" width="800" alt="Book appointment" />
</p>
<p>
  <img src="docs/screens/07_staff_dashboard.png" width="800" alt="Staff KPIs" />
</p>
<p>
  <img src="docs/screens/08_staff_list_filters.png" width="800" alt="Staff list with filters" />
</p>

---

## 🧱 Tech Stack

- **Python** 3.11+
- **Django** 5.x
- **SQLite** (dev default) – switchable via `DATABASE_URL`
- **Bootstrap 5** + Inter font
- **Flatpickr** for calendars

---

## 📁 Project Structure (excerpt)

```
Proyecto_cita_medica/
├─ agenda/
│  ├─ admin.py
│  ├─ apps.py
│  ├─ context_processors.py
│  ├─ forms.py
│  ├─ models.py
│  ├─ signals.py
│  ├─ urls.py
│  └─ views.py
├─ templates/
│  ├─ agenda/ (patient + staff pages)
│  ├─ registration/ (login, register)
│  ├─ base.html
│  └─ inicio.html
├─ static/
│  └─ css/custom.css
├─ docs/
│  └─ screens/*.png
├─ Proyecto_cita_medica/
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ .env.example
├─ .gitignore
├─ manage.py
└─ requirements.txt
```

---

## 🚀 Getting Started

### 1) Clone & create virtualenv
```bash
git clone https://github.com/schubhardp/medidate.git
cd medidate
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Environment variables
Copy the example file and adjust:
```bash
cp .env.example .env
```
Required keys:
```
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
# Optional: DATABASE_URL=postgres://USER:PASS@HOST:5432/DBNAME
```

### 4) Migrate & run
```bash
python manage.py migrate
python manage.py runserver
```

Open: http://127.0.0.1:8000/

---

## 👥 Users & Permissions

### Create an admin/superuser
```bash
python manage.py createsuperuser
```
Log in at `/admin/`.

### Staff access (“Consultorio”)
To use the staff dashboard, a user must have the **`agenda.access_consultorio`** permission.  
Grant it via **Admin → Users → (select user) → User permissions** and add the permission.  
Then the **Consultorio** link appears in the navbar and staff views become accessible (`/consultorio/`).

> Patients don’t need any special permission; a `Paciente` profile is created automatically for logged-in users who visit patient pages.

---

## 🧪 Tests
Basic scaffolding is present; feel free to extend with pytest/Django test cases.  

---

## 🧭 Roadmap Ideas
- Email notifications & reminders (booking/cancellation).
- iCal/ICS calendar attachments.
- Doctor availability windows per weekday.
- Multi-clinic / multi-location support.
- Internationalization toggle (ES/EN) and accessibility pass.

---

## 🔐 Security & Production Notes
- Set `DEBUG=False` and a strong `SECRET_KEY` in production.
- Configure `ALLOWED_HOSTS` properly.
- Use Postgres or MySQL via `DATABASE_URL` for production environments.
- Run `python manage.py collectstatic` behind a real web server or CDN.
- Consider CSRF/Session hardening and HTTPS only cookies.

---

## 🧑‍💻 Author

**Philipp Schubhard**  
- GitHub: https://github.com/schubhardp  
- LinkedIn: https://www.linkedin.com/in/philipp-schubhard/

If you find this useful, a ⭐ on GitHub would be awesome.

---

## 📄 License

MIT — You’re free to use this for learning and personal projects. For commercial use, review and adapt accordingly.
