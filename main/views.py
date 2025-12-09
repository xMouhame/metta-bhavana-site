from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from .forms import AppointmentForm


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def services(request):
    return render(request, "services.html")


def appointments(request):
    success = False

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()  # save to database

            # --------- BUILD EMAIL TO CLINIC ----------
            subject_clinic = "New Appointment Request – Metta Bhavana"

            client_name = appointment.name
            client_email = appointment.email
            client_phone = appointment.phone or "Not provided"
            service = appointment.get_service_type_display()
            date = appointment.preferred_date
            # human-readable time slot
            time_slot = appointment.get_preferred_time_display()
            message_text = appointment.message or "No additional message."

            body_clinic = (
                f"A new appointment request has been submitted.\n\n"
                f"Name: {client_name}\n"
                f"Email: {client_email}\n"
                f"Phone: {client_phone}\n"
                f"Service type: {service}\n"
                f"Preferred date: {date}\n"
                f"Preferred time: {time_slot}\n\n"
                f"Client message:\n{message_text}\n"
            )

            # Send email to clinic inbox
            send_mail(
                subject_clinic,
                body_clinic,
                settings.DEFAULT_FROM_EMAIL,
                ["mettabhavana.wellness@gmail.com"],
                fail_silently=False,
            )

            # --------- BUILD CONFIRMATION EMAIL TO CLIENT ----------
            subject_client = "Your Appointment Request – Metta Bhavana"
            body_client = (
                f"Hello {client_name},\n\n"
                f"Thank you for reaching out to Metta Bhavana Psychological & Spiritual Wellness.\n"
                f"We have received your appointment request with the following details:\n\n"
                f"Service: {service}\n"
                f"Preferred date: {date}\n"
                f"Preferred time: {time_slot}\n\n"
                f"If any changes are needed, we will contact you at this email address.\n\n"
                f"Warmly,\n"
                f"Metta Bhavana Psychological & Spiritual Wellness\n"
                f"330 E Lakeside St, Madison, WI 53715\n"
                f"Phone: (414) 801-9208\n"
            )

            send_mail(
                subject_client,
                body_client,
                settings.DEFAULT_FROM_EMAIL,
                [client_email],
                fail_silently=False,
            )

            # Show success message on page and reset form
            success = True
            form = AppointmentForm()
    else:
        form = AppointmentForm()

    return render(request, "appointments.html", {"form": form, "success": success})


def contact(request):
    return render(request, "contact.html")
