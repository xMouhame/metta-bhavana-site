from django import forms
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    # Honeypot field: hidden, bots fill it, humans don't
    honeypot = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
    )

    # Simple human check
    human_check = forms.IntegerField(
        label="To help us avoid spam, what is 7 + 3?",
    )

    class Meta:
        model = Appointment
        fields = [
            "name",
            "email",
            "phone",
            "service_type",
            "preferred_date",
            "preferred_time",
            "message",
        ]
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            # preferred_time will automatically be a <select> because of choices
            "message": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "preferred_time": "Preferred time of day",
        }

    def clean_honeypot(self):
        """
        If this field is filled, it's probably a bot.
        """
        value = self.cleaned_data.get("honeypot")
        if value:
            raise forms.ValidationError("Spam detected.")
        return value

    def clean_human_check(self):
        """
        Simple anti-bot math question.
        """
        value = self.cleaned_data.get("human_check")
        if value != 10:
            raise forms.ValidationError("Incorrect answer. Please try again.")
        return value
