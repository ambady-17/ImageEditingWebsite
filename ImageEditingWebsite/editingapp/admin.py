from django.contrib import admin
from .models import ImageUploadModel, UserMessage, ContactMessage, AdminReply

# Register your models here.
admin.site.register(ImageUploadModel)
admin.site.register(UserMessage)
admin.site.register(ContactMessage)
admin.site.register(AdminReply)