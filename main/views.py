import logging

from django.conf import settings
from django.shortcuts import render
import resend

from .forms import AppointmentForm

logger = logging.getLogger(__name__)


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def services(request):
    return render(request, "services.html")


def contact(request):
    return render(request, "contact.html")


def _send_resend_email(*, from_email: str, to_email: str, subject: str, text: str) -> None:
    """
    Send one email via Resend. Raises exception on failure.
    """
    resend.api_key = settings.RESEND_API_KEY

    resend.Emails.send(
        {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "text": text,
        }
    )


def appointments(request):
    """
    Appointment form:
    - Saves appointment in DB
    - Sends notification to clinic + cousin personal email
    - Sends confirmation to client
    - Never breaks the page if email fails
    """
    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            appointment = form.save()

            name = getattr(appointment, "name", "")
            email = getattr(appointment, "email", "")
            phone = getattr(appointment, "phone", "")
            preferred_date = getattr(appointment, "preferred_date", "")
            preferred_time = getattr(appointment, "preferred_time", "")
            message = getattr(appointment, "message", "")

            subject_clinic = f"New appointment request from {name}"
            body_clinic = (
                "A new appointment has been requested:\n\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Phone: {phone}\n"
                f"Preferred date: {preferred_date}\n"
                f"Preferred time: {preferred_time}\n\n"
                f"Message:\n{message}\n"
            )

            subject_client = "Your appointment request with Metta Bhavana"
            body_client = (
                f"Dear {name},\n\n"
                "Thank you for contacting Metta Bhavana Psychological & Spiritual Wellness.\n\n"
                "We have received your appointment request with the following details:\n\n"
                f"Preferred date: {preferred_date}\n"
                f"Preferred time: {preferred_time}\n\n"
                "We will review your request and get back to you as soon as possible.\n\n"
                "Warmly,\n"
                "Metta Bhavana Psychological & Spiritual Wellness"
            )

            # Always log submission (for Render logs)
            print("=== New appointment submitted (Resend) ===")
            print(body_clinic)

            # ✅ Cousin personal email (ADDED)
            COUSIN_PERSONAL_EMAIL = "Pfall89@gmail.com"

            try:
                if not settings.RESEND_API_KEY:
                    raise RuntimeError("RESEND_API_KEY is not set.")

                from_email = settings.DEFAULT_FROM_EMAIL

                # 1️⃣ Clinic inbox
                _send_resend_email(
                    from_email=from_email,
                    to_email=settings.CLINIC_NOTIFY_EMAIL,
                    subject=subject_clinic,
                    text=body_clinic,
                )

                # 2️⃣ Cousin personal email
                _send_resend_email(
                    from_email=from_email,
                    to_email=COUSIN_PERSONAL_EMAIL,
                    subject=subject_clinic,
                    text=body_clinic,
                )

                # 3️⃣ Client confirmation
                if email:
                    _send_resend_email(
                        from_email=from_email,
                        to_email=email,
                        subject=subject_client,
                        text=body_client,
                    )

            except Exception as e:
                logger.error("Error sending appointment emails via Resend: %s", e)

            return render(
                request,
                "appointments.html",
                {
                    "form": AppointmentForm(),
                    "success": True,
                },
            )

        return render(request, "appointments.html", {"form": form})

    return render(request, "appointments.html", {"form": AppointmentForm()})
