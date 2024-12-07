from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.utils.timezone import now, timedelta
from .forms import CustomSignupForm,CustomLoginForm
from .utils import send_otp
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login,logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django_select2.views import AutoResponseView
User=get_user_model()
from .models import Profile,Skill
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
                login(request, user)
                return redirect('profile_setup')
            else:
                messages.error(request, "Invalid or expired OTP. Please try again.")

        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request,'verify_otp.html')

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)

        if not form.is_valid():
            print("Form errors:", form.errors)

        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    messages.error(request, "Invalid email or password.")
                    return render(request, 'login.html', {'form': form})
            else:
                username = username_or_email

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)

                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)
                next_url = request.GET.get('next')

                return redirect(next_url or 'home') 
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})

def resend_otp(request):
    email = request.session.get("email")

    try:
        user = User.objects.get(email=email)
        send_otp(user)
        messages.success(request, "A new OTP has been sent to your email.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    return redirect("verify_otp")

def logout_view(request):
    logout(request)  
    messages.success(request, "You have been logged out successfully.") 
    return redirect('login')  


def forgot_password(request):
    if request.method=='POST':
        email=request.POST.get('email')
        try:
            user=User.objects.get(email=email)
            otp=user.generate_otp()
            otp_hash=user.otp_hash
            reset_link = request.build_absolute_uri(
                reverse('reset_password') + f'?email={email}&otp={otp_hash}'
            )
            subject="Reset your password"
            message=f"Click the link to reset your password:{reset_link}"
            from_email = settings.EMAIL_HOST_USER 
            send_mail(
                subject,
                message,
                from_email,
                [email],
                fail_silently=False         
            )
            messages.success(request,"Password reset link sent to your email")
        except User.DoesNotExist:
            messages.error(request,"No accound found with this email")
            return redirect('forgot_password')
    
    return render(request,'forgot_password.html')

def reset_password(request):
    email=request.GET['email']
    otp_hash=request.GET['otp']
    if request.method=='POST':
        new_password=request.POST['password']
        try:
            user=User.objects.get(email=email)
            if user.otp_hash == otp_hash and now() <= user.otp_created_at + timedelta(minutes=5):
                user.password=make_password(new_password)
                user.otp_hash=None
                user.save()
                messages.success(request,"Password reset suceessfully")
                return redirect('home')
            else:
                messages.error(request,"invalid reset link")
        except User.DoesNotExist:
            messages.error(request,"No accound found with this email")
    
    return render(request,'reset_password.html')


@login_required
def profile_setup(request):
    profile, created = Profile.objects.get_or_create(username=request.user)
    if request.method=='POST':
        profile_picture = request.FILES.get('profile_picture', profile.profile_picture)
        bio = request.POST.get('bio', '')
        education = request.POST.get('education', '')
        experience = request.POST.get('experience', '')
        phone_number = request.POST.get('phone_number', '')
        location = request.POST.get('location', '')
        linkedin = request.POST.get('linkedin', '')
        twitter = request.POST.get('twitter', '')
        github = request.POST.get('github', '')
        status = request.POST.get('status', 'Available')
        selected_skills = request.POST.getlist('skills') 

        profile.profile_picture = profile_picture
        profile.bio = bio
        profile.education = education
        profile.experience = experience
        profile.phone_number = phone_number
        profile.location = location
        profile.linkedin = linkedin
        profile.twitter = twitter
        profile.github = github
        profile.status = status
        
        for skill_id in selected_skills:
            try:
                skill=Skill.objects.get(id=skill_id)
                profile.skills.add(skill)
            except Skill.DoesNotExist:
                continue
            
        profile.save()

        return redirect('profile')
    return render(request, 'profile_setup.html',{'profile':profile})
@login_required
def profile(request):
    profile=Profile.objects.get(username=request.user)
    return render(request,'profile.html',{'profile':profile})


class CustomSkillAutoResponseForm(AutoResponseView):
    def get(self, request, *args, **kwargs):
        term = self.request.GET.get('term', '').strip()
        
        skills = Skill.objects.filter(name__icontains=term) if term else Skill.objects.none()
        results = [{'id': skill.id, 'text': skill.name} for skill in skills]
        return JsonResponse({'results': results})

def dashboard(request):
    return render(request,'dashboard.html')