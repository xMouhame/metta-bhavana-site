# main/views.py

import logging

from django.conf import settings
from django.shortcuts import render
import resend  # use Resend API for emails

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


def appointments(request):
    """
    Show the appointment form and handle submissions.
    - On GET: show empty form
    - On POST: save appointment, send emails via Resend.
    - If email fails, log error but still show success to user.
    """
    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            appointment = form.save()

            # ----- Build email content -----
            name = getattr(appointment, "name", "")
            email = getattr(appointment, "email", "")
            phone = getattr(appointment, "phone", "")
            preferred_date = getattr(appointment, "preferred_date", "")
            preferred_time = getattr(appointment, "preferred_time", "")
            message = getattr(appointment, "message", "")

            # Email TO CLINIC
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

            # Email TO CLIENT
            subject_client = "Your appointment request with Metta Bhavana"
            body_client = (
                f"Dear {name},\n\n"
                "Thank you for contacting Metta Bhavana Psychological & "
                "Spiritual Wellness.\n\n"
                "We have received your appointment request with the "
                "following details:\n\n"
                f"Preferred date: {preferred_date}\n"
                f"Preferred time: {preferred_time}\n\n"
                "We will review your request and get back to you as soon as possible.\n\n"
                "Warmly,\n"
                "Metta Bhavana Psychological & Spiritual Wellness"
            )

            # Debug so we see in logs
            print("=== New appointment submitted (Resend) ===")
            print(body_clinic)

            # ----- Try to send both emails via Resend -----
            try:
                if getattr(settings, "RESEND_API_KEY", ""):
                    # Email to clinic
                    resend.Emails.send({
                        "from": settings.DEFAULT_FROM_EMAIL,
                        "to": ["mettabhavana.wellness@gmail.com"],
                        "subject": subject_clinic,
                        "text": body_clinic,
                    })

                    # Confirmation email to the client
                    if email:
                        resend.Emails.send({
                            "from": settings.DEFAULT_FROM_EMAIL,
                            "to": [email],
                            "subject": subject_client,
                            "text": body_client,
                        })
                else:
                    logger.error("RESEND_API_KEY is not set; skipping email send.")

            except Exception as e:
                logger.error("Error sending appointment emails via Resend: %s", e)

            # Show success message and an empty form again
            return render(
                request,
                "appointments.html",
                {
                    "form": AppointmentForm(),  # new empty form
                    "success": True,            # used in the template
                },
            )

        else:
            # Form not valid – re-show with errors
            return render(
                request,
                "appointments.html",
                {"form": form},
            )

    # GET request – show empty form
    form = AppointmentForm()
    return render(request, "appointments.html", {"form": form})
