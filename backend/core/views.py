from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, PdfSerializer, ChatMessageSerializer
from .models import Session, User, Pdf, ChatMessage
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import login
from social_django.utils import psa
import logging
import requests
import PyPDF2
from django.core.files.storage import default_storage

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


@method_decorator(csrf_exempt, name="dispatch")
class PdfUploadView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session_token = request.COOKIES.get("session_token")
        if not session_token:
            logger.warning("PDF upload attempted without session token")
            return Response({"message": "No session token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            session = Session.objects.get(
                token=session_token, expires_at__gt=datetime.now())
            user = session.user
        except Session.DoesNotExist:
            logger.warning(
                "Invalid or expired session token: %s", session_token)
            return Response({"message": "Invalid or expired session"}, status=status.HTTP_401_UNAUTHORIZED)

        # Check PDF limit (5 for free tier)
        pdf_count = Pdf.objects.filter(user=user).count()
        if pdf_count >= 5 and not user.subscription:
            logger.warning("User %s exceeded free tier PDF limit", user.id)
            return Response({"message": "Free tier limit reached (5 PDFs). Upgrade to Pro."}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get("file")
        if not file:
            logger.error("No file provided in PDF upload")
            return Response({"message": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith(".pdf"):
            logger.error("Invalid file type for upload: %s", file.name)
            return Response({"message": "Only PDF files are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file size (10 MB = 10 * 1024 * 1024 bytes)
        if file.size > 10 * 1024 * 1024:
            logger.error("File too large: %s bytes", file.size)
            return Response({"message": "File size exceeds 10 MB limit"}, status=status.HTTP_400_BAD_REQUEST)

        # Simulate file storage (e.g., save to staticfiles or cloud storage)
        # For simplicity, store file name and size; in production, use cloud storage
        file_url = f"/upload/{uuid.uuid4()}_{file.name}"
        pdf = Pdf(
            user=user,
            file_name=file.name,
            file_size=file.size,
            file_url=file_url,
            uploaded_at=datetime.now()
        )
        pdf.save()
        logger.info("PDF uploaded: %s for user %s", file.name, user.id)

        serializer = PdfSerializer(pdf)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class PdfListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session_token = request.COOKIES.get("session_token")
        if not session_token:
            logger.warning("PDF list fetch attempted without session token")
            return Response({"message": "No session token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            session = Session.objects.get(
                token=session_token, expires_at__gt=datetime.now())
            user = session.user
        except Session.DoesNotExist:
            logger.warning(
                "Invalid or expired session token: %s", session_token)
            return Response({"message": "Invalid or expired session"}, status=status.HTTP_401_UNAUTHORIZED)

        pdfs = Pdf.objects.filter(user=user).order_by('-uploaded_at')
        serializer = PdfSerializer(pdfs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class PdfDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pdf_id):
        user, error_response = get_authenticated_user(request)
        if error_response:
            return error_response

        try:
            pdf = Pdf.objects.get(id=pdf_id, user=user)
        except Pdf.DoesNotExist:
            return Response({"message": "PDF not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PdfSerializer(pdf)
        return Response(serializer.data)

# --------------------------
# Chat View
# --------------------------


@method_decorator(csrf_exempt, name="dispatch")
class ChatView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pdf_id):
        user, error_response = get_authenticated_user(request)
        if error_response:
            return error_response

        try:
            pdf = Pdf.objects.get(id=pdf_id, user=user)
        except Pdf.DoesNotExist:
            return Response({"message": "PDF not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.credits < 2:
            return Response({"message": "Insufficient credits. Upgrade to Pro."}, status=status.HTTP_403_FORBIDDEN)

        user_message = request.data.get("message")
        if not user_message:
            return Response({"message": "No message provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Extract PDF text
        try:
            file_path = default_storage.path(pdf.file_url.lstrip('/'))
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                pdf_text = "".join(page.extract_text()
                                   or "" for page in pdf_reader.pages)
        except Exception as e:
            logger.error("Failed to extract PDF text: %s", str(e))
            return Response({"message": "Failed to process PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Call Gemini API
        try:
            gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            payload = {"contents": [
                {"parts": [{"text": f"Context: {pdf_text}\n\nUser question: {user_message}"}]}]}
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{gemini_url}?key={settings.GOOGLE_GEMINI_API_KEY}", json=payload, headers=headers)
            response.raise_for_status()
            ai_response = response.json(
            )['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            logger.error("Gemini API error: %s", str(e))
            return Response({"message": "Failed to generate response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Deduct credits and save chat messages
        user.credits -= 2
        user.save()
        user_msg = ChatMessage(pdf=pdf, user_id=user.id, content=user_message,
                               is_user_message=True, created_at=datetime.now())
        ai_msg = ChatMessage(pdf=pdf, user_id=user.id, content=ai_response,
                             is_user_message=False, created_at=datetime.now())
        user_msg.save()
        ai_msg.save()

        return Response({
            "user_message": ChatMessageSerializer(user_msg).data,
            "ai_response": ChatMessageSerializer(ai_msg).data,
            "credits_remaining": user.credits
        })


def get_authenticated_user(request):
    """Fetch the user from the session token."""
    token = request.COOKIES.get("session_token")
    if not token:
        return None, Response({"message": "No session token"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        session = Session.objects.get(
            token=token, expires_at__gt=datetime.now())
        return session.user, None
    except Session.DoesNotExist:
        return None, Response({"message": "Invalid or expired session"}, status=status.HTTP_401_UNAUTHORIZED)
