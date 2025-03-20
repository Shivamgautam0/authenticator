from django.urls import path
from .views import change_password, signup, verifyotp, login,homepage,delete_account,logout
from django.shortcuts import redirect

def home(request):
    return redirect("signup")

urlpatterns = [
    path("", signup, name="signup"),
    path("verifyotp/", verifyotp, name="verifyotp"),
    path("login/", login, name="login"),
    path("home/", homepage, name="homepage"),
    path("delete-account/", delete_account, name="delete-account"),
    path("logout/", logout, name="logout"),
    path("change-password/", change_password, name="change-password"),  
]
