from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Uses UUID as primary key and enforces unique email.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    credits = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username or self.email


class Pdf(models.Model):
    """
    PDF uploaded by a user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="pdfs")
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_url = models.CharField(max_length=255, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name


class ChatMessage(models.Model):
    """
    A chat message related to a PDF.
    user_id is stored as UUID instead of a ForeignKey to keep schema flexible.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pdf = models.ForeignKey(Pdf, on_delete=models.CASCADE,
                            related_name="chat_messages")
    user_id = models.UUIDField()
    content = models.TextField()
    is_user_message = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message for PDF {self.pdf.id}"


class Subscription(models.Model):
    """
    Subscription details for a user.
    One-to-one relation ensures each user has at most one subscription.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="subscription")
    plan = models.CharField(max_length=100)
    credits = models.PositiveIntegerField()
    paypal_sub_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Subscription for {self.user.username}"


class Session(models.Model):
    """
    Session tokens for user authentication.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sessions")
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session for {self.user.username}"
