# MediDate – Medical Appointment Management System

MediDate is a web-based application for scheduling and managing medical appointments.  
It was developed as part of **Novaris Data** projects to showcase backend and database skills in real-world scenarios.

---

## ✨ Features

### Patient side
- Browse specialties and doctors.
- Book appointments with day/time picker (weekends disabled).
- View next appointment and count of upcoming visits.
- Manage profile (name, email, phone) and cancel own bookings.
- Friendly UI with status badges (Scheduled, Attended, Canceled).

### Staff side
- Dedicated **Consultorio** dashboard (permission-gated).
- KPIs: appointments today / next 7 days / canceled today.
- Filterable list: by specialty, doctor, patient, date range, and status.
- Cancel appointments with reason logging.
- Responsive Bootstrap 5 UI + custom styles.

---

## 🧱 Tech Stack

- **Python** 3.11+  
- **Django** 5.x  
- **PostgreSQL** (production) / SQLite (default dev)  
- **Bootstrap 5** + Inter font  
- **Flatpickr** for calendars  

---

## 🚀 Getting Started

### 1) Clone & create virtualenv
```bash
git clone https://github.com/<your-username>/medidate.git
cd medidate
python -m venv .venv
# Windows
.venv\Scripts\activate
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
DATABASE_URL=postgres://USER:PASS@HOST:5432/DBNAME
```

### 4) Migrate & run
```bash
python manage.py migrate
python manage.py runserver
```

Open: http://127.0.0.1:8000/

---

## 👥 Users & Permissions

- **Admin**: create with `python manage.py createsuperuser`  
- **Staff access**: assign the `agenda.access_consultorio` permission in the admin panel  
- **Patients**: profiles created automatically upon registration  

---

## 🖼️ Screens

<p>
  <img src="docs/screens/01_home_logged_out.png" width="800" alt="Home (logged out)" />
</p>
<p>
  <img src="docs/screens/05_patient_dashboard.png" width="800" alt="Patient dashboard" />
</p>
<p>
  <img src="docs/screens/07_staff_dashboard.png" width="800" alt="Staff KPIs" />
</p>

👉 [View all screenshots here](docs/screens/)

---

## 📊 Roadmap
- Email notifications & reminders  
- iCal/ICS calendar attachments  
- Doctor availability management  
- Multi-clinic / multi-location support  
- Internationalization (ES/EN)  

---

## 👥 Developed by

**Novaris Data – Consulting · Development · IT Solutions**  
🌐 [www.novarisdata.com](https://www.novarisdata.com)  
🔗 [Follow us on LinkedIn](https://www.linkedin.com/company/novarisdata/)

---

## 📄 License
MIT — Free to use for learning and portfolio purposes. For commercial use, review and adapt accordingly.

---

# 🇪🇸 MediDate – Sistema de Gestión de Citas Médicas

MediDate es una aplicación web para agendar y gestionar citas médicas.  
Fue desarrollado como parte de los proyectos de **Novaris Data** para demostrar habilidades en backend y bases de datos en escenarios reales.

## Funcionalidades principales
- Reservar citas según especialidad y médico.  
- Gestión de pacientes, médicos, especialidades y citas.  
- Panel de administración con métricas y filtros avanzados.  
- Base de datos en PostgreSQL con migraciones y seguridad.  
- Interfaz responsive con Bootstrap 5.

## Stack Tecnológico
- **Backend:** Django (Python)  
- **Base de datos:** PostgreSQL  
- **Frontend:** HTML, CSS, Bootstrap  
- **Control de versiones:** Git + GitHub  

---

Desarrollado por **Novaris Data – Consulting · Development · IT Solutions**  
🌐 [www.novarisdata.com](https://www.novarisdata.com)
🔗 [Síguenos en LinkedIn](https://www.linkedin.com/company/novarisdata/)
