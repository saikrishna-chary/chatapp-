from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


# --------------------------
# 🔹 Custom User Manager
# --------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)
        user.is_admin = True
        user.is_staff = True  # Required for Django Admin
        user.is_superuser = True  # Required for Django Admin
        user.save(using=self._db)
        return user


# --------------------------
# 🔹 Custom User Model
# --------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)      # Required for admin access
    is_superuser = models.BooleanField(default=False)  # Required for admin access
    is_admin = models.BooleanField(default=False)      # Optional custom flag

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


# --------------------------
# 🔹 Chat Room Model
# --------------------------
class ChatRoom(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)  # For group chat name
    is_group = models.BooleanField(default=False)
    members = models.ManyToManyField(CustomUser, related_name='chatrooms')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name if self.name else f"Private Chat Room {self.id}"


# --------------------------
# 🔹 Message Model
# --------------------------
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat_media/', blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')

    def __str__(self):
        return f"{self.sender.name}: {self.content[:20] if self.content else '[Media]'}"
