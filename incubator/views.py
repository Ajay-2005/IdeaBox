from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .forms import CustomSignupForm
from .utils import send_otp
from django.contrib.auth import get_user_model

User=get_user_model()
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
            return JsonResponse({
                'message': 'Your message has been sent successfully!',
                'message_type': 'success',  #
            })
        except Exception as e:
            print(e)
            messages.error(
                request, "Failed to send the message. Please try again.")

    return render(request, 'home.html')

def register(request):
    if request.method=='POST':
        form = CustomSignupForm(request.POST) 
        print(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  
            user.save()
            send_otp(user)
            request.session['email'] = user.email  
            messages.success(request, "Registration successful! Please check your email for the OTP.")
            return redirect("verify_otp")
        else:
            print(form.errors)
            print(f"Form is invalid: {form.errors}")
            messages.error(request, "Registration failed. Please correct the errors below.")
            return render(request, 'register.html', {'form': form})
    
    else:
        form = CustomSignupForm()
        return render(request, 'register.html', {'form': form})


def verify_otp(request):
    if request.method=='POST':
        entered_otp=request.POST.get('otp')
        email=request.session.get('email')
    
        try:
            user = User.objects.get(email=email)

            if user.verify_otp(entered_otp):  
                user.is_active = True  
                user.otp_hash = None  
                user.otp_created_at = None
                user.save()

                messages.success(request, "Your account has been activated successfully!")
                return redirect("/")
            else:
                messages.error(request, "Invalid or expired OTP. Please try again.")

        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request,'verify_otp.html')