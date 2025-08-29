from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import RegisterSerializer, LoginSerializer
from .models import Session, User
from django.conf import settings
from django.contrib.auth import login
from social_django.utils import psa
import uuid
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def create_session_and_cookie(user, response):
    """Helper to create session and set cookie."""
    session_token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    Session.objects.create(
        user=user, token=session_token, expires_at=expires_at)
    response.set_cookie(
        "session_token",
        session_token,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        expires=expires_at
    )
    return response


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Register attempt: %s", request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("User created: %s", serializer.data["email"])
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        logger.error("Register errors: %s", serializer.errors)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Login attempt: %s", request.data)
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            response = Response(
                {"message": "Login successful"}, status=status.HTTP_200_OK)
            response = create_session_and_cookie(user, response)
            logger.info("Login successful, session set for user %s", user.id)
            return response
        logger.error("Login errors: %s", serializer.errors)
        return Response({"message": serializer.errors}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session_token = request.COOKIES.get("session_token")
        if session_token:
            Session.objects.filter(token=session_token).delete()
            response = Response(
                {"message": "Logout successful"}, status=status.HTTP_200_OK)
            response.delete_cookie("session_token")
            logger.info("Logout successful, session deleted: %s",
                        session_token)
            return response
        logger.warning("Logout attempt with no session token")
        return Response({"message": "No session found"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class UserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session_token = request.COOKIES.get("session_token")
        if not session_token:
            logger.warning("User fetch attempted without session token")
            return Response({"message": "No session token"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            session = Session.objects.get(
                token=session_token, expires_at__gt=datetime.now())
            user = session.user
            return Response({"username": user.username, "email": user.email, "credits": user.credits})
        except Session.DoesNotExist:
            logger.warning(
                "Invalid or expired session token: %s", session_token)
            return Response({"message": "Invalid or expired session"}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(csrf_exempt, name="dispatch")
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        redirect_uri = f"{request.scheme}://{request.get_host()}/api/auth/google/callback/"
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?response_type=code&client_id={settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY}"
            f"&redirect_uri={redirect_uri}&scope=email profile"
        )
        return Response({"auth_url": auth_url}, status=status.HTTP_200_OK)


@csrf_exempt
@psa("social:complete")
def google_callback(request, backend):
    """
    Function-based view for Google OAuth callback (needed because @psa breaks class-based views)
    """
    try:
        user = request.backend.auth_complete(request=request)
        if not user:
            logger.error("Google OAuth failed: No user returned")
            return Response({"message": "Authentication failed"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.username:
            user.username = user.email.split("@")[0]
            user.save()

        login(request, user, backend="social_core.backends.google.GoogleOAuth2")
        response = Response(
            {"message": "Google login successful"}, status=status.HTTP_200_OK)
        response = create_session_and_cookie(user, response)
        logger.info("Google login successful, session set for user %s", user.id)
        return response

    except Exception as e:
        logger.exception("Google OAuth error")
        return Response({"message": "Authentication error"}, status=status.HTTP_400_BAD_REQUEST)
