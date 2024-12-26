import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import EmailValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, name, password=None, email=None, **extra_fields):
        if not self.is_valid_phone_number(phone_number):
            raise ValueError("The phone number must be a valid 10-digit Indian phone number")

        if email and not self.is_valid_email(email):
            raise ValueError("The email is not valid")

        if password and not self.is_valid_password(password):
            raise ValueError("Password must be at least 8 characters long and alphanumeric.")

        if not phone_number:
            raise ValueError("The phone number must be set")
        
        user = self.model(phone_number=phone_number, name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, password=None, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone_number, name, password, email, **extra_fields)

    def is_valid_phone_number(self, phone_number):
        # Phone number validation is done for India (10 digits starting with 7-9)
        phone_regex = r"^[789]\d{9}$"  # Phone number should start with 7, 8, or 9 and followed by 9 digits according to indian standards
        return bool(re.match(phone_regex, phone_number))

    def is_valid_email(self, email):
        validator = EmailValidator()
        try:
            validator(email)
            return True
        except ValidationError:
            return False

    def is_valid_password(self, password):
        return len(password) >= 8 and any(c.isdigit() for c in password) and any(c.isalpha() for c in password)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13, unique=True)
    email = models.EmailField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.phone_number


class Contact(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class SpamReport(models.Model):
    reported_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Spam report for {self.phone_number} by {self.reported_by}"
