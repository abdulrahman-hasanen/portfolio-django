# Abdulrahman Hasanen — Django Portfolio

A dynamic personal portfolio application built with **Python** and **Django 6.1**.

The application provides project management, image uploads, a contact system, and an administrative dashboard. It uses Django Templates, SQLite, and locally compiled Tailwind CSS.

## Features

- Responsive portfolio powered by Django Templates.
- Dynamic project management through Django Admin.
- Project image uploads and automatic image optimization.
- Contact form with messages stored in the database.
- Optional email notifications for contact submissions.
- Custom Django Admin interface.
- Locally compiled Tailwind CSS.
- Static-file handling with WhiteNoise.
- Production deployment support using Gunicorn.

## Tech Stack

| Area | Technology |
|---|---|
| Backend | Python, Django 6.1 |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Templates | Django Templates |
| Styling | Tailwind CSS |
| Static Files | WhiteNoise |
| Image Processing | Pillow |
| Production Server | Gunicorn |

## Project Structure

```text
portfolio-django/
│
├── config/                 # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── core/                   # Main Django application
│   ├── migrations/
│   ├── management/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── admin.py
│
├── templates/              # Django HTML templates
│   ├── includes/
│   └── pages/
│
├── static/                 # Django CSS, JavaScript and images
│   ├── css/
│   ├── js/
│   └── files/
│
├── media/                  # Uploaded project images
│   └── projects/
│
├── tools/                  # Development scripts
│   └── build_css.sh
│
├── manage.py
├── requirements.txt
├── tailwind.config.js
├── .env.example
├── .gitignore
└── README.md
```

## Requirements

Make sure the following tools are installed:

- Python 3.14 (or a compatible Python version).
- pip.
- Git.

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/abdulrahman-hasanen/portfolio-django.git
cd portfolio-django
```

### 2. Create a Virtual Environment

**Windows:**

```cmd
python -m venv venv
```

**Linux / macOS:**

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

**Windows — Command Prompt:**

```cmd
venv\Scripts\activate.bat
```

**Windows — PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

The terminal should display `(venv)` when the environment is active.

### 4. Install Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

The main dependencies include Django, Pillow, WhiteNoise, and Gunicorn.

### 5. Configure Environment Variables

Create a local `.env` file from `.env.example`.

**Windows — Command Prompt:**

```cmd
if not exist .env copy .env.example .env
```

**Windows — PowerShell:**

```powershell
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
```

**Linux / macOS:**

```bash
test -f .env || cp .env.example .env
```

For local development, make sure `.env` contains:

```env
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

The development configuration uses a local-only fallback secret key when `DJANGO_DEBUG=1`.

Never use the development configuration in production.

Do not overwrite an existing `.env` file.

### 6. Apply Database Migrations

```bash
python manage.py migrate
```

### 7. Create an Admin Account

```bash
python manage.py createsuperuser
```

Follow the prompts to create your administrator account.

### 8. Run the Development Server

```bash
python manage.py runserver
```

Open the website:

<http://127.0.0.1:8000/>

Open Django Admin:

<http://127.0.0.1:8000/admin/>

To stop the development server, press `Ctrl + C`.

## Django Admin

The administrative dashboard provides tools for managing the portfolio.

### Projects

- Add and edit projects.
- Publish and manage project information.
- Upload project screenshots.
- Maintain project details through the admin interface.

### Contact Messages

- View submitted contact messages.
- Review sender information and message content.
- Manage stored messages.

## Contact Form

The contact form validates submitted data and stores messages in the database.

Contact submissions remain available through Django Admin.

Email notifications are optional and can be enabled by configuring the email environment variables.

## Tailwind CSS

Tailwind CSS is compiled locally into:

```text
static/css/tailwind.css
```

The compiled stylesheet is committed to the repository.

After changing Tailwind classes in Django templates or relevant JavaScript files, rebuild the CSS.

The build script is:

```text
tools/build_css.sh
```

### Build Commands

One-time build:

```bash
./tools/build_css.sh
```

Watch mode:

```bash
./tools/build_css.sh --watch
```

