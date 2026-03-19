import re, random, string, requests, math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Incident 
from django.conf import settings
from geopy.distance import geodesic
from django.http import JsonResponse

import random

# --- 1. REGISTRATION & OTP LOGIC ---
# def register(request):
#     if request.method == 'POST':
#         u = request.POST.get('username')
#         e = request.POST.get('email')
#         p = request.POST.get('password')
#         ut = request.POST.get('user_type')
#         ph = request.POST.get('phone')

#         if User.objects.filter(username=u).exists():
#             messages.error(request, "Username already taken.")
#             return render(request, 'register.html')
        
#         # Session ma data mathi rakhne
#         request.session['reg_data'] = {'username': u, 'email': e, 'password': p, 'user_type': ut, 'phone': ph}
        
#         # Demo ko lagi direct OTP page ma pathaune (Email ko wait nagarne)
#         return redirect('verify_otp')
#     return render(request, 'register.html')

def register(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        ut = request.POST.get('user_type')
        ph = request.POST.get('phone')

        if User.objects.filter(username=u).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'register.html')
        

        otp = str(random.randint(100000, 999999))
        

        request.session['reg_otp'] = otp
        request.session['reg_data'] = {'username': u, 'email': e, 'password': p, 'user_type': ut, 'phone': ph}
        

        try:
            send_mail(
                'CEARS Verification Code',
                f'Your OTP for registration is: {otp}',
                settings.EMAIL_HOST_USER,
                [e],
                fail_silently=False,
            )
            messages.success(request, "OTP sent to your email!")
            return redirect('verify_otp')
        except Exception as err:
            print(f"Email Error: {err}")
            messages.error(request, "Failed to send email. Check your internet or App Password.")
            return render(request, 'register.html')

    return render(request, 'register.html')

def verify_otp(request):
    if request.method == 'POST':
        user_code = request.POST.get('otp')
        saved_otp = request.session.get('reg_otp')
        data = request.session.get('reg_data')

        # दुबैलाई String मा ढालेर चेक गर्ने
        if str(user_code) == str(saved_otp): 
            if data:
                new_user = User.objects.create_user(
                    username=data['username'], 
                    email=data['email'], 
                    password=data['password']
                )
                UserProfile.objects.create(
                    user=new_user, 
                    user_type=data['user_type'], 
                    phone_number=data['phone']
                )
                request.session.flush()
                messages.success(request, "Account verified! Please login.")
                return redirect('login')
        else:
            messages.error(request, f"Invalid OTP. Please check your email.")
            
    return render(request, 'verify_otp.html')


# def verify_otp(request):
#     if request.method == 'POST':
#         user_code = request.POST.get('otp')
#         saved_otp = request.session.get('reg_otp') # Real OTP from session
#         data = request.session.get('reg_data')

#         if user_code == saved_otp: # Actual verification
#             if data:
#                 new_user = User.objects.create_user(
#                     username=data['username'], 
#                     email=data['email'], 
#                     password=data['password']
#                 )
#                 UserProfile.objects.create(
#                     user=new_user, 
#                     user_type=data['user_type'], 
#                     phone_number=data['phone']
#                 )
#                 request.session.flush()
#                 messages.success(request, "Account verified! Please login.")
#                 return redirect('login')
#         else:
#             messages.error(request, "Invalid OTP code. Please try again.")
            
#     return render(request, 'verify_otp.html')
# --- 2. LOGIN & LOGOUT ---
def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        
        if user is not None:
            login(request, user)
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.user_type == 'volunteer':
                    return redirect('responder_dashboard')
                return redirect('dashboard')
            except UserProfile.DoesNotExist:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# --- 3. SOS LOGIC ---
@login_required
def send_sos(request):
    if request.method == 'POST':
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        e_type = request.POST.get('emergency_type', 'General')
        desc = request.POST.get('description', 'No details provided.')
        phone = request.POST.get('phone_number', 'Not Provided')

        address = f"Coordinates: {lat}, {lng}"
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}"
            res = requests.get(url, headers={'User-Agent': 'CEARS-App/1.0'}, timeout=5).json()
            address = res.get('display_name', address)
        except: pass

        Incident.objects.create(
            user=request.user, lat=lat, lng=lng, 
            location_name=address, status='Pending', 
            emergency_type=e_type, description=desc, phone_number=phone
        )
        
        messages.success(request, "🚨 SOS Sent! Help is on the way.")
    return redirect('dashboard')

# --- 4. DASHBOARDS ---
@login_required
def dashboard_view(request):
    history = Incident.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'dashboard.html', {'history': history})

@login_required
def responder_dashboard(request):
    incidents = Incident.objects.exclude(status='Resolved').order_by('-timestamp')
    res_lat = request.session.get('res_lat', 27.7172)
    res_lng = request.session.get('res_lng', 85.3240)

    for inc in incidents:
        try:
            dist = geodesic((res_lat, res_lng), (float(inc.lat), float(inc.lng))).km
            inc.dist = f"{round(dist, 2)} km"
        except:
            inc.dist = "Calculating..."
            
    return render(request, 'responder_dashboard.html', {'incidents': incidents})

# --- 5. ACTIONS ---
@login_required
def accept_incident(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    incident.status = 'In Progress'
    incident.volunteer = request.user
    incident.save()
    messages.info(request, "Incident Accepted.")
    return redirect('responder_dashboard')

@login_required
def resolve_incident(request, incident_id):
    inc = get_object_or_404(Incident, id=incident_id)
    if inc.volunteer == request.user:
        inc.status = 'Resolved'
        inc.save()
        messages.success(request, "Incident Resolved.")
    return redirect('responder_dashboard')

# --- 6. API UTILS ---
def update_responder_location(request):
    lat, lng = request.GET.get('lat'), request.GET.get('lng')
    if lat and lng:
        request.session['res_lat'], request.session['res_lng'] = float(lat), float(lng)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)
# --- 7. FORGOT PASSWORD LOGIC ---
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            otp = str(random.randint(100000, 999999))
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp
            send_mail('Reset Code', f'Your Password Reset OTP: {otp}', settings.EMAIL_HOST_USER, [email], fail_silently=True)
            return redirect('verify_password_otp')
        messages.error(request, "Email not found.")
    return render(request, 'forgot_password.html')

def verify_password_otp(request):
    if request.method == 'POST':
        if request.POST.get('otp') == request.session.get('reset_otp'):
            return redirect('reset_password_now')
        messages.error(request, "Invalid OTP.")
    return render(request, 'verify_otp.html')

def reset_password_now(request):
    if request.method == 'POST':
        pw = request.POST.get('new_password')
        cpw = request.POST.get('confirm_password')
        if pw == cpw:
            email = request.session.get('reset_email')
            user = User.objects.get(email=email)
            user.set_password(pw)
            user.save()
            messages.success(request, "Password reset successful! Please login.")
            return redirect('login')
        messages.error(request, "Passwords do not match.")
    return render(request, 'reset_password_now.html')