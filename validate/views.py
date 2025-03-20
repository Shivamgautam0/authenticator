from django.shortcuts import redirect, render
import random
from .models import users
from django.http import JsonResponse, HttpResponse  
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
otp = random.randint(10000, 99999)

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
            
        print(f"Generated OTP: {otp}")
        sender_email = "shivamgautam.hanuai@gmail.com"
        try:
            send_mail(
                "Your single-use code",
                f"Hi, {username} \n \n \n OTP is {otp}",
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
        username = request.POST.get("username")
        useremail = request.POST.get("useremail")
        password = request.POST.get("password")
        user_otp = int(request.POST.get("otp"))
        
        if otp == user_otp:
            users.objects.create(username=username,useremail=useremail, password=password)
            users.save()
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
                
                return JsonResponse({"message": "Login successful!",})
            else:
                return JsonResponse({"message": "Invalid credentials!"}, status=400)
        except users.DoesNotExist:
            return JsonResponse({"message": "User not found!"}, status=400)
        
    return render(request, "login.html")


@login_required(login_url='/login/')
def homepage(request):
    if 'useremail' in request.session: 
        return render(request, "homepage.html", {
            "username": request.session.get("username", "Guest"),
            "useremail": request.session["useremail"]
        })
    else:
        return redirect("/login/")

@csrf_exempt
@login_required(login_url='/login/')
def delete_account(request):
    if request.method == "POST":
        if 'useremail' not in request.session:
            return JsonResponse({"success": False, "message": "Not logged in"}, status=401)
        
        useremail = request.session['useremail']
        
        try:
            user = users.objects.get(useremail=useremail)
            user.delete()
            del request.session['useremail']
            
            return JsonResponse({"success": True, "message": "Account deleted successfully"})
        except users.DoesNotExist:
            return JsonResponse({"success": False, "message": "User not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)
    
    return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)
@csrf_exempt
def changepassword(request):
    if request.method == "POST":
        if 'useremail' not in request.session:
            return JsonResponse({"success": False, "message": "Not logged in"}, status=401)
        useremail = request.session['useremail']
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        try:
            user = users.objects.get(useremail=useremail)
            if user.password == old_password:
                user.password = new_password
                user.save()
                return JsonResponse({"success": True, "message": "Password changed successfully"})
            else:
                return JsonResponse({"success": False, "message": "Invalid old password"}, status=400)
        except users.DoesNotExist:
            return JsonResponse({"success": False, "message": "User not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)
    return JsonResponse({"success": False, "message": "GET method not allowed"}, status=405)

def logout(request):
    if 'useremail'in request.session:
        del request.session['useremail']
    return redirect('login')