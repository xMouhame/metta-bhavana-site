from django.db import models


class Appointment(models.Model):
    SERVICE_CHOICES = [
        ("individual", "Individual Counseling"),
        ("marital", "Marital Counseling"),
        ("family", "Family Counseling"),
    ]

    TIME_CHOICES = [
        ("morning", "Morning (9:00–11:59 AM)"),
        ("afternoon", "Afternoon (12:00–3:59 PM)"),
        ("evening", "Evening (4:00–7:00 PM)"),
        ("flexible", "I'm flexible / No specific time"),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    preferred_date = models.DateField()

    # CHANGED: from TimeField to CharField with choices
    preferred_time = models.CharField(
        max_length=20,
        choices=TIME_CHOICES,
    )

    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.service_type} ({self.preferred_date})"
