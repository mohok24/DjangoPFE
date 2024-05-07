from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings

class User(AbstractUser):
    role = models.CharField(max_length=30)
    user_permissions = models.ManyToManyField(Permission, related_name='user_permissions_set')

class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    age = models.IntegerField()

class Report(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    type = models.CharField(max_length=255, default="N/A")
    indication = models.CharField(max_length=255, default="N/A")
    leftM = models.CharField(max_length=255, default="N/A")
    rightM = models.CharField(max_length=255, default="N/A")
    bothM = models.CharField(max_length=255, default="N/A")
    leftE = models.CharField(max_length=255, default="N/A")
    rightE = models.CharField(max_length=255, default="N/A")
    bothE = models.CharField(max_length=255, default="N/A")
    leftclassification = models.CharField(max_length=255, default="N/A")
    rightclassification = models.CharField(max_length=255, default="N/A")
    bothclassification = models.CharField(max_length=255,default="N/A")
    conclusion = models.CharField(max_length=255, default="N/A")
    recommendations = models.CharField(max_length=255, default="N/A")

class Struct(models.Model):
    struct_desc = models.CharField(max_length=255)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject=models.TextField(max_length=100, default="N/A")
    content = models.TextField(default="N/A")
    previous_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='next_messages')
    image = models.FileField(upload_to='static/message_attachments/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} ({self.timestamp})"
