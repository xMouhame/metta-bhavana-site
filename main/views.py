# main/views.py

import logging

from django.conf import settings
from django.shortcuts import render
from django.core.mail import send_mail

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
    - On POST: save appointment, try to send emails
    - If email fails, log error but still show success to user
    """
    if request.method == "POST":
        form = AppointmentForm(request.POST)

        if form.is_valid():
            appointment = form.save()

            # ----- Build email content -----
            # Adjust field names here if your model uses different ones
            name = getattr(appointment, "name", "")
            email = getattr(appointment, "email", "")
            phone = getattr(appointment, "phone", "")
            preferred_date = getattr(appointment, "preferred_date", "")
            preferred_time = getattr(appointment, "preferred_time", "")
            message = getattr(appointment, "message", "")

            # Email TO CLINIC
            subject_clinic = f"New appointment request from {name}"
            message_clinic = (
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
            message_client = (
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

            # ----- Try to send both emails -----
            try:
                # Email to clinic (goes to your Gmail / DEFAULT_FROM_EMAIL)
                send_mail(
                    subject_clinic,
                    message_clinic,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )

                # Confirmation email to the client
                if email:
                    send_mail(
                        subject_client,
                        message_client,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )

            except Exception as e:
                # Don't crash the site if email fails – just log it to Render logs
                logger.error("Error sending appointment emails: %s", e)

            # Show success message and an empty form again
            return render(
                request,
                "appointments.html",
                {
                    "form": AppointmentForm(),  # new empty form
                    "success": True,            # you can use this in the template
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
