import secrets
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import EmailVerification, Score, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

def register_email_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Email is required.')
            return render(request, 'accounts/register_email.html')
        
        # Warn if email already exists in verification table
        if EmailVerification.objects.filter(email=email).exists():
            messages.warning(
                request, 
                "This email is already in use. Using it will cause the old account to be frozen."
            )

        # Generate 6-digit code with leading zeros (if les than 100000 fill the left fields with 0's)
        code = f"{secrets.randbelow(1000000):06d}"
        expires_at = timezone.now() + timezone.timedelta(minutes=5)
        
        # Store/update verification record
        EmailVerification.objects.update_or_create(
            email=email,
            defaults={'code': code, 'expires_at': expires_at}
        )
        
        # Send verification email
        try:
            send_mail(
                'Registration Verification Code',
                f'Your verification code is: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            messages.error(request, 'Failed to send verification email. Please try again.')
            return render(request, 'accounts/register_email.html')
        
        request.session['verification_email'] = email
        return redirect('verify_code')
    
    return render(request, 'accounts/register_email.html')


def verify_code_view(request):
    email = request.session.get('verification_email')
    if not email:
        messages.error(request, 'Session expired. Please start again.')
        return redirect('register_email')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            verification = EmailVerification.objects.get(email=email)
            if verification.code == code and verification.is_valid():
                request.session['verified_email'] = email
                verification.delete()
                del request.session['verification_email']
                return redirect('create_account')
            else:
                messages.error(request, 'Invalid or expired code.')
        except EmailVerification.DoesNotExist:
            messages.error(request, 'Code not found. Please request a new one.')
            return redirect('register_email')
    
    return render(request, 'accounts/verify_code.html')


def create_account_view(request):
    verified_email = request.session.get('verified_email')
    if not verified_email:
        return redirect('register_email')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            
            if User.objects.filter(email=verified_email).exists():
                messages.error(request, 'This email is already registered.')
                return render(request, 'accounts/create_account.html', {
                    'form': form,
                    'email': verified_email
                })

            with transaction.atomic():
                user = form.save(commit=False)
                user.email = verified_email
                user.save()  
                
                # Create stuff (default)
                Score.objects.create(user=user, total=0)
                UserProfile.objects.create(user=user, role='normal_user')
                
                auth_login(request, user)
                
                # rm session
                if 'verified_email' in request.session:
                    del request.session['verified_email']
                
                messages.success(request, "Account created successfully!")
                return redirect('/')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/create_account.html', {
        'form': form,
        'email': verified_email
    })