from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserView,
    GoogleLoginView,
    google_callback,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserView.as_view(), name='profile'),
    path('google/login/', GoogleLoginView.as_view(), name='google_login'),
    path('google/callback/', google_callback,
         name='google_callback'),
]
