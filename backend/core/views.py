from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import Session, User
import uuid
from datetime import datetime, timedelta


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Register attempt:", request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("User created:", serializer.data['email'])
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        print("Register errors:", serializer.errors)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Login attempt:", request.data)
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            session_token = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(days=7)
            session = Session.objects.create(
                user=user,
                token=session_token,
                expires_at=expires_at
            )
            print("Session created for user:",
                  user.id, "Token:", session_token)
            response = Response({
                "message": "Login successful",
                "session_token": session_token,
                "expires_at": expires_at.isoformat()
            }, status=status.HTTP_200_OK)
            response.set_cookie(
                'session_token',
                session_token,
                httponly=True,
                secure=True,  # Always secure
                samesite='Lax',
                expires=expires_at
            )
            return response
        print("Login errors:", serializer.errors)
        return Response({"message": serializer.errors}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session_token = request.COOKIES.get('session_token')
        print("Logout attempt for token:", session_token)
        if session_token:
            try:
                Session.objects.filter(token=session_token).delete()
                print("Session deleted:", session_token)
                response = Response(
                    {"message": "Logout successful"}, status=status.HTTP_200_OK)
                response.delete_cookie('session_token')
                return response
            except Exception as e:
                print("Logout error:", str(e))
                return Response({"message": "Error during logout"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "No session found"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class UserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        print("User fetch attempt with cookies:", request.COOKIES)
        session_token = request.COOKIES.get('session_token')
        if not session_token:
            print("No session token provided")
            return Response({"message": "No session token"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            session = Session.objects.get(
                token=session_token, expires_at__gt=datetime.now())
            user = session.user
            print("User found:", user.username)
            return Response({
                "username": user.username,
                "email": user.email,
                "credits": user.credits
            }, status=status.HTTP_200_OK)
        except Session.DoesNotExist:
            print("Invalid or expired session token:", session_token)
            return Response({"message": "Invalid or expired session"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print("User fetch error:", str(e))
            return Response({"message": "Server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
