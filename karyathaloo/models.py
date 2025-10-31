

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


