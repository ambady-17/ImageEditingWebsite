from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from .forms import ImageUploadForm
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .opencv_fun import opencv_gray,opencv_edge,opencv_brightp,opencv_brightn,opencv_scaleup,opencv_scaledown,opencv_filter,opencv_crop
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone
from django.core.mail import send_mail
import os
import shutil
from django.contrib.auth.decorators import login_required, user_passes_test
from .opencv_fun import opencv_blur,opencv_gaussian,opencv_sharpen,opencv_sepia,opencv_negative

loc=''
loc_new=''
loc_temp=''
loc_temp_new=''

def _ensure_reg_login_background():
  source_dir = os.path.join(settings.BASE_DIR, 'reg_login')
  dest_dir = os.path.join(settings.MEDIA_ROOT, 'reg_login')
  os.makedirs(dest_dir, exist_ok=True)
  if os.path.isdir(source_dir):
    for name in sorted(os.listdir(source_dir)):
      file_path = os.path.join(source_dir, name)
      if os.path.isfile(file_path):
        dest_path = os.path.join(dest_dir, name)
        if not os.path.exists(dest_path):
          try:
            shutil.copy2(file_path, dest_path)
          except Exception:
            continue


def _get_auth_bg():
  _ensure_reg_login_background()
  bg_dir = os.path.join(settings.MEDIA_ROOT, 'reg_login')
  if os.path.isdir(bg_dir):
    for name in sorted(os.listdir(bg_dir)):
      _, ext = os.path.splitext(name)
      if ext.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
        return settings.MEDIA_URL + 'reg_login/' + name
  return '/static/assets/img/portfolio/portfolio-1.jpg'


def _ensure_editor_background():
  source_dir = os.path.join(settings.BASE_DIR, 'editing_page')
  dest_dir = os.path.join(settings.MEDIA_ROOT, 'editing_page')
  os.makedirs(dest_dir, exist_ok=True)
  if os.path.isdir(source_dir):
    for name in sorted(os.listdir(source_dir)):
      file_path = os.path.join(source_dir, name)
      if os.path.isfile(file_path):
        dest_path = os.path.join(dest_dir, name)
        if not os.path.exists(dest_path):
          try:
            shutil.copy2(file_path, dest_path)
          except Exception:
            continue


def _get_editor_bg():
  _ensure_editor_background()
  bg_dir = os.path.join(settings.MEDIA_ROOT, 'editing_page')
  if os.path.isdir(bg_dir):
    for name in sorted(os.listdir(bg_dir)):
      _, ext = os.path.splitext(name)
      if ext.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
        return settings.MEDIA_URL + 'editing_page/' + name
  return '/static/assets/img/portfolio/portfolio-1.jpg'


def _get_site_setting():
  setting, _ = SiteSetting.objects.get_or_create(pk=1)
  return setting


def _format_storage_usage():
  total_bytes = 0
  for img in ImageUploadModel.objects.all():
    try:
      total_bytes += os.path.getsize(img.document.path)
    except Exception:
      continue
  if total_bytes < 1024:
    return f"{total_bytes} bytes"
  if total_bytes < 1024*1024:
    return f"{total_bytes//1024} KB"
  return f"{total_bytes / (1024*1024):.1f} MB"


def _admin_check(user):
  return user.is_active and (user.is_staff or user.is_superuser)


def admin_required(view_func):
  return user_passes_test(_admin_check, login_url='/login/')(view_func)


def first_view(request):
  source_dir = os.path.join(settings.BASE_DIR, 'Home image')
  dest_dir = os.path.join(settings.MEDIA_ROOT, 'home_slider')
  os.makedirs(dest_dir, exist_ok=True)

  slider_images = []
  if os.path.isdir(source_dir):
    for name in sorted(os.listdir(source_dir)):
      file_path = os.path.join(source_dir, name)
      _, ext = os.path.splitext(name)
      if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] and os.path.isfile(file_path):
        dest_path = os.path.join(dest_dir, name)
        if not os.path.exists(dest_path):
          try:
            shutil.copy2(file_path, dest_path)
          except Exception:
            continue
        slider_images.append(settings.MEDIA_URL + 'home_slider/' + name)

  if not slider_images:
    # fallback static images if none in Home image folder
    slider_images = [
      '/static/assets/img/portfolio/portfolio-1.jpg',
      '/static/assets/img/portfolio/portfolio-2.jpg',
      '/static/assets/img/portfolio/portfolio-3.jpg'
    ]

  return render(request, 'first.html', {'slider_images': slider_images})

