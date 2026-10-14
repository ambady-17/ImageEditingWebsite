# from django.conf.urls import url
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
 path('', views.first_view, name='first_view'),
 path('contact/', views.contact_view, name='contact_view'),
 path('about/', views.about_view, name='about_view'),
 path('register/', views.register_view, name='register_view'),
 path('login/', views.login_view, name='login_view'), 
 path('forgot-password/', views.forgot_password_view, name='forgot_password_view'),
 path('logout/', views.logout_view, name='logout_view'), 
 path('auto-logout/', views.browser_close_logout, name='browser_close_logout'),
 path('dface/', views.dface, name='dface'),
 path('editor/', views.editor_view, name='editor_view'),
 path('editor/upload/', views.editor_upload_image, name='editor_upload_image'),
 path('messages/', views.message_center, name='message_center'),
 path('gray/', views.gray_fun, name='gray_fun'),
 path('edge/', views.edge_fun, name='edge_fun'),
 path('change/', views.change_fun, name='change_fun'),
 path('brightp/', views.brightp_fun, name='brightp_fun'),
 path('brightn/', views.brightn_fun, name='brightn_fun'),
 path('scaleup/', views.scaleup_fun, name='scaleup_fun'),
 path('scaledown/', views.scaledown_fun, name='scaledown_fun'),
 path('filter/', views.filter_fun, name='filter_fun'),
 path('crop/', views.crop_fun, name='crop_fun'),
 path('croppage/', views.crop_html, name='crop_html'),
 path('blur/',views.blur_fun,name='blur_fun'),
 path('gaussian/',views.gaussian_fun,name='gaussian_fun'),
 path('sharpen/',views.sharpen_fun,name='sharpen_fun'),
 path('sepia/',views.sepia_fun,name='sepia_fun'),
 path('negative/',views.negative_fun,name='negative_fun'),
 path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
 path('admin-images/', views.admin_images, name='admin_images'),
 path('admin-images/<int:image_id>/delete/', views.admin_delete_image, name='admin_delete_image'),
 path('admin-users/', views.admin_users, name='admin_users'),
 path('admin-users/add/', views.admin_add_user, name='admin_add_user'),
 path('admin-users/<int:user_id>/toggle-superuser/', views.admin_toggle_superuser, name='admin_toggle_superuser'),
 path('admin-users/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
 path('admin-settings/', views.admin_settings, name='admin_settings'),
 path('admin-messages/<int:message_id>/reply/', views.admin_reply_message, name='admin_reply_message'),
 path('admin-messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),
 path('my-messages/', views.user_messages, name='user_messages'),
 
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
