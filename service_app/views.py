# Import render and redirect
from django.shortcuts import render, redirect

# Import Django messages
from django.contrib import messages

# Import Django authentication functions
from django.contrib.auth import authenticate, login, logout

# Import our registration form
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.db.models import Q,Avg
from django.db import models 

from .models import Category, Service, CustomerProfile, ProviderProfile, Booking,Review,Favorite,Notification,ContactEnquiry
# ============================================================
# HOME PAGE
# ============================================================

def home(request):

    return render(
        request,
        "home.html"
    )


# ============================================================
# REGISTRATION
# ============================================================
def register_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        form = RegistrationForm(request.POST)

        if form.is_valid():

            # Save user
            user = form.save()

            # Get selected role
            role = form.cleaned_data.get("role")

            # Create profile
            if role == "customer":
                CustomerProfile.objects.create(user=user)

            elif role == "provider":
                ProviderProfile.objects.create(user=user)

            messages.success(
                request,
                "Account created successfully! Please login to continue."
            )

            return redirect("login")

    else:
        form = RegistrationForm()

    return render(request, "register.html", {
        "form": form
    })

# ============================================================
# LOGIN
# ============================================================
def login_view(request):

    # ----------------------------------------------------
    # ALREADY LOGGED-IN USER
    # ----------------------------------------------------
    # If user is already logged in,
    # send them to their correct dashboard.

    if request.user.is_authenticated:

        # Admin
        if request.user.is_superuser:
            return redirect("admin_dashboard")

        # Customer
        elif hasattr(request.user, "customerprofile"):
            return redirect("customer_dashboard")

        # Service Provider
        elif hasattr(request.user, "providerprofile"):
            return redirect("provider_dashboard")

        # User without role
        return redirect("dashboard")


    # ----------------------------------------------------
    # CHECK LOGIN FORM
    # ----------------------------------------------------

    if request.method == "POST":

        # Get username from form
        username = request.POST.get("username")

        # Get password from form
        password = request.POST.get("password")


        # ----------------------------------------------------
        # AUTHENTICATE USER
        # ----------------------------------------------------
        #
        # authenticate() checks the username and password.
        #
        # If credentials are correct:
        #     User object is returned.
        #
        # If credentials are incorrect:
        #     None is returned.
        # ----------------------------------------------------

        user = authenticate(
            request,
            username=username,
            password=password
        )


        # ----------------------------------------------------
        # CHECK USER
        # ----------------------------------------------------

        if user is not None:

            # Create login session
            login(
                request,
                user
            )


            # Show success message
            messages.success(
                request,
                "Login successful! Welcome to ServiceHub."
            )


            # ------------------------------------------------
            # ROLE-BASED REDIRECT
            # ------------------------------------------------

            # Admin
            if user.is_superuser:
                return redirect("admin_dashboard")

            # Customer
            elif hasattr(user, "customerprofile"):
                return redirect("customer_dashboard")

            # Service Provider
            elif hasattr(user, "providerprofile"):
                return redirect("provider_dashboard")

            # User without assigned role
            else:
                return redirect("dashboard")


        else:

            # Wrong username or password
            messages.error(
                request,
                "Invalid username or password."
            )


    # Display login page
    return render(
        request,
        "login.html"
    )

