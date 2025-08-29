from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import RegisterSerializer, LoginSerializer
from .models import Session, User
import uuid
from datetime import datetime, timedelta
from django.conf import settings


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Create session
            session_token = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(days=7)
            Session.objects.create(
                user=user, token=session_token, expires_at=expires_at)

            # Set cookie with environment-aware settings
            response = Response({
                "message": "Login successful",
                "session_token": session_token,
                "expires_at": expires_at.isoformat()
            }, status=status.HTTP_200_OK)

            response.set_cookie(
                'session_token',
                session_token,
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                samesite=settings.SESSION_COOKIE_SAMESITE,
                expires=expires_at
            )
            return response

        return Response({"message": serializer.errors}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session_token = request.COOKIES.get('session_token')
        if session_token:
            Session.objects.filter(token=session_token).delete()
            response = Response(
                {"message": "Logout successful"}, status=status.HTTP_200_OK)
            response.delete_cookie('session_token')
            return response
        return Response({"message": "No session found"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class UserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session_token = request.COOKIES.get('session_token')
        if not session_token:
            return Response({"message": "No session token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            session = Session.objects.get(
                token=session_token, expires_at__gt=datetime.now())
            user = session.user
            return Response({
                "username": user.username,
                "email": user.email,
                "credits": user.credits
            }, status=status.HTTP_200_OK)
        except Session.DoesNotExist:
            return Response({"message": "Invalid or expired session"}, status=status.HTTP_401_UNAUTHORIZED)
