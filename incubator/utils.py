import random
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

def send_otp(user):
    otp=user.generate_otp()
    subject = "Your OTP for account verification"
    message = f"Your OTP is {otp}. Please enter it on the verification page."
    from_email = settings.EMAIL_HOST_USER  
    recipient_list = [user.email]  
    send_mail(subject, message, from_email, recipient_list)



