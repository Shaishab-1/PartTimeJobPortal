from django.db import models

from django.contrib.auth.models import User

class Job(models.Model):
    post = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    work_hour = models.CharField(max_length=200)
    hourly_pay = models.IntegerField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.post


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.applicant.username} - {self.job.post}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField(null=True, blank=True)
    qualifications = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    professional_details = models.TextField(blank=True)

    @property
    def is_complete(self):
        return all([self.age, self.qualifications, self.skills])

    def __str__(self):
        return f"Profile for {self.user.username}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_application', 'New Application'),
        ('application_approved', 'Application Approved'),
        ('application_rejected', 'Application Rejected'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='new_application')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.notification_type}"