@login_required(login_url="login")
def dashboard(request):

    # Open dashboard.html
    return render(
        request,
        "dashboard.html"
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    # Logout current user
    logout(request)


    # Show message
    messages.success(
        request,
        "You have been logged out successfully."
    )


    # Go to Login page
    return redirect("login")


# ============================================================
# CUSTOM ADMIN LOGIN
# ============================================================
def admin_login(request):

    # If form is submitted
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check username and password
        user = authenticate(request, username=username, password=password)

        # Check user is admin
        if user is not None and user.is_superuser:

            login(request, user)

            messages.success(request, "Admin login successful!")

            return redirect("admin_dashboard")

        else:
            messages.error(request, "Invalid admin username or password.")

    return render(request, "admin_login.html")


# ============================================================
# CUSTOM ADMIN DASHBOARD
# ============================================================


@login_required(login_url="admin_login")
def admin_dashboard(request):

    # Only admin/staff user can access
    if not request.user.is_staff:
        return redirect("home")

    # Main counts
    total_users = User.objects.filter(
        is_staff=False
    ).count()

    total_categories = Category.objects.count()

    total_services = Service.objects.count()

    total_bookings = Booking.objects.count()

    total_reviews = Review.objects.count()

    total_enquiries = ContactEnquiry.objects.count()

    pending_enquiries = ContactEnquiry.objects.filter(
        status="pending"
    ).count()

    return render(
        request,
        "admin_dashboard.html",
        {
            "total_users": total_users,
            "total_categories": total_categories,
            "total_services": total_services,
            "total_bookings": total_bookings,
            "total_reviews": total_reviews,
            "total_enquiries": total_enquiries,
            "pending_enquiries": pending_enquiries,
        }
    )


@login_required(login_url="admin_login")
def category_list(request):

    # Only admin can access
    if not request.user.is_superuser:
        return redirect("dashboard")

    # Get all categories
    categories = Category.objects.all().order_by("-id")

    return render(request, "category_list.html", {
        "categories": categories
    })


# ============================================================
# ADD CATEGORY
# ============================================================

@login_required(login_url="admin_login")
def category_add(request):

    # Only admin can access
    if not request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":

        name = request.POST.get("name")
        description = request.POST.get("description")

        # Check duplicate category
        if Category.objects.filter(name__iexact=name).exists():

            messages.error(request, "Category already exists.")

        else:

            # Save category
            Category.objects.create(
                name=name,
                description=description
            )

            messages.success(request, "Category added successfully!")

            return redirect("category_list")

    return render(request, "category_add.html")

@login_required(login_url="admin_login")
def category_edit(request, id):

    # Only admin can access
    if not request.user.is_superuser:
        return redirect("dashboard")

    # Get category by ID
    category = Category.objects.get(id=id)

    if request.method == "POST":

        name = request.POST.get("name")
        description = request.POST.get("description")

        # Check duplicate name except current category
        if Category.objects.filter(name__iexact=name).exclude(id=id).exists():

            messages.error(request, "Category already exists.")

        else:

            # Update category
            category.name = name
            category.description = description
            category.save()

            messages.success(request, "Category updated successfully!")

            return redirect("category_list")

    return render(request, "category_edit.html", {
        "category": category
    })

@login_required(login_url="admin_login")
def category_delete(request, id):

    # Only admin can access
    if not request.user.is_superuser:
        return redirect("dashboard")

    # Get category by ID
    category = Category.objects.get(id=id)

    # Delete category
    category.delete()

    messages.success(request, "Category deleted successfully!")

    return redirect("category_list")

@login_required(login_url="admin_login")
def service_list(request):

    # Only admin can access
    if not request.user.is_superuser:
        return redirect("dashboard")

    # Get all services
    services = Service.objects.all().order_by("-id")

    return render(request, "service_list.html", {
        "services": services
    })


@login_required(login_url="admin_login")
def service_add(request):

    # Only admin can access
    if not request.user.is_superuser:
        return redirect("dashboard")

    # Get categories for dropdown
    categories = Category.objects.all().order_by("name")

    if request.method == "POST":

        category_id = request.POST.get("category")
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        is_active = request.POST.get("is_active") == "on"

        # Get selected category
        category = Category.objects.get(id=category_id)

        # Save service
        Service.objects.create(
            category=category,
            name=name,
            description=description,
            price=price,
            is_active=is_active
        )

        messages.success(request, "Service added successfully!")

        return redirect("service_list")

    return render(request, "service_add.html", {
        "categories": categories
    })


@login_required(login_url="admin_login")
def service_edit(request, id):

    # Only admin can access
    if not request.user.is_superuser:
        return redirect("dashboard")

    # Get selected service
    service = Service.objects.get(id=id)

    # Get categories for dropdown
    categories = Category.objects.all().order_by("name")

    if request.method == "POST":

        category_id = request.POST.get("category")
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        is_active = request.POST.get("is_active") == "on"

        # Get selected category
        category = Category.objects.get(id=category_id)

        # Update service
        service.category = category
        service.name = name
        service.description = description
        service.price = price
        service.is_active = is_active

        service.save()

        messages.success(request, "Service updated successfully!")

        return redirect("service_list")

    return render(request, "service_edit.html", {
        "service": service,
        "categories": categories
    })


@login_required(login_url="admin_login")
def service_delete(request, id):

    # Only admin can access
    if not request.user.is_superuser:
        return redirect("dashboard")

    # Get selected service
    service = Service.objects.get(id=id)

    # Delete service
    service.delete()

    messages.success(request, "Service deleted successfully!")

    return redirect("service_list")

@login_required(login_url="admin_login")
def admin_user_list(request):

    # Only admin can access
    if not request.user.is_superuser:
        return redirect("dashboard")

    # Registered users except admin
    users = User.objects.filter(is_superuser=False).order_by("-id")

    # User counts
    total_users = users.count()
    total_customers = CustomerProfile.objects.count()
    total_providers = ProviderProfile.objects.count()

    return render(request, "admin_user_list.html", {
        "users": users,
        "total_users": total_users,
        "total_customers": total_customers,
        "total_providers": total_providers
    })

@login_required(login_url="admin_login")
def user_status(request, id):

    # Only admin can access
    if not request.user.is_superuser:
        return redirect("dashboard")

    # Get selected user
    account = User.objects.get(id=id)

    # Change status
    if account.is_active:
        account.is_active = False
        messages.success(request, "User deactivated successfully!")
    else:
        account.is_active = True
        messages.success(request, "User activated successfully!")

    account.save()

    return redirect("admin_user_list")
@login_required(login_url="login")
def customer_dashboard(request):

    # Only customers can access
    if not hasattr(request.user, "customerprofile"):
        return redirect("dashboard")

    customer = request.user.customerprofile


    # Total bookings
    total_bookings = Booking.objects.filter(
        customer=customer
    ).count()


    # Pending bookings
    pending_bookings = Booking.objects.filter(
        customer=customer,
        status="pending"
    ).count()


    # Favorites
    favorite_count = Favorite.objects.filter(
        customer=customer
    ).count()


    # Reviews
    review_count = Review.objects.filter(
        customer=customer
    ).count()


    # Unread notifications
    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()


    return render(
        request,
        "customer_dashboard.html",
        {
            "customer": customer,
            "total_bookings": total_bookings,
            "pending_bookings": pending_bookings,
            "favorite_count": favorite_count,
            "review_count": review_count,
            "unread_notifications": unread_notifications
        }
    )
@login_required(login_url="login")
def provider_dashboard(request):

    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile

    # Provider's services
    total_services = Service.objects.filter(provider=provider).count()

    # Provider's booking counts
    pending_bookings = Booking.objects.filter(
        provider=provider,
        status="pending"
    ).count()

    confirmed_bookings = Booking.objects.filter(
        provider=provider,
        status="confirmed"
    ).count()

    completed_jobs = Booking.objects.filter(
        provider=provider,
        status="completed"
    ).count()

    return render(request, "provider_dashboard.html", {
        "provider": provider,
        "total_services": total_services,
        "pending_bookings": pending_bookings,
        "confirmed_bookings": confirmed_bookings,
        "completed_jobs": completed_jobs
    })


@login_required(login_url="login")
def customer_profile(request):

    # Only customer can access
    if not hasattr(request.user, "customerprofile"):
        return redirect("dashboard")

    customer = request.user.customerprofile

    # Update profile
    if request.method == "POST":

        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        # Update User data
        request.user.email = email
        request.user.save()

        # Update CustomerProfile data
        customer.phone = phone
        customer.address = address
        customer.save()

        messages.success(
            request,
            "Profile updated successfully!"
        )

        return redirect("customer_profile")

    return render(request, "customer_profile.html", {
        "customer": customer
    })




# ============================================================
# PROVIDER PROFILE
# ============================================================

@login_required(login_url="login")
def provider_profile(request):

    # Only provider can access
    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile

    # Update provider profile
    if request.method == "POST":

        email = request.POST.get("email")
        business_name = request.POST.get("business_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        experience = request.POST.get("experience")

        # Update User data
        request.user.email = email
        request.user.save()

        # Update ProviderProfile data
        provider.business_name = business_name
        provider.phone = phone
        provider.address = address
        provider.experience = experience
        provider.save()

        messages.success(
            request,
            "Provider profile updated successfully!"
        )

        return redirect("provider_profile")

    return render(request, "provider_profile.html", {
        "provider": provider
    })


# ============================================================
# PROVIDER SERVICE LIST
# ============================================================

@login_required(login_url="login")
def provider_service_list(request):

    # Only provider can access
    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile

    # Get only this provider's services
    services = Service.objects.filter(
        provider=provider
    ).order_by("-id")

    return render(request, "provider_service_list.html", {
        "services": services
    })


# ============================================================
# PROVIDER ADD SERVICE
# ============================================================

@login_required(login_url="login")
def provider_service_add(request):

    # Only provider can access
    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile
    categories = Category.objects.all().order_by("name")

    if request.method == "POST":

        category_id = request.POST.get("category")
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")

        category = Category.objects.get(id=category_id)

        # Create service for logged-in provider
        Service.objects.create(
            provider=provider,
            category=category,
            name=name,
            description=description,
            price=price,
            is_active=True
        )

        messages.success(
            request,
            "Service added successfully!"
        )

        return redirect("provider_service_list")

    return render(request, "provider_service_add.html", {
        "categories": categories
    })


# ============================================================
# PROVIDER EDIT SERVICE
# ============================================================

@login_required(login_url="login")
def provider_service_edit(request, id):

    # Only provider can access
    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile

    # Provider can access only own service
    try:
        service = Service.objects.get(
            id=id,
            provider=provider
        )

    except Service.DoesNotExist:

        messages.error(
            request,
            "Service not found or access denied."
        )

        return redirect("provider_service_list")

    categories = Category.objects.all().order_by("name")

    if request.method == "POST":

        category_id = request.POST.get("category")
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        is_active = request.POST.get("is_active") == "on"

        category = Category.objects.get(id=category_id)

        service.category = category
        service.name = name
        service.description = description
        service.price = price
        service.is_active = is_active

        service.save()

        messages.success(
            request,
            "Service updated successfully!"
        )

        return redirect("provider_service_list")

    return render(request, "provider_service_edit.html", {
        "service": service,
        "categories": categories
    })


# ============================================================
# PROVIDER DELETE SERVICE
# ============================================================

@login_required(login_url="login")
def provider_service_delete(request, id):

    # Only provider can access
    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile

    # Provider can delete only own service
    try:
        service = Service.objects.get(
            id=id,
            provider=provider
        )

    except Service.DoesNotExist:

        messages.error(
            request,
            "Service not found or access denied."
        )

        return redirect("provider_service_list")

    service.delete()

    messages.success(
        request,
        "Service deleted successfully!"
    )

    return redirect("provider_service_list")




# ============================================================
# PUBLIC SERVICE DETAIL
# ============================================================


# ============================================================
# PUBLIC SERVICE LIST + SEARCH + FILTER
# ============================================================

def public_service_list(request):

    # Get search and category values
    search = request.GET.get("search", "")
    category_id = request.GET.get("category", "")

    # Only active provider services
    services = Service.objects.filter(
        is_active=True,
        provider__isnull=False
    ).order_by("-id")

    # Search by service name, description or provider
    if search:
        services = services.filter(
            models.Q(name__icontains=search) |
            models.Q(description__icontains=search) |
            models.Q(provider__business_name__icontains=search) |
            models.Q(provider__user__username__icontains=search)
        )

    # Filter by category
    if category_id:
        services = services.filter(category_id=category_id)

    categories = Category.objects.all().order_by("name")

    return render(request, "public_service_list.html", {
        "services": services,
        "categories": categories,
        "search": search,
        "selected_category": category_id
    })


# ============================================================
# BOOK SERVICE
# ============================================================
from datetime import date
@login_required(login_url="login")
def book_service(request, id):

    # Only customers can book services
    if not hasattr(request.user, "customerprofile"):

        messages.error(
            request,
            "Only customers can book services."
        )

        return redirect(
            "public_service_detail",
            id=id
        )


    customer = request.user.customerprofile


    # Get selected service
    try:

        service = Service.objects.get(
            id=id,
            is_active=True,
            provider__isnull=False
        )

    except Service.DoesNotExist:

        messages.error(
            request,
            "Service not found."
        )

        return redirect("public_service_list")


    # Booking form submitted
    if request.method == "POST":

        booking_date = request.POST.get("booking_date")
        booking_time = request.POST.get("booking_time")
        message = request.POST.get("message", "").strip()


        # ================= VALIDATION =================

        if not booking_date or not booking_time:

            messages.error(
                request,
                "Please select booking date and time."
            )


        elif booking_date < str(date.today()):

            messages.error(
                request,
                "Booking date cannot be in the past."
            )


        else:

            # ================= CREATE BOOKING =================

            booking = Booking.objects.create(

                customer=customer,

                service=service,

                provider=service.provider,

                booking_date=booking_date,

                booking_time=booking_time,

                message=message,

                status="pending"
            )


            # ================= CREATE NOTIFICATION =================
            # Notify provider about new booking request

            Notification.objects.create(

                user=service.provider.user,

                notification_type="booking",

                title="New Booking Request",

                message=(
                    f"{request.user.username} requested "
                    f"your service: {service.name}."
                ),

                booking=booking
            )


            # Success message
            messages.success(
                request,
                "Booking request sent successfully! "
                "Waiting for provider confirmation."
            )


            return redirect(
                "customer_booking_list"
            )


    # ================= BOOKING PAGE =================

    return render(
        request,
        "booking.html",
        {
            "service": service,
            "today": date.today()
        }
    )


@login_required(login_url="login")
def customer_booking_list(request):

    # Only customer can access
    if not hasattr(request.user, "customerprofile"):
        return redirect("dashboard")

    customer = request.user.customerprofile

    # Get bookings of logged-in customer
    bookings = Booking.objects.filter(
        customer=customer
    ).order_by("-id")

    return render(request, "customer_booking_list.html", {
        "bookings": bookings
    })

# ============================================================
# PROVIDER BOOKING REQUESTS
# ============================================================

@login_required(login_url="login")
def provider_booking_list(request):

    # Only provider can access
    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile

    # Get only this provider's bookings
    bookings = Booking.objects.filter(
        provider=provider
    ).order_by("-id")

    return render(request, "provider_booking_list.html", {
        "bookings": bookings
    })


@login_required(login_url="login")
def provider_booking_confirm(request, id):

    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile

    try:
        booking = Booking.objects.get(
            id=id,
            provider=provider
        )

    except Booking.DoesNotExist:
        messages.error(request, "Booking not found or access denied.")
        return redirect("provider_booking_list")

    if booking.status == "pending":
        booking.status = "confirmed"
        booking.save()

        messages.success(
            request,
            "Booking confirmed successfully!"
        )

    return redirect("provider_booking_list")


@login_required(login_url="login")
def provider_booking_cancel(request, id):

    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile

    try:
        booking = Booking.objects.get(
            id=id,
            provider=provider
        )

    except Booking.DoesNotExist:
        messages.error(request, "Booking not found or access denied.")
        return redirect("provider_booking_list")

    if booking.status in ["pending", "confirmed"]:
        booking.status = "cancelled"
        booking.save()

        messages.success(
            request,
            "Booking cancelled successfully!"
        )

    return redirect("provider_booking_list")

# ============================================================
# MARK BOOKING AS COMPLETED
# ============================================================

@login_required(login_url="login")
def provider_booking_complete(request, id):

    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile

    try:
        booking = Booking.objects.get(
            id=id,
            provider=provider
        )

    except Booking.DoesNotExist:
        messages.error(request, "Booking not found or access denied.")
        return redirect("provider_booking_list")

    # Only confirmed booking can be completed
    if booking.status == "confirmed":

        booking.status = "completed"
        booking.save()

        messages.success(
            request,
            "Booking marked as completed successfully!"
        )

    else:
        messages.error(
            request,
            "Only confirmed bookings can be completed."
        )

    return redirect("provider_booking_list")    

# ============================================================
# PROVIDER COMPLETED JOBS
# ============================================================

@login_required(login_url="login")
def provider_completed_jobs(request):

    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile

    completed_jobs = Booking.objects.filter(
        provider=provider,
        status="completed"
    ).order_by("-id")

    return render(request, "provider_completed_jobs.html", {
        "completed_jobs": completed_jobs
    })




# ============================================================
# PUBLIC SERVICE DETAIL
# ============================================================

def public_service_detail(request, id):

    try:
        service = Service.objects.get(
            id=id,
            is_active=True,
            provider__isnull=False
        )

    except Service.DoesNotExist:

        messages.error(
            request,
            "Service not found."
        )

        return redirect("public_service_list")


    # Service Reviews
    reviews = Review.objects.filter(
        service=service
    ).select_related(
        "customer__user"
    ).order_by("-created_at")


    # Review Statistics
    total_reviews = reviews.count()

    average_rating = reviews.aggregate(
        avg=Avg("rating")
    )["avg"]


    # Check Favorite Status
    is_favorite = False

    if request.user.is_authenticated:

        if hasattr(request.user, "customerprofile"):

            is_favorite = Favorite.objects.filter(
                customer=request.user.customerprofile,
                service=service
            ).exists()


    return render(
        request,
        "service_detail.html",
        {
            "service": service,
            "reviews": reviews,
            "total_reviews": total_reviews,
            "average_rating": average_rating,
            "is_favorite": is_favorite
        }
    )

# ============================================================
# CUSTOMER - MY REVIEWS
# ============================================================






@login_required(login_url="login")
def add_review(request, booking_id):

    # Only customer
    if not hasattr(request.user, "customerprofile"):
        messages.error(request, "Only customers can submit reviews.")
        return redirect("dashboard")

    customer = request.user.customerprofile

    # Get customer's completed booking
    try:
        booking = Booking.objects.get(
            id=booking_id,
            customer=customer,
            status="completed"
        )

    except Booking.DoesNotExist:
        messages.error(
            request,
            "You can review only your completed bookings."
        )
        return redirect("customer_booking_list")

    # Prevent duplicate review
    if Review.objects.filter(booking=booking).exists():
        messages.warning(
            request,
            "You have already reviewed this booking."
        )
        return redirect("customer_booking_list")

    if request.method == "POST":

        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "").strip()

        # Rating validation
        if rating not in ["1", "2", "3", "4", "5"]:
            messages.error(
                request,
                "Please select a valid rating."
            )

        # Comment validation
        elif not comment:
            messages.error(
                request,
                "Please write your review."
            )

        else:

            # Save review
            Review.objects.create(
                booking=booking,
                customer=customer,
                service=booking.service,
                provider=booking.provider,
                rating=int(rating),
                comment=comment
            )

            messages.success(
                request,
                "Review submitted successfully!"
            )

            return redirect("customer_booking_list")

    return render(request, "review_add.html", {
        "booking": booking
    })


@login_required(login_url="login")
def customer_reviews(request):

    if not hasattr(request.user, "customerprofile"):
        return redirect("dashboard")

    customer = request.user.customerprofile

    reviews = Review.objects.filter(
        customer=customer
    ).select_related(
        "service",
        "provider",
        "booking"
    ).order_by("-created_at")

    return render(request, "customer_reviews.html", {
        "reviews": reviews
    })


# ============================================================
# PROVIDER - RECEIVED REVIEWS
# ============================================================

@login_required(login_url="login")
def provider_reviews(request):

    if not hasattr(request.user, "providerprofile"):
        return redirect("dashboard")

    provider = request.user.providerprofile

    # Reviews belonging to logged-in provider
    reviews = Review.objects.filter(
        provider=provider
    ).select_related(
        "customer__user",
        "service",
        "booking"
    ).order_by("-created_at")

    # Total reviews
    total_reviews = reviews.count()

    # Average rating
    average_rating = reviews.aggregate(
        avg=Avg("rating")
    )["avg"]

    # Rating counts
    five_star = reviews.filter(rating=5).count()
    four_star = reviews.filter(rating=4).count()
    three_star = reviews.filter(rating=3).count()
    two_star = reviews.filter(rating=2).count()
    one_star = reviews.filter(rating=1).count()

    return render(request, "provider_reviews.html", {
        "reviews": reviews,
        "total_reviews": total_reviews,
        "average_rating": average_rating,
        "five_star": five_star,
        "four_star": four_star,
        "three_star": three_star,
        "two_star": two_star,
        "one_star": one_star
    })


# ============================================================
# CUSTOMER - ADD FAVORITE
# ============================================================

@login_required(login_url="login")
def add_favorite(request, service_id):

    # Only customers can use favorites
    if not hasattr(request.user, "customerprofile"):
        messages.error(
            request,
            "Only customers can add services to favorites."
        )
        return redirect("dashboard")

    customer = request.user.customerprofile

    try:
        service = Service.objects.get(
            id=service_id,
            is_active=True
        )

    except Service.DoesNotExist:
        messages.error(
            request,
            "Service not found."
        )
        return redirect("public_service_list")

    # Add only if not already saved
    favorite, created = Favorite.objects.get_or_create(
        customer=customer,
        service=service
    )

    if created:

        messages.success(
            request,
            "Service added to favorites!"
        )

    else:

        messages.info(
            request,
            "Service is already in your favorites."
        )

    return redirect(
        "public_service_detail",
        id=service.id
    )


# ============================================================
# CUSTOMER - REMOVE FAVORITE
# ============================================================

@login_required(login_url="login")
def remove_favorite(request, service_id):

    if not hasattr(request.user, "customerprofile"):
        return redirect("dashboard")

    customer = request.user.customerprofile

    favorite = Favorite.objects.filter(
        customer=customer,
        service_id=service_id
    ).first()

    if favorite:

        favorite.delete()

        messages.success(
            request,
            "Service removed from favorites."
        )

    return redirect("customer_favorites")

# ============================================================
# CUSTOMER - MY FAVORITES
# ============================================================

@login_required(login_url="login")
def customer_favorites(request):

    if not hasattr(request.user, "customerprofile"):
        return redirect("dashboard")

    customer = request.user.customerprofile

    favorites = Favorite.objects.filter(
        customer=customer
    ).select_related(
        "service",
        "service__category",
        "service__provider"
    ).order_by("-created_at")

    return render(
        request,
        "customer_favorites.html",
        {
            "favorites": favorites
        }
    )


# ============================================================
# USER NOTIFICATIONS
# ============================================================

@login_required(login_url="login")
def notifications_list(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).select_related(
        "booking",
        "booking__service"
    ).order_by("-created_at")

    unread_count = notifications.filter(
        is_read=False
    ).count()

    return render(
        request,
        "notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_count
        }
    )

