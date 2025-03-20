# validate/views.py
from django.shortcuts import redirect, render
import random
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import ensure_csrf_cookie

def generate_otp(email):
    otp = random.randint(100000, 999999)
    # Store OTP in cache with 10-minute expiry
    cache.set(f"otp_{email}", otp, 600)
    return otp

def verify_user_otp(email, user_otp):
    stored_otp = cache.get(f"otp_{email}")
    if stored_otp and int(user_otp) == stored_otp:
        # Delete the OTP after successful verification
        cache.delete(f"otp_{email}")
        return True
    return False

@ensure_csrf_cookie
def signup(request):
    if request.method == 'POST':
        email = request.POST.get("useremail")
        password = request.POST.get("password")
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({"message": "Email already exists"})
        
        # Generate unique OTP for this email
        otp = generate_otp(email)
        
        try:
            send_mail(
                "Your OTP for signup",
                f"Your OTP is {otp}. It will expire in 10 minutes.",
                "shivamgautam.hanuai@gmail.com",
                [email],
                fail_silently=False,
            )
            return JsonResponse({"message": "OTP sent!!"})
        except Exception as e:
            print(f"Email error: {e}")
            return JsonResponse({"message": "Failed to send OTP"}, status=500)
    
    return render(request, 'index.html')

@require_POST
def verifyotp(request):
    email = request.POST.get("useremail")
    password = request.POST.get("password")
    user_otp = request.POST.get("otp")
    
    if verify_user_otp(email, user_otp):
        # Username will be the part of email before @
        username = email.split('@')[0]
        # Make sure username is unique
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
        # Create user with Django's built-in model
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password  # create_user automatically hashes the password
        )
        return JsonResponse({"message": "Signup successful!"})
    
    return JsonResponse({"message": "Invalid or expired OTP!"}, status=400)

@ensure_csrf_cookie
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("useremail")
        password = request.POST.get("password")
        
        try:
            user = User.objects.get(email=email)
            # Authenticate using Django's system
            user = authenticate(username=user.username, password=password)
            
            if user is not None:
                auth_login(request, user)
                return JsonResponse({"message": "Login successful!"})
            else:
                return JsonResponse({"message": "Invalid credentials!"}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"message": "User not found!"}, status=400)
    
    return render(request, "login.html")

@login_required
def homepage(request):
    return render(request, "homepage.html", {"useremail": request.user.email})

@login_required
@require_POST
def delete_account(request):
    try:
        user = request.user
        user.delete()
        auth_logout(request)
        return JsonResponse({"success": True, "message": "Account deleted successfully"})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)

def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Check if the old password is correct
        if not request.user.check_password(old_password):
            return JsonResponse({"success": False, "message": "Old password is incorrect"}, status=400)
        
        # Check if the new passwords match
        if new_password1 != new_password2:
            return JsonResponse({"success": False, "message": "New passwords do not match"}, status=400)
        
        # Change the password
        request.user.set_password(new_password1)
        request.user.save()
        
        # Update the session after password change
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        
        return JsonResponse({"success": True, "message": "Password changed successfully"})
    
    return render(request, 'change_password.html')