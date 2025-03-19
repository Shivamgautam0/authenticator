from django.urls import path
from .views import signup, verifyotp, login,homepage,delete_account,logout
from django.shortcuts import redirect

def home_redirect(request):
    return redirect("signup")

urlpatterns = [
    path("", home_redirect),  # Redirect root to signup
    path("signup/", signup, name="signup"),
    path("verifyotp/", verifyotp, name="verifyotp"),
    path("login/", login, name="login"),
    path("home/", homepage, name="homepage"),
    path("delete-account/", delete_account, name="delete-account"),
    path("logout/", logout, name="logout"),
]
