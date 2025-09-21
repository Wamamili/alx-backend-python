import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


# -------------------
# Custom User Model
# -------------------
class User(AbstractUser):
    """
    Extends Django's AbstractUser to include additional fields.
    """
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False, db_index=True)  # Unique + indexed
    password_hash = models.CharField(max_length=128, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')

    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'password_hash']

    def __str__(self):
        return f"{self.email} ({self.role})"


# -------------------
# Property Model
# -------------------
class Property(models.Model):
    """
    Represents a rental property listed by a host.
    """
    property_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties")
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    location = models.CharField(max_length=255, null=False, blank=False)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["property_id"]),
            models.Index(fields=["host"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.location}"


# -------------------
# Booking Model
# -------------------
class Booking(models.Model):
    """
    Represents a booking made by a user for a property.
    """
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField(null=False, blank=False)
    check_out = models.DateField(null=False, blank=False)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        indexes = [
            models.Index(fields=["property"]),
            models.Index(fields=["booking_id"]),
        ]

    def __str__(self):
        return f"Booking {self.booking_id} for {self.property.title} ({self.status})"


# -------------------
# Payment Model
# -------------------
class Payment(models.Model):
    """
    Represents a payment for a booking.
    """
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    payment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["booking"]),
        ]

    def __str__(self):
        return f"Payment {self.payment_id} for {self.booking.booking_id}"


# -------------------
# Review Model
# -------------------
class Review(models.Model):
    """
    Represents a review for a property by a user.
    """
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=False,
        blank=False,
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("property", "user")  # One review per user per property

    def __str__(self):
        return f"Review {self.rating}/5 for {self.property.title} by {self.user.email}"


# -------------------
# Conversation Model
# -------------------
class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    participants_id = models.ForeignKey(
        "User",
        to_field="user_id",
        on_delete=models.CASCADE,
        related_name="conversations_created",  # unique name for reverse accessor
        null=True,
        blank=True,
        db_index=True,
    )

    # All participants (including creator if you want)
    participants = models.ManyToManyField(
        "User",
        related_name="conversations_joined",  # unique name for reverse accessor
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


# -------------------
# Message Model
# -------------------
class Message(models.Model):
    """
    Represents individual messages within a conversation.
    """
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_sent")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_received", null=True, blank=True)
    message_body = models.TextField(null=False, blank=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.email} to {self.recipient.email} in {self.conversation.conversation_id}"
