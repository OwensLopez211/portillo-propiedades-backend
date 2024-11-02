from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.http import JsonResponse
from django.conf import settings
import requests


def send_email(subject, body, recipient_email):
    url = "https://api.mailerlite.com/api/v2/email/send"
    headers = {
        "Content-Type": "application/json",
        "X-MailerLite-ApiKey": settings.MAILERLITE_API_KEY
    }
    payload = {
        "subject": subject,
        "body": body,
        "recipients": [{"email": recipient_email}]
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return True
    else:
        print("Error:", response.json())
        return False
