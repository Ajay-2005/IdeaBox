from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

def home(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        fullmessage = f"Message from {name}:\nReply to {email} \n{message}"
        
        try:
            send_mail(
                subject=subject,
                message=fullmessage,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['testcodeaj123@gmail.com'],
                fail_silently=False
            )
            messages.success(request, "Your message has been sent successfully")
            return redirect('home')  

        except Exception as e:
            print(e)
            messages.error(request, "Failed to send the message. Please try again.")

    return render(request, 'home.html')
