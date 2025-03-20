from django.shortcuts import redirect, render
import random
from .models import users
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt

# Generate new OTP for each request
def generate_otp():
    return random.randint(10000, 99999)

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        useremail = request.POST.get("useremail")
        password = request.POST.get("password")
        print(f"Received signup request for {useremail}")
        
        if users.objects.filter(useremail=useremail).exists():
            print("Email already exists!")
            return JsonResponse({"message": "Email already exists"})
            
        # Generate a new OTP for this request
        new_otp = generate_otp()
        print(f"Generated OTP: {new_otp}")
        
        # Store data in session
        request.session['signup_otp'] = new_otp
        request.session['signup_username'] = username
        request.session['signup_email'] = useremail
        request.session['signup_password'] = password
        
        sender_email = "shivamgautam.hanuai@gmail.com"
        try:
            send_mail(
                "Your OTP for signup",
                f"OTP is {new_otp}",
                sender_email,
                [useremail],
                fail_silently=False,
            )
            return JsonResponse({"message": "OTP sent!!"})
        except Exception as e:
            print(f"Email error: {e}")
            return JsonResponse({"message": "Failed to send OTP"}, status=500)
    
    return render(request, 'index.html')

@csrf_exempt
def verifyotp(request):
    if request.method == 'POST':
        user_otp = int(request.POST.get("otp"))
        
        # Get stored data from session
        stored_otp = request.session.get('signup_otp')
        stored_username = request.session.get('signup_username')
        stored_email = request.session.get('signup_email')
        stored_password = request.session.get('signup_password')
        
        if not all([stored_otp, stored_username, stored_email, stored_password]):
            return JsonResponse({"message": "Session expired! Please try again."}, status=400)
        
        if stored_otp == user_otp:
            # Create new user with stored credentials
            users.objects.create(
                username=stored_username,
                useremail=stored_email, 
                password=stored_password
            )
            
            # Clear sensitive session data
            for key in ['signup_otp', 'signup_username', 'signup_email', 'signup_password']:
                if key in request.session:
                    del request.session[key]
                    
            return JsonResponse({"message": "Signup successful!"})
        
        return JsonResponse({"message": "Invalid OTP!"}, status=400)
    
    return JsonResponse({"message": "Invalid request method"}, status=400)

@csrf_exempt
def login(request):
    if request.method == "POST":
        useremail = request.POST.get("useremail")
        password = request.POST.get("password")
        
        try:
            user = users.objects.get(useremail=useremail)
            if password == user.password:
                request.session['useremail'] = useremail
                request.session['username'] = user.username
                return JsonResponse({"message": "Login successful!"})
            else:
                return JsonResponse({"message": "Invalid credentials!"}, status=400)
        except users.DoesNotExist:
            return JsonResponse({"message": "User not found!"}, status=400)
    
    return render(request, "login.html")

def homepage(request):  
    if 'useremail' not in request.session:
        return redirect('login')
        
    useremail = request.session['useremail']
    username = request.session.get('username', '')
    return render(request, "homepage.html", {"useremail": useremail, "username": username})

@csrf_exempt
def delete_account(request):
    if request.method == "POST":
        if 'useremail' not in request.session:
            return JsonResponse({"success": False, "message": "Not logged in"}, status=401)
        
        useremail = request.session['useremail']
        
        try:
            user = users.objects.get(useremail=useremail)
            user.delete()
            del request.session['useremail']
            if 'username' in request.session:
                del request.session['username']
            
            return JsonResponse({"success": True, "message": "Account deleted successfully"})
        except users.DoesNotExist:
            return JsonResponse({"success": False, "message": "User not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)
    
    return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)

def logout(request):
    if 'useremail' in request.session:
        del request.session['useremail']
    if 'username' in request.session:
        del request.session['username']
    return redirect('login')