@login_required(login_url="login")
def notification_read(request, id):

    try:

        notification = Notification.objects.get(
            id=id,
            user=request.user
        )

    except Notification.DoesNotExist:

        messages.error(
            request,
            "Notification not found."
        )

        return redirect("notifications_list")


    notification.is_read = True
    notification.save()


    return redirect("notifications_list")

@login_required(login_url="login")
def notifications_mark_all_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(
        is_read=True
    )

    messages.success(
        request,
        "All notifications marked as read."
    )

    return redirect("notifications_list")

@login_required(login_url="login")
def notification_delete(request, id):

    try:

        notification = Notification.objects.get(
            id=id,
            user=request.user
        )

    except Notification.DoesNotExist:

        messages.error(
            request,
            "Notification not found."
        )

        return redirect("notifications_list")


    notification.delete()

    messages.success(
        request,
        "Notification deleted."
    )

    return redirect("notifications_list")

def contact(request):

    # If user is logged in, pre-fill basic details
    initial_name = ""
    initial_email = ""

    if request.user.is_authenticated:
        initial_name = request.user.username
        initial_email = request.user.email


    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()


        # Validation
        if not name:
            messages.error(
                request,
                "Please enter your name."
            )

        elif not email:
            messages.error(
                request,
                "Please enter your email."
            )

        elif not subject:
            messages.error(
                request,
                "Please enter enquiry subject."
            )

        elif not message:
            messages.error(
                request,
                "Please enter your message."
            )

        else:

            # Save enquiry
            ContactEnquiry.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message,
                status="pending"
            )

            messages.success(
                request,
                "Your enquiry has been submitted successfully!"
            )

            return redirect("contact")


    return render(
        request,
        "contact.html",
        {
            "initial_name": initial_name,
            "initial_email": initial_email
        }
    )


