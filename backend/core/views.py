# core/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer, SessionSerializer
from .models import Session
import uuid
from datetime import datetime, timedelta


class RegisterView(APIView):
    def post(self, request):
        print("Register attempt:", request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("User created:", serializer.data['email'])
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        print("Register errors:", serializer.errors)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
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
                secure=request.is_secure(),
                expires=expires_at
            )
            return response
        print("Login errors:", serializer.errors)
        return Response({"message": serializer.errors}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        session_token = request.COOKIES.get('session_token')
        print("Logout attempt for token:", session_token)
        if session_token:
            Session.objects.filter(token=session_token).delete()
            print("Session deleted:", session_token)
            response = Response(
                {"message": "Logout successful"}, status=status.HTTP_200_OK)
            response.delete_cookie('session_token')
            return response
        return Response({"message": "No session found"}, status=status.HTTP_400_BAD_REQUEST)
