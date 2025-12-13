import logging

from django.conf import settings
from django.shortcuts import render
import resend

from .forms import AppointmentForm

logger = logging.getLogger(**name**)

def home(request):
return render(request, "home.html")

def about(request):
return render(request, "about.html")

def services(request):
return render(request, "services.html")

def contact(request):
return render(request, "contact.html")

def _send_resend_email(*, from_email: str, to_emails: list[str], subject: str, text: str) -> None:
"""
Send one email via Resend to one or multiple recipients.
Raises exception on failure.
"""
resend.api_key = settings.RESEND_API_KEY

```
resend.Emails.send(
    {
        "from": from_email,
        "to": to_emails,  # list of emails
        "subject": subject,
        "text": text,
    }
)
```

def appointments(request):
"""
Appointment form:
- Saves the appointment in DB
- Sends notification to clinic + cousin personal email + confirmation to client via Resend
- If email fails, site still shows success (but logs the error)
"""
if request.method == "POST":
form = AppointmentForm(request.POST)

```
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

        # Always show something in Render logs
        print("=== New appointment submitted (Resend) ===")
        print(body_clinic)

        # Send emails (but don't break the page if they fail)
        try:
            if not getattr(settings, "RESEND_API_KEY", ""):
                raise RuntimeError("RESEND_API_KEY is not set in environment variables.")

            from_email = settings.DEFAULT_FROM_EMAIL

            # ✅ Clinic recipients (clinic email + cousin personal email)
            clinic_recipients = getattr(settings, "CLINIC_NOTIFY_EMAILS", None)
            if not clinic_recipients:
                # fallback if you didn’t add CLINIC_NOTIFY_EMAILS yet
                clinic_recipients = [getattr(settings, "CLINIC_NOTIFY_EMAIL", "")]

            # Remove any empty strings
            clinic_recipients = [e for e in clinic_recipients if e]

            # Email to clinic + cousin
            _send_resend_email(
                from_email=from_email,
                to_emails=clinic_recipients,
                subject=subject_clinic,
                text=body_clinic,
            )

            # Confirmation to client
            if email:
                _send_resend_email(
                    from_email=from_email,
                    to_emails=[email],
                    subject=subject_client,
                    text=body_client,
                )

        except Exception as e:
            # Optional fallback sender if you set FALLBACK_FROM_EMAIL
            try:
                if getattr(settings, "FALLBACK_FROM_EMAIL", ""):
                    logger.warning("Primary sender failed. Trying fallback sender. Error: %s", e)

                    from_email = settings.FALLBACK_FROM_EMAIL

                    _send_resend_email(
                        from_email=from_email,
                        to_emails=clinic_recipients,
                        subject=subject_clinic,
                        text=body_clinic,
                    )

                    if email:
                        _send_resend_email(
                            from_email=from_email,
                            to_emails=[email],
                            subject=subject_client,
                            text=body_client,
                        )
                else:
                    logger.error("Error sending appointment emails via Resend: %s", e)
            except Exception as e2:
                logger.error("Fallback sender also failed: %s", e2)

        return render(
            request,
            "appointments.html",
            {"form": AppointmentForm(), "success": True},
        )

    return render(request, "appointments.html", {"form": form})

return render(request, "appointments.html", {"form": AppointmentForm()})
```
