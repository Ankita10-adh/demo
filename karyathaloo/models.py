

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=14, null=True, blank=True)
    image = models.FileField(null=True, blank=True, upload_to='user_images/')
    gender = models.CharField(max_length=15, null=True, blank=True)
    type = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.user.username


# -----------------------------
# Recruiter model
# -----------------------------
class Recruiter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True) 
    mobile = models.CharField(max_length=14, null=True, blank=True)
    image = models.FileField(null=True, blank=True, upload_to='recruiter_images/')
    gender = models.CharField(max_length=15, null=True, blank=True)
    type = models.CharField(max_length=15, null=True, blank=True)
    company = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.username


# -----------------------------
# Job model
# -----------------------------
class Job(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, null=True, blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    experience = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    skills = models.CharField(max_length=300, blank=True, null=True)
    creation_date = models.DateField(auto_now_add=True)

    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Internship', 'Internship')
    ]
    WORK_MODE_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline')
    ]

    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, null=True, blank=True)
    work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.title


# -----------------------------
# Job Application model
# -----------------------------
class Apply(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    resume = models.FileField(null=True, blank=True, upload_to='resumes/')
    apply_date = models.DateField(auto_now_add=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.student.user.username} applied to {self.job.title}"



class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.email


# -----------------------------
# Payment System for Recruiters
# -----------------------------
"""import uuid

class PaymentTransaction(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    ref_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')  # Pending, Success, Failed
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recruiter.user.username} - {self.amount} ({self.status})"""


# In your existing models.py file, add these two new models:

# -----------------------------
# 1. Payment Request/Payout Ledger (NEW)
# Tracks the recruiter's intent to pay a user for a specific job application.
# -----------------------------
class RecruiterPayout(models.Model):
    # The application this payment is related to (links Recruiter, Job, and Student)
    application = models.OneToOneField('Apply', on_delete=models.CASCADE, 
                                     limit_choices_to={'status': 'Accepted'}, 
                                     help_text="Payout is only created for 'Accepted' applications.")
    
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    student = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    
    # Amount paid (can be the Job.salary or a portion thereof)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status of the entire payout process (Recruiter's internal ledger status)
    PAYOUT_STATUS_CHOICES = [
        ('PENDING', 'Payment Pending'),
        ('INITIATED', 'Payment Initiated'),
        ('COMPLETED', 'Payment Completed'),
        ('FAILED', 'Payment Failed'),
    ]
    payout_status = models.CharField(max_length=20, choices=PAYOUT_STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payout for {self.student.user.username} on {self.application.job.title} - {self.payout_status}"





# -----------------------------
# 2. External Transaction Details (NEW)
# Records the details from the external payment gateway (e.g., bank, PayPal, etc.)
# -----------------------------
class PaymentTransaction(models.Model):
    payout = models.ForeignKey(RecruiterPayout, on_delete=models.CASCADE)
    
    # Generic fields for any external payment system
    transaction_id = models.CharField(max_length=150, unique=True, null=True, blank=True)
    gateway_name = models.CharField(max_length=50, default='Internal Ledger') # e.g., 'Esewa', 'PayPal'
    
    TRANSACTION_STATUS_CHOICES = [
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    transaction_status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='PROCESSING')
    
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Txn for Payout #{self.payout.id} via {self.gateway_name}"