# ============================================================
# ADMIN - CONTACT ENQUIRIES
# ============================================================
from django.shortcuts import render, redirect, get_object_or_404

# View all enquiries
@login_required(login_url="admin_login")
def admin_enquiry_list(request):

    # Only admin/staff can access
    if not request.user.is_staff:
        return redirect("home")

    enquiries = ContactEnquiry.objects.all().order_by("-created_at")

    pending_count = ContactEnquiry.objects.filter(
        status="pending"
    ).count()

    resolved_count = ContactEnquiry.objects.filter(
        status="resolved"
    ).count()

    return render(
        request,
        "admin_enquiry_list.html",
        {
            "enquiries": enquiries,
            "pending_count": pending_count,
            "resolved_count": resolved_count,
        }
    )


# View single enquiry
@login_required(login_url="admin_login")
def admin_enquiry_detail(request, id):

    if not request.user.is_staff:
        return redirect("home")

    enquiry = get_object_or_404(
        ContactEnquiry,
        id=id
    )

    return render(
        request,
        "admin_enquiry_detail.html",
        {
            "enquiry": enquiry
        }
    )


# Mark enquiry resolved
@login_required(login_url="admin_login")
def admin_enquiry_resolve(request, id):

    if not request.user.is_staff:
        return redirect("home")

    enquiry = get_object_or_404(
        ContactEnquiry,
        id=id
    )

    enquiry.status = "resolved"
    enquiry.save()

    messages.success(
        request,
        "Enquiry marked as resolved successfully."
    )

    return redirect("admin_enquiry_list")


