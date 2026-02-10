from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User, SellerProfile,Profile
from bluesoko.models import Shop
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username:
            return render(request, "main/login.html", {
                "error": "Username is required."
            })
        if not password:
            return render(request, "main/login.html", {
                "error": "Password is required."
            })
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully Login.")
            return redirect('bluesoko:home')
            
        messages.error(request, "Invalid username or password")
    return render(request, 'main/login.html')


def register(request):
    if request.method == "POST":
        role = request.POST.get("account_type")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        phone = request.POST.get("phone")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        business_name = request.POST.get("business_name")
        business_email = request.POST.get("business_email")
        region = request.POST.get("region")
        
        if not username:
            messages.error(request, "Username is required.")
            return render(request, 'main/register.html')
        
        if not password:
            return render(request, "main/register.html", {
                "error": "password are required."
            })
    
        if password != password2:
            return render(request, "main/register.html", {
                "error": "Passwords do not match"
            })
        
        if not phone:
            return render(request,"main/register.html", {
                "error": "Phone number is required."
            })
            
        if not role or role not in ["buyer", "seller"]:
            return render(request, "main/register.html", {
                "error": "Invalid account type"
            })
            
        if User.objects.filter(username=username).exists():
            return render(request, "main/register.html", {
                "error": "Username already exists"
            })
            
        if email and User.objects.filter(email=email).exists():
            return render(request, "main/register.html", {
                "error": "Email already in use"
            })
            
        if phone and User.objects.filter(phone=phone).exists():
            return render(request, "main/register.html", {
                "error": "Phone number already in use"
            })
            
            # Seller validation
        if role == "seller":
            if not phone:
                return render(request, "main/register.html", {
                    "error": "Phone number is required for sellers"
                })
            if not business_name or not business_email:
                return render(request, "main/register.html", {
                    "error": "Business name and email are required"
                })
            if not region:
                return render(request, "main/register.html", {
                    "error": "Please select your region"
                })
                
        # 🔒 ATOMIC TRANSACTION (IMPORTANT)
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone=phone,
                role=role,
                first_name=first_name,
                last_name=last_name,
            ) 
            if role == "seller":
                seller_profile = SellerProfile.objects.create(
                    user=user,
                    business_name=business_name,
                    business_email=business_email,
                    region=region
                )

        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect("main:login")
    
    return render(request, "main/register.html")


def logout_view(request):
    logout(request)
    
    messages.success(request, "You have successfully Logout.")
    return redirect('main:login')


def test_500(request):
    1 / 0   # This will raise ZeroDivisionError


def test_403(request):
    raise PermissionDenied

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    seller_profile = None
    shop_location = None
    user_shop = None

    # SELLER DATA
    if request.user.role == "seller":
        seller_profile = getattr(request.user, "seller_profile", None)

        if seller_profile:
            shop_location = getattr(seller_profile, "location", None)
            user_shop = Shop.objects.filter(owner=request.user).first()

    # UPDATE PROFILE
    if request.method == "POST":
        avatar = request.FILES.get("avatar")
        address = request.POST.get("address", "").strip()

        # ✅ Validate image type
        if avatar and not avatar.content_type.startswith("image"):
            messages.error(request, "Invalid file type. Please upload an image.")
            return redirect("main:profile")

        # ✅ Validate image size (2MB)
        if avatar and avatar.size > 2 * 1024 * 1024:
            messages.error(request, "Image must be under 2MB.")
            return redirect("main:profile")

        if avatar:
            profile.avatar = avatar

        profile.address = address
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("main:profile")

    return render(request, "main/profile.html", {
        "profile": profile,
        "seller_profile": seller_profile,
        "shop_location": shop_location,
        "user_shop": user_shop,
    })

