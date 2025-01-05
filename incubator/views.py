from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.utils.timezone import now, timedelta
from .forms import CustomSignupForm,CustomLoginForm
from .utils import send_otp
import json
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login,logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django_select2.views import AutoResponseView
User=get_user_model()
from django.db.models import Q
from .models import Profile,Skill,Idea,Post,Comment,Reply,Tag
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
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
			return render(request, 'auth/register.html', {'form': form})
	
	else:
		form = CustomSignupForm()
		return render(request, 'auth/register.html', {'form': form})


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

	return render(request,'auth/verify_otp.html')

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
                    return render(request, 'auth/login.html', {'form': form})
            else:
                username = username_or_email

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)

                # Handle "remember me"
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)

                # Redirect based on `next` parameter or user role
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                elif user.role == 'mentor':  # Example: Redirect mentors
                    return redirect('mentor-dashboard')
                elif user.role == 'entrepreneur':  # Example: Redirect entrepreneurs
                    return redirect('dashboard')
                elif user.role == 'collaborator':  # Example: Redirect collaborators
                    return redirect('/')
                else:  # Default redirect for undefined roles
                    messages.warning(request, "Role not defined. Redirecting to home.")
                    return redirect('home')

            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomLoginForm()

    return render(request, 'auth/login.html', {'form': form})

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
	
	return render(request,'auth/forgot_password.html')

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
	
	return render(request,'auth/reset_password.html')

phone_number_validator = RegexValidator(
	regex=r'^[6-9]\d{9}$',  
	message="Enter a valid 10-digit phone number."
)

@login_required
def profile_setup(request):
	profile, created = Profile.objects.get_or_create(username=request.user)
	if request.method == 'POST':
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

		try:
			if phone_number:  
				phone_number_validator(phone_number)
		except ValidationError as e:
			return render(request, 'profile_setup.html', {
				'profile': profile,
				'error': e.message, 
			})

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

		# Update skills
		profile.skills.clear()  # Clear previous skills
		for skill_id in selected_skills:
			try:
				skill = Skill.objects.get(id=skill_id)
				profile.skills.add(skill)
			except Skill.DoesNotExist:
				continue

		profile.save()
		return redirect('dashboard')
	
	return render(request, 'profile_setup.html', {'profile': profile})

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
@login_required
def dashboard(request):
	ideas = Idea.objects.order_by('-created_at')[:5]
	context = {
		'ideas': ideas,
	}
	return render(request,'dashboard.html',context)
@login_required
def submit_idea(request):
	if request.method=='POST':
		try:
			data=json.loads(request.body)
			Idea.objects.create(
				title=data.get('title'),
				description=data.get('description'),
				category=data.get('category'),
				creator=request.user,
				visibility=data['visibility'],
				target_audience=data.get('targetAudience'),
				market_opportunity=data.get('marketOpportunity'),

			)
			return JsonResponse({"status": "success", "message": "Idea submitted successfully!"}, status=201)
		except Exception as e:
			print(e)
			return JsonResponse({"status": "error", "message": str(e)}, status=400)
	return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

def edit_idea(request, idea_id):
	if request.method == 'POST':
		data = json.loads(request.body)
		idea = get_object_or_404(Idea, id=idea_id)
		if request.user == idea.creator:
			idea.title = data.get('title')
			idea.description = data.get('description')
			idea.category = data.get('category')
			idea.visibility = data.get('visibility')
			idea.target_audience = data.get('targetAudience')
			idea.market_opportunity = data.get('marketOpportunity')
			idea.save()
			return JsonResponse({'success': True, 'message': 'Idea updated successfully!'})
		return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
	return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
def idea_list(request):
	idea=Idea.objects.all()
	return JsonResponse({'ideas':idea})

@login_required
def delete_idea(request, idea_id):
    if request.method == 'POST':
        idea = get_object_or_404(Idea, id=idea_id)
        if request.user == idea.creator:
            idea.delete()
            return JsonResponse({'success': True}) 
        else:
            return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

def get_idea(request, idea_id):
	idea = get_object_or_404(Idea, id=idea_id)
	return JsonResponse({
		'id': idea.id,
		'title': idea.title,
		'description': idea.description,
		'category': idea.category,
		'visibility': idea.visibility,
		'target_audience': idea.target_audience,
		'market_opportunity': idea.market_opportunity
	})

