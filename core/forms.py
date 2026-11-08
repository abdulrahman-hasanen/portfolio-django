from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot: real visitors never see or fill this field.
    website = forms.CharField(required=False)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your name.")
        return name

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError("Message must be at least 10 characters.")
        return message

    def is_spam(self):
        return bool(self.cleaned_data.get("website"))