# Delete enquiry
@login_required(login_url="admin_login")
def admin_enquiry_delete(request, id):

    if not request.user.is_staff:
        return redirect("home")

    enquiry = get_object_or_404(
        ContactEnquiry,
        id=id
    )

    enquiry.delete()

    messages.success(
        request,
        "Enquiry deleted successfully."
    )

    return redirect("admin_enquiry_list")


@login_required(login_url="admin_login")
def admin_enquiry_list(request):

    if not request.user.is_staff:
        return redirect("home")

    # Get all enquiries
    enquiries = ContactEnquiry.objects.all().order_by(
        "-created_at"
    )

    # Count pending enquiries
    pending_count = ContactEnquiry.objects.filter(
        status="pending"
    ).count()

    # Count resolved enquiries
    resolved_count = ContactEnquiry.objects.filter(
        status="resolved"
    ).count()

    return render(
        request,
        "admin_enquiry_list.html",
        {
            "enquiries": enquiries,
            "pending_count": pending_count,
            "resolved_count": resolved_count,
        }
    )

@login_required(login_url="admin_login")
def admin_enquiry_detail(request, id):

    if not request.user.is_staff:
        return redirect("home")

    enquiry = get_object_or_404(
        ContactEnquiry,
        id=id
    )

    return render(
        request,
        "admin_enquiry_detail.html",
        {
            "enquiry": enquiry
        }
    )


@login_required(login_url="admin_login")
def admin_enquiry_resolve(request, id):

    if not request.user.is_staff:
        return redirect("home")

    enquiry = get_object_or_404(
        ContactEnquiry,
        id=id
    )

    enquiry.status = "resolved"

    enquiry.save()

    messages.success(
        request,
        "Enquiry marked as resolved successfully."
    )

    return redirect("admin_enquiry_list")


@login_required(login_url="admin_login")
def admin_enquiry_delete(request, id):

    if not request.user.is_staff:
        return redirect("home")

    enquiry = get_object_or_404(
        ContactEnquiry,
        id=id
    )

    enquiry.delete()

    messages.success(
        request,
        "Enquiry deleted successfully."
    )

    return redirect("admin_enquiry_list")