@login_required
def mentordashboard(request):
	return render(request,'mentors_dashboard.html')
@login_required

def discussion_forum(request):
	tags = Tag.objects.all()
	posts_list = Post.objects.all()

	return render(request, 'forum/forum.html', {'tags': tags, 'posts': posts_list})

@login_required
def submit_question(request):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
			title = data.get('title')
			description = data.get('description')
			tags = data.get('tags')
			created_by=request.user

			if not title or not description or not tags:
				return JsonResponse({"status": "error", "message": "All fields are required."}, status=400)

			post = Post.objects.create(title=title, description=description,created_by=created_by)
			post.tags.add(*tags)  
			return JsonResponse({"status": "success", "message": "Question submitted successfully."}, status=200)
		except Exception as e:
			print(e)
			return JsonResponse({"status": "error", "message": str(e)}, status=400)
	return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)

@login_required
def add_comment(request):
	if request.method == 'POST':
		data=json.loads(request.body)
		post_id=data.get('post_id')
		content=data.get('content')
		print(post_id)
		try:
			post = Post.objects.get(id=post_id)
			comment = Comment.objects.create(question=post, content=content, user=request.user)
			return JsonResponse({
				'success': True,
				'message': 'Comment added successfully!',
				'comment_id': comment.id,
				'comment_content': comment.content,
				'comment_user': comment.user.username,
				'comment_created': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
			})
		except Exception as e:
			return JsonResponse({'success': False, 'message': str(e)})
	return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def Reply_comment(request):
	if request.method == 'POST':
		data=json.loads(request.body)
		comment_id = data.get('comment_id')
		content = data.get('content')
		print(comment_id)
		try:
			comment = get_object_or_404(Comment, id=comment_id)
			reply = Reply.objects.create(comment=comment, content=content, user=request.user)
			return JsonResponse({
				'success': True,
				'message': 'Reply added successfully!',
				'reply_id': reply.id,
				'reply_content': reply.content,
				'reply_user': reply.user.username,
				'reply_created': reply.created_at.strftime('%Y-%m-%d %H:%M:%S')
			})
		except Exception as e:
			return JsonResponse({'success': False, 'message': str(e)})
	return JsonResponse({'success': False, 'message': 'Invalid request method'})


def view_post(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	comments = Comment.objects.filter(question=post)
	related_posts = Post.objects.exclude(id=post_id).filter(tags__in=post.tags.all())[:5]
	return render(request, 'forum/view_post.html', {
		'post': post,
		'related_posts': related_posts,
		'comments': comments, 
	})

def vote_comment(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		comment_id = data.get('comment_id')
		vote_type = data.get('vote_type') 
		user = request.user

		try:
			comment = Comment.objects.get(id=comment_id)
			user_vote = request.session.get(f"vote_{comment_id}", None)

			if vote_type == 'upvote':
				if user_vote == 'upvote':
					comment.upvotes -= 1
					del request.session[f"vote_{comment_id}"]
				else:
					if user_vote == 'downvote':
						comment.downvotes -= 1
					comment.upvotes += 1
					request.session[f"vote_{comment_id}"] = 'upvote'

			elif vote_type == 'downvote':
				if user_vote == 'downvote':
					comment.downvotes -= 1
					del request.session[f"vote_{comment_id}"]
				else:
					
					if user_vote == 'upvote':
						comment.upvotes -= 1
					comment.downvotes += 1
					request.session[f"vote_{comment_id}"] = 'downvote'

			comment.save()

			return JsonResponse({
				'success': True,
				'upvotes': comment.upvotes,
				'downvotes': comment.downvotes
			})

		except Comment.DoesNotExist:
			return JsonResponse({'success': False, 'message': 'Comment does not exist.'})
		except Exception as e:
			return JsonResponse({'success': False, 'message': str(e)})

	return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def edit_comment(request, comment_id):
	if request.method == 'POST':
		data=json.loads(request.body)
		comment = get_object_or_404(Comment, id=comment_id)
		if request.user == comment.user: 
			comment.content = data.get('content')
			comment.save()
			return JsonResponse({'success': True, 'content': comment.content})
		return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

def delete_comment(request, comment_id):
	if request.method == 'POST':
		comment = get_object_or_404(Comment, id=comment_id)
		if request.user == comment.user:  
			comment.delete()
			return JsonResponse({'success': True})
		return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