**Windows users:** The current build script supports Linux and macOS. Use WSL on Windows to execute it.

If you are not changing Tailwind classes, you can use the already compiled stylesheet.

### Design Configuration

Design tokens, brand colors, surface colors (`surface-0` through `surface-3`), and font families are configured in:

```text
tailwind.config.js
```

## Image Optimization

The project includes a custom Django management command for optimizing existing project images.

### Preview Changes

```bash
python manage.py optimize_images --dry-run
```

### Apply Optimization

```bash
python manage.py optimize_images
```

New project image uploads are automatically:

- Resized to a maximum dimension of 1600 pixels.
- Converted to WebP format.
- Stored in the media directory.

## Testing and Project Checks

Run the Django test suite:

```bash
python manage.py test
```

Check the Django configuration:

```bash
python manage.py check
```

Run the production deployment checks:

```bash
python manage.py check --deploy
```

Review any deployment warnings before publishing the application.

## Production Deployment

The application can be deployed to a hosting platform that supports Python and Django.

### Environment Variables

Configure the following environment variables in your hosting provider:

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Production secret key |
| `DJANGO_DEBUG` | Set to `0` in production |
| `DJANGO_ALLOWED_HOSTS` | Allowed production hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Trusted HTTPS origins |
| `DJANGO_BEHIND_PROXY` | Reverse proxy configuration |
| `DJANGO_DB_PATH` | Optional persistent SQLite database path |
| `DJANGO_MEDIA_ROOT` | Uploaded media storage directory |
| `DJANGO_SERVE_MEDIA` | Enable Django media serving |

### Installation and Build Commands

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Collect static files:

```bash
python manage.py collectstatic --noinput
```

Start the production application:

```bash
gunicorn config.wsgi:application
```

### Static Files

Django static files are served using **WhiteNoise**.

The `collectstatic` command collects application static files into `STATIC_ROOT`.

### Database

The current project uses SQLite by default.

For production, the database file must be stored on persistent storage. Do not rely on temporary or ephemeral filesystems for SQLite data.

For serverless hosting, the database configuration must be adapted to a supported persistent database service before deployment.

### Uploaded Media

Uploaded project images are stored separately from application static files.

Configure:

```env
DJANGO_MEDIA_ROOT=/path/to/persistent/media
```

Set:

```env
DJANGO_SERVE_MEDIA=1
```

when Django should serve uploaded media.

Alternatively, use a web server or object storage service to serve the `/media/` URL.

### Reverse Proxy and HTTPS

When running behind a trusted reverse proxy that terminates HTTPS, configure:

```env
DJANGO_BEHIND_PROXY=1
```

Configure `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` for your production domain.

HSTS settings should only be strengthened when all relevant subdomains are guaranteed to use HTTPS.

### Email Notifications

To enable SMTP email notifications, configure:

```env
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=1
CONTACT_NOTIFY_EMAIL=
DEFAULT_FROM_EMAIL=
```

Keep all email credentials private.

## Security Notes

- Never commit `.env` files.
- Never expose passwords, API keys, or secret keys.
- Never commit the local `db.sqlite3` unless there is a specific reviewed reason.
- Keep `venv/` and `.venv/` out of version control.
- Keep `__pycache__/` and generated `staticfiles/` out of version control.
- Keep `.env.example` free of real credentials.
- If a previously used `SECRET_KEY` was exposed publicly, treat it as compromised and generate a new one.

## Useful Commands

| Task | Command |
|---|---|
| Create virtual environment | `python -m venv venv` |
| Activate environment (Windows CMD) | `venv\Scripts\activate.bat` |
| Install dependencies | `python -m pip install -r requirements.txt` |
| Apply migrations | `python manage.py migrate` |
| Create admin account | `python manage.py createsuperuser` |
| Run development server | `python manage.py runserver` |
| Run tests | `python manage.py test` |
| Check configuration | `python manage.py check` |
| Collect static files | `python manage.py collectstatic --noinput` |

---

**Maintainer:** Abdulrahman Hasanen

**Repository:** <https://github.com/abdulrahman-hasanen/portfolio-django>