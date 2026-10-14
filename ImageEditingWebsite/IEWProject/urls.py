from django.contrib import admin
from django.urls import include, path
from editingapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('editingapp.urls')),
]