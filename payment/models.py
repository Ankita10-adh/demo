from django.db import models
from django.contrib.auth.models import User
import uuid

class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    # Primary key UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Sender (employer) and receiver (employee) — nullable during development
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_payments', null=True, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_payments', null=True, blank=True)

    # Payment amount with default
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Purpose of payment
    purpose = models.CharField(max_length=255, default='General Payment')

    # Unique transaction UUID
    transaction_uuid = models.CharField(max_length=100, default=uuid.uuid4, unique=True)

    # Payment status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Reference ID from eSewa (optional)
    ref_id = models.CharField(max_length=100, null=True, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender_name = self.sender.username if self.sender else "Unknown"
        receiver_name = self.receiver.username if self.receiver else "Unknown"
        return f"{sender_name} → {receiver_name} | {self.amount} ({self.status})"
