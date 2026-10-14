from django.db import models
from django.contrib.auth.models import User

class ImageUploadModel(models.Model):
  description = models.CharField(max_length=255, blank=True)
  document = models.ImageField(upload_to='images')
  uploaded_at = models.DateTimeField(auto_now_add=True)


class SiteSetting(models.Model):
  site_name = models.CharField(max_length=120, default='IEW Admin')
  logo = models.ImageField(upload_to='site/', blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)


class AdminActivityLog(models.Model):
  admin_username = models.CharField(max_length=150)
  action = models.CharField(max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)


class UserMessage(models.Model):
  sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
  recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
  subject = models.CharField(max_length=200)
  body = models.TextField()
  is_read = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-created_at']


class ContactMessage(models.Model):
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_messages')
  name = models.CharField(max_length=200)
  email = models.EmailField(blank=True)
  phone = models.CharField(max_length=50, blank=True)
  subject = models.CharField(max_length=200)
  message = models.TextField()
  is_read = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-created_at']


class AdminReply(models.Model):
  contact_message = models.ForeignKey(ContactMessage, on_delete=models.CASCADE, related_name='replies')
  admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_replies')
  body = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['created_at']

  def __str__(self):
    return f"Reply to '{self.contact_message.subject}' by {self.admin_user}"