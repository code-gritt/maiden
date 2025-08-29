from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserView,
    GoogleLoginView,
    google_callback,
    PdfUploadView,
    PdfListView,
    PdfDetailView,
    ChatView,
)

app_name = "core"

urlpatterns = [
    # Authentication
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", UserView.as_view(), name="profile"),

    # Google OAuth
    path("google/login/", GoogleLoginView.as_view(), name="google_login"),
    path("google/callback/", google_callback, name="google_callback"),

    # PDF management
    path("pdf/upload/", PdfUploadView.as_view(), name="pdf_upload"),
    path("pdf/list/", PdfListView.as_view(), name="pdf_list"),
    path("pdf/<uuid:pdf_id>/", PdfDetailView.as_view(), name="pdf_detail"),

    # PDF chat
    path("pdf/<uuid:pdf_id>/chat/", ChatView.as_view(), name="pdf_chat"),
]
