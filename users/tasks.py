from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_reset_email_task(email, reset_link):
    subject = "Password Reset Request"
    message = f"Click the link to reset your password: {reset_link}\n\nThis link is valid for 15 minutes and can be used only once."
    send_mail(subject, message, 'noreply@example.com', [email])
