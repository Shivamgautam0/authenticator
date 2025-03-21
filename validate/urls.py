# validate/urls.py
from django.urls import path
from .views import signup, verifyotp, login_view, homepage, delete_account, logout_view, change_password
from django.shortcuts import redirect

def home(request):
    return redirect("signup")

urlpatterns = [
    path("", home),
    path("signup/", signup, name="signup"),
    path("verifyotp/", verifyotp, name="verifyotp"),
    path("login/", login_view, name="login"),
    path("home/", homepage, name="homepage"),
    path("delete-account/", delete_account, name="delete-account"),
    path("logout/", logout_view, name="logout"),
    path("change-password/", change_password, name="change-password"),
]