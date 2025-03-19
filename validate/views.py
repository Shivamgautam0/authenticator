from django.shortcuts import render
import random
from .models import users
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
otp = random.randint(10000,99999)
@csrf_exempt
def signup(request):
    tempmail = "shivamgautam.hanuai@gmail.com"
    if request.method == 'POST':
        useremail =  request.POST.get("useremail")
        password = request.POST.get("password")
        print(f"Received signup request for {useremail}")
        if users.objects.filter(useremail=useremail).exists():
            print("Email already exists!")
            return JsonResponse({"message" : "Email already exists"})
        print(f"Generated OTP: {otp}")
        send_mail(
            "Your OTP for signup",
            f"OTP is {otp}",
            [tempmail],
            [useremail],
            fail_silently= False,
        )
        return JsonResponse({"message" : "OTP sent!!"})
    return render(request,'index.html')
@csrf_exempt
def verifyotp(request):
    if request.method == 'POST':
        useremail = request.POST.get("useremail")
        password  = request.POST.get("password")
        userotp = int(request.POST.get("userotp"))
    if otp == userotp:
        users.objects.create(email=useremail,password=password)
        return JsonResponse({"message": "Signup successful!"})
        
    return JsonResponse({"message": "Invalid OTP!"}, status=400)

@csrf_exempt
def login(request):
    if request.method == "POST":
        useremail = request.POST.get("useremail")
        password = request.POST.get("password")
        
        try:
            user = users.objects.get(useremail=useremail)
            if password == users.password:
                return JsonResponse({"message": "Login successful!"})
            else:
                return JsonResponse({"message": "Invalid credentials!"}, status=400)
        except users.DoesNotExist:
            return JsonResponse({"message": "User not found!"}, status=400)
    
    return render(request, "login.html")