def contact_view(request):
  if request.method == 'POST':
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    subject = request.POST.get('subject', '').strip()
    message_text = request.POST.get('message', '').strip()

    if not subject or not message_text:
      messages.error(request, 'Subject and message are required.')
      return render(request, 'contact.html', {
        'name': name,
        'email': email,
        'phone': phone,
        'subject': subject,
        'message': message_text
      })

    ContactMessage.objects.create(
      user=request.user if request.user.is_authenticated else None,
      name=name,
      email=email,
      phone=phone,
      subject=subject,
      message=message_text
    )
    messages.success(request, 'Your message has been sent. Our admin team will review it soon.')
    return redirect('contact_view')

  return render(request, 'contact.html', {})

def about_view(request):
  return render(request, 'about.html', {})

def register_view(request):
    if request.method == "POST":
        username = request.POST['username'].strip()
        fname = request.POST['fname'].strip()
        lname = request.POST['lname'].strip()
        email = request.POST['email'].strip()
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        # Check if username already exists
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register_view')
        
        # Check if email already exists
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('register_view')
        
        # Validate username length
        if len(username) > 20:
            messages.error(request, "Username must be under 20 characters!")
            return redirect('register_view')
        
        # Validate username is alphanumeric
        if not username.replace('_', '').replace('-', '').isalnum():
            messages.error(request, "Username must be alphanumeric!")
            return redirect('register_view')
        
        # Validate password match
        if pass1 != pass2:
            messages.error(request, "Passwords don't match!")
            return redirect('register_view')
        
        # Validate email format
        try:
            from django.core.validators import validate_email
            validate_email(email)
        except:
            messages.error(request, "Please enter a valid email address!")
            return redirect('register_view')
        
        # Create user with proper exception handling
        try:
            myuser = User.objects.create_user(username, email, pass1)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.save()
            messages.success(request, f"Account created successfully. Welcome, {username}!")
            return redirect('login_view')
        except IntegrityError as e:
            if 'username' in str(e):
                messages.error(request, "Username already exists!")
            elif 'email' in str(e):
                messages.error(request, "Email already registered!")
            else:
                messages.error(request, "Registration failed. Please try again.")
            return redirect('register_view')
        except Exception as e:
            messages.error(request, "Registration failed. Please try again.")
            return redirect('register_view')

    return render(request, "signup.html", {'auth_bg': _get_auth_bg()})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect(reverse('admin_dashboard') + '?fresh=1')
        return redirect(reverse('editor_view') + '?fresh=1')

    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            request.session.set_expiry(0)
            messages.success(request, f"Welcome back, {username}!")
            if user.is_staff or user.is_superuser:
                admin_url = reverse('admin_dashboard') + '?fresh=1'
                return redirect(admin_url)
            editor_url = reverse('editor_view') + '?fresh=1'
            return redirect(editor_url)
    
        else:
            messages.error(request, "Invalid Username or Password")
            return redirect('login_view')
    
    return render(request, "signin.html", {'auth_bg': _get_auth_bg()})


def forgot_password_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        new_pass1 = request.POST.get('new_pass1', '')
        new_pass2 = request.POST.get('new_pass2', '')

        if not username or not new_pass1 or not new_pass2:
            messages.error(request, 'All fields are required.')
        elif new_pass1 != new_pass2:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                user = User.objects.get(username=username)
                user.set_password(new_pass1)
                user.save()
                messages.success(request, 'Password reset successfully. Please log in with your new password.')
                return redirect('login_view')
            except User.DoesNotExist:
                messages.error(request, 'No account found with that username.')

    return render(request, "forgot_password.html", {'auth_bg': _get_auth_bg()})


@admin_required
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged Out Successfully !")
    return redirect('/')

@login_required(login_url='/login/')
def browser_close_logout(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required.'}, status=405)
    logout(request)
    return JsonResponse({'ok': True})

@login_required(login_url='/login/')
def editor_view(request):
    global loc, loc_new, loc_temp, loc_temp_new
    editor_bg = _get_editor_bg()

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()

            loc = os.path.join(settings.MEDIA_ROOT, post.document.name)
            loc_new = settings.MEDIA_URL + post.document.name
            name, ext = os.path.splitext(loc)
            loc_temp = name + "_temp" + ext
            loc_temp_new = settings.MEDIA_URL + post.document.name.rsplit('.',1)[0] + "_temp." + post.document.name.rsplit('.',1)[1]

            return render(request, 'editor.html', {
                'form': form,
                'post': post,
                'path': loc_new,
                'path_temp': loc_temp_new,
                'editor_bg': editor_bg
            })

    else:
        form = ImageUploadForm()
        # Clear global variables on fresh page load (GET request)
        loc = ''
        loc_new = ''
        loc_temp = ''
        loc_temp_new = ''

    return render(request, 'editor.html', {
        'form': form,
        'editor_bg': editor_bg,
        'path': loc_new if loc_new else None,
        'path_temp': loc_temp_new if loc_temp_new else None,
        'post': None
    })

@login_required(login_url='/login/')
def editor_upload_image(request):
    global loc, loc_new, loc_temp, loc_temp_new
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required.'}, status=405)

    form = ImageUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        error_msg = ', '.join([f"{field}: {error[0]}" for field, error in form.errors.items()])
        print(f'Form validation failed: {error_msg}')
        return JsonResponse({'ok': False, 'error': f'Invalid upload: {error_msg}', 'errors': form.errors}, status=400)

    try:
        post = form.save()
        loc = os.path.join(settings.MEDIA_ROOT, post.document.name)
        loc_new = settings.MEDIA_URL + post.document.name
        name, ext = os.path.splitext(loc)
        loc_temp = name + "_temp" + ext
        loc_temp_new = settings.MEDIA_URL + post.document.name.rsplit('.',1)[0] + "_temp." + post.document.name.rsplit('.',1)[1]

        # Verify the image file exists
        if not os.path.exists(loc):
            print(f'Uploaded file not found at: {loc}')
            return JsonResponse({'ok': False, 'error': 'File was saved but not accessible'}, status=500)

        print(f'Image uploaded successfully: {loc}')
        return JsonResponse({
            'ok': True,
            'path': loc_new,
            'path_temp': loc_temp_new
        })
    except Exception as e:
        print(f'Error in editor_upload_image: {str(e)}')
        return JsonResponse({'ok': False, 'error': f'Server error: {str(e)}'}, status=500)

@login_required(login_url='/login/')
def dface(request):
    return editor_view(request)


@login_required(login_url='/login/')
def gray_fun(request):
    global  loc,loc_new,loc_temp,loc_temp_new  
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_gray(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in gray_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

@login_required(login_url='/login/')
def edge_fun(request):
    global  loc,loc_new,loc_temp,loc_temp_new  
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_edge(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in edge_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

@login_required(login_url='/login/')
def change_fun(request):
    global  loc,loc_new,loc_temp,loc_temp_new  
    try:
        # Check if temporary file exists before attempting to replace
        if not os.path.exists(loc_temp):
            return JsonResponse({'action_done': False, 'error': 'No edited version found. Apply an effect first.'})
        
        # Check if original file exists before removing
        if os.path.exists(loc):
            os.remove(loc)
        
        # Rename temp file to original
        os.rename(loc_temp, loc)
        
        return JsonResponse({'action_done': True, 'message': 'Changes applied to image'})
    except Exception as e:
        print(f'Error in change_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': f'Failed to apply changes: {str(e)}'})

@login_required(login_url='/login/')
def brightp_fun(request):
    global  loc,loc_new,loc_temp,loc_temp_new   
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_brightp(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in brightp_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

@login_required(login_url='/login/')
def brightn_fun(request):
    global  loc,loc_new,loc_temp,loc_temp_new  
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_brightn(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in brightn_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

@login_required(login_url='/login/')
def scaledown_fun(request):
    global  loc,loc_new,loc_temp,loc_temp_new  
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_scaledown(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in scaledown_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

@login_required(login_url='/login/')
def scaleup_fun(request):
    global  loc,loc_new,loc_temp,loc_temp_new  
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_scaleup(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in scaleup_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

@login_required(login_url='/login/')
def crop_html(request):    
    return render(request, 'crophtml.html')

@login_required(login_url='/login/')
def crop_fun(request):
    if 'xname' in request.GET: 
        x = request.GET['xname']
        y = request.GET['yname']
        wd = request.GET['width']
        ht = request.GET['height']
        print('done')
    else:
        x = None
        y = None
        wd = None
        ht = None
    global  loc,loc_new,loc_temp,loc_temp_new   
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    opencv_crop(loc,loc_temp,x,y,wd,ht)
    return render(request, 'crophtml.html',{'path':loc_new, 'path_temp':loc_temp_new})

@login_required(login_url='/login/')
def filter_fun(request):
    global  loc,loc_new,loc_temp,loc_temp_new  
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_filter(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in filter_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

@login_required(login_url='/login/')
def blur_fun(request):
    global loc,loc_new,loc_temp,loc_temp_new
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_blur(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in blur_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

@login_required(login_url='/login/')
def gaussian_fun(request):
    global loc,loc_new,loc_temp,loc_temp_new
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_gaussian(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in gaussian_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

@login_required(login_url='/login/')
def sharpen_fun(request):
    global loc,loc_new,loc_temp,loc_temp_new
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_sharpen(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in sharpen_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

@login_required(login_url='/login/')
def sepia_fun(request):
    global loc,loc_new,loc_temp,loc_temp_new
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_sepia(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in sepia_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

@login_required(login_url='/login/')
def negative_fun(request):
    global loc,loc_new,loc_temp,loc_temp_new
    if not loc or not os.path.exists(loc):
        return JsonResponse({'action_done': False, 'error': 'No image uploaded. Please upload an image first.'})
    try:
        opencv_negative(loc,loc_temp)
        if os.path.exists(loc_temp):
            return JsonResponse({'action_done': True, 'path': loc_new, 'path_temp': loc_temp_new})
        else:
            return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})
    except Exception as e:
        print(f'Error in negative_fun: {str(e)}')
        return JsonResponse({'action_done': False, 'error': 'Failed to process image. Please try again.'})

from .models import ImageUploadModel, SiteSetting, ContactMessage, AdminReply, AdminActivityLog

@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_uploaded_images = ImageUploadModel.objects.count()
    total_edited_images = ImageUploadModel.objects.filter(description__gt='').count()
    recent_activity = ImageUploadModel.objects.order_by('-uploaded_at')[:5]
    storage_usage = _format_storage_usage()

    return render(request, 'admin_dashboard.html', {
        'total_users': total_users,
        'total_uploaded_images': total_uploaded_images,
        'total_edited_images': total_edited_images,
        'recent_activity': recent_activity,
        'storage_usage': storage_usage,
        'site_setting': _get_site_setting()
    })


@admin_required
def admin_images(request):
    images = ImageUploadModel.objects.all().order_by('-uploaded_at')
    return render(request, 'admin_images.html', {
        'images': images,
        'site_setting': _get_site_setting()
    })


@admin_required
def admin_delete_image(request, image_id):
    if request.method != 'POST':
        return redirect('admin_images')

    image = get_object_or_404(ImageUploadModel, pk=image_id)
    if image.document:
        try:
            os.remove(image.document.path)
        except Exception:
            pass
    image.delete()
    messages.success(request, 'Image deleted successfully.')
    return redirect('admin_images')


@admin_required
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    staff_count = User.objects.filter(is_staff=True).count()
    superuser_count = User.objects.filter(is_superuser=True).count()
    return render(request, 'admin_users.html', {
        'users': users,
        'staff_count': staff_count,
        'superuser_count': superuser_count,
        'site_setting': _get_site_setting()
    })


@admin_required
def admin_add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', 'user')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return redirect('admin_users')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('admin_users')

        user = User.objects.create_user(username=username, email=email, password=password)
        if role == 'staff':
            user.is_staff = True
        elif role == 'superuser':
            user.is_staff = True
            user.is_superuser = True
        user.save()
        messages.success(request, f'User {username} created successfully.')
    return redirect('admin_users')


@admin_required
def admin_toggle_superuser(request, user_id):
    if request.method == 'POST':
        user_obj = get_object_or_404(User, pk=user_id)
        if user_obj == request.user:
            messages.error(request, 'You cannot change your own superuser status.')
            return redirect('admin_users')
        user_obj.is_superuser = not user_obj.is_superuser
        if user_obj.is_superuser:
            user_obj.is_staff = True
        user_obj.save()
        messages.success(request, f'Superuser status updated for {user_obj.username}.')
    return redirect('admin_users')


@admin_required
def admin_delete_user(request, user_id):
    if request.method == 'POST':
        user_obj = get_object_or_404(User, pk=user_id)
        if user_obj == request.user:
            messages.error(request, 'You cannot delete your own account while signed in.')
            return redirect('admin_users')
        user_obj.delete()
        messages.success(request, 'User deleted successfully.')
    return redirect('admin_users')


@admin_required
def admin_settings(request):
    site_setting = _get_site_setting()
    storage_usage = _format_storage_usage()

    if request.method == 'POST':
        site_setting.site_name = request.POST.get('site_name', site_setting.site_name).strip() or site_setting.site_name
        if request.FILES.get('logo'):
            site_setting.logo = request.FILES['logo']
        site_setting.save()
        messages.success(request, 'Settings updated successfully.')
        return redirect('admin_settings')

    return render(request, 'admin_settings.html', {
        'site_setting': site_setting,
        'storage_usage': storage_usage
    })


@admin_required
def message_center(request):
    if request.method == 'POST' and 'mark_read' in request.POST:
        read_ids = request.POST.getlist('mark_read')
        ContactMessage.objects.filter(id__in=read_ids).update(is_read=True)
        messages.success(request, 'Messages marked as read.')
        return redirect('message_center')

    # Get all messages with replies prefetched
    contact_messages = ContactMessage.objects.prefetch_related('replies', 'replies__admin_user').all().order_by('-created_at')
    
    # Categorize messages
    replied_messages = [msg for msg in contact_messages if msg.replies.exists()]
    unreplied_messages = [msg for msg in contact_messages if not msg.replies.exists()]
    
    return render(request, 'editingapp/admin_messages.html', {
        'contact_messages': contact_messages,
        'replied_messages': replied_messages,
        'unreplied_messages': unreplied_messages,
        'site_setting': _get_site_setting()
    })


@admin_required
def admin_reply_message(request, message_id):
    """Admin replies to a contact message."""
    if request.method != 'POST':
        return redirect('message_center')

    contact_msg = get_object_or_404(ContactMessage, pk=message_id)
    reply_body = request.POST.get('reply_body', '').strip()

    if not reply_body:
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return JsonResponse({'success': False, 'error': 'Reply cannot be empty.'})
        else:
            messages.error(request, 'Reply cannot be empty.')
            return redirect('message_center')

    try:
        AdminReply.objects.create(
            contact_message=contact_msg,
            admin_user=request.user,
            body=reply_body
        )
        # Mark the message as read when replying
        if not contact_msg.is_read:
            contact_msg.is_read = True
            contact_msg.save()

        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return JsonResponse({'success': True, 'message': f'Reply sent to "{contact_msg.name}" successfully.'})
        else:
            messages.success(request, f'Reply sent to "{contact_msg.name}" successfully.')
            return redirect('message_center')
            
    except Exception as e:
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return JsonResponse({'success': False, 'error': f'Failed to send reply: {str(e)}'})
        else:
            messages.error(request, f'Failed to send reply: {str(e)}')
            return redirect('message_center')


@admin_required
def delete_message(request, message_id):
    """Delete a contact message and all associated replies."""
    if request.method != 'POST':
        return redirect('message_center')

    try:
        message = get_object_or_404(ContactMessage, pk=message_id)
        message_name = message.name
        
        # Delete the message (this will also delete associated replies due to CASCADE)
        message.delete()
        
        # Log admin activity
        AdminActivityLog.objects.create(
            admin_username=request.user.username,
            action=f"Deleted message from {message_name}"
        )
        
        # Check if this is an AJAX request - improved detection
        is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 
            request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' or
            'application/json' in request.headers.get('Content-Type', '')
        )
        
        if is_ajax:
            return JsonResponse({'success': True, 'message': f'Message from {message_name} deleted successfully.'})
        else:
            messages.success(request, f'Message from {message_name} deleted successfully.')
            return redirect('message_center')
            
    except Exception as e:
        # Check if this is an AJAX request - improved detection
        is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 
            request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' or
            'application/json' in request.headers.get('Content-Type', '')
        )
        
        if is_ajax:
            return JsonResponse({'success': False, 'error': f'Failed to delete message: {str(e)}'})
        else:
            messages.error(request, f'Failed to delete message: {str(e)}')
            return redirect('message_center')


@login_required(login_url='/login/')
def user_messages(request):
    """Shows the logged-in user their contact messages and any admin replies."""
    from django.db.models import Q
    # Match by user FK or by email so older messages (before user field) also show
    filters = Q(user=request.user)
    if request.user.email:
        filters |= Q(email__iexact=request.user.email)
    user_contact_messages = ContactMessage.objects.filter(
        filters
    ).prefetch_related('replies', 'replies__admin_user').distinct().order_by('-created_at')

    return render(request, 'user_messages.html', {
        'user_contact_messages': user_contact_messages
    })


@admin_required
def reply_message(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'})
    
    message_id = request.POST.get('message_id')
    subject = request.POST.get('subject', '').strip()
    reply_text = request.POST.get('message', '').strip()
    
    if not message_id or not subject or not reply_text:
        return JsonResponse({'success': False, 'error': 'All fields are required'})
    
    try:
        # Get the original message
        original_message = ContactMessage.objects.get(id=message_id)
        
        if not original_message.email:
            return JsonResponse({'success': False, 'error': 'No email address available for this contact'})
        
        # Prepare email content
        email_subject = subject
        email_body = f"""Dear {original_message.name},

Thank you for contacting us. Here is our reply to your message:

{reply_text}

---
Original Message:
Subject: {original_message.subject}
{original_message.message}

---
Best regards,
IEW Support Team
Image Editing Website"""
        
        # Send email
        try:
            send_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@iew.com',
                [original_message.email],
                fail_silently=False,
            )
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Failed to send email: {str(e)}'})
        
        # Create AdminReply record for user message display
        AdminReply.objects.create(
            contact_message=original_message,
            admin_user=request.user,
            body=reply_text
        )
        
        # Update message with reply details (for admin display)
        original_message.is_replied = True
        original_message.replied_at = timezone.now()
        original_message.reply_subject = subject
        original_message.reply_message = reply_text
        original_message.save()
        
        # Log admin activity
        AdminActivityLog.objects.create(
            admin_username=request.user.username,
            action=f"Replied to message from {original_message.name} ({original_message.email})"
        )
        
        return JsonResponse({'success': True, 'message': 'Reply sent successfully'})
        
    except ContactMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})