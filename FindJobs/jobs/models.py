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
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
