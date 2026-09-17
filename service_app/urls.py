# ============================================================
# SERVICE APP - URL CONFIGURATION
# ============================================================
#
# This file will contain the URLs related to our
# ServiceHub application.
#
# Example:
#
# /              → Home
# /register/     → Registration
# /login/        → Login
# /services/     → Services
# /booking/      → Booking
#
# We will add these URLs one by one as our project develops.
# ============================================================


# ------------------------------------------------------------
# IMPORT path
# ------------------------------------------------------------
#
# path() is provided by Django.
#
# It is used to create URL patterns.
#
# Example:
#
# path("login/", views.login_view)
#
# ------------------------------------------------------------

from django.urls import path


# ------------------------------------------------------------
# IMPORT VIEWS
# ------------------------------------------------------------
#
# The dot (.) means:
#
# Import views.py from the CURRENT application.
#
# Our current application is:
#
# service_app
#
# ------------------------------------------------------------

from . import views



# ============================================================
# URL PATTERNS
# ============================================================
#
# urlpatterns is a special list used by Django.
#
# Django checks this list when a user enters a URL.
# ============================================================

urlpatterns = [


    # --------------------------------------------------------
    # HOME PAGE URL
    # --------------------------------------------------------
    #
    # "" means the root/home URL.
    #
    # Therefore:
    #
    # http://127.0.0.1:8000/
    #
    # will call:
    #
    # views.home
    #
    # name="home"
    #
    # gives this URL a name.
    #
    # Later we can use:
    #
    # {% url 'home' %}
    #
    # inside our HTML pages.
    # --------------------------------------------------------

    path("",views.home, name="home"),
    path("register/", views.register_view,name="register"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard,name="dashboard"),
    path("contact/",views.contact,name="contact"),
    # Logout
    path("logout/",views.logout_view,name="logout"),

    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-categories/", views.category_list, name="category_list"),
    path("admin-category/add/", views.category_add, name="category_add"),
    path("admin-category/edit/<int:id>/", views.category_edit, name="category_edit"),
    path("admin-category/delete/<int:id>/", views.category_delete, name="category_delete"),

    # Service URLs
    path("admin-services/", views.service_list, name="service_list"),
    path("admin-service/add/", views.service_add, name="service_add"),
    path("admin-service/edit/<int:id>/", views.service_edit, name="service_edit"),
    path("admin-service/delete/<int:id>/", views.service_delete, name="service_delete"),

    path("admin-users/", views.admin_user_list, name="admin_user_list"),
    path("admin-user/status/<int:id>/", views.user_status, name="user_status"),

    path("customer-dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("customer-profile/", views.customer_profile, name="customer_profile"),
    # Provider URL
    path("provider-dashboard/", views.provider_dashboard, name="provider_dashboard"),
    path("provider-profile/", views.provider_profile, name="provider_profile"),
    # Provider Service URLs
    path("provider-services/", views.provider_service_list, name="provider_service_list"),
    path("provider-service/add/", views.provider_service_add, name="provider_service_add"),
    path("provider-service/edit/<int:id>/", views.provider_service_edit, name="provider_service_edit"),
    path("provider-service/delete/<int:id>/", views.provider_service_delete, name="provider_service_delete"),

    # Public Service URLs
    path("services/", views.public_service_list, name="public_service_list"),
    path("service/<int:id>/", views.public_service_detail, name="public_service_detail"),

    # Booking
    path("service/<int:id>/book/", views.book_service, name="book_service"),
    path("my-bookings/", views.customer_booking_list, name="customer_booking_list"),

    # Provider Booking
    path("provider-bookings/", views.provider_booking_list, name="provider_booking_list"),
    path("provider-booking/confirm/<int:id>/", views.provider_booking_confirm, name="provider_booking_confirm"),
    path("provider-booking/cancel/<int:id>/", views.provider_booking_cancel, name="provider_booking_cancel"),
    path("provider-booking/complete/<int:id>/", views.provider_booking_complete, name="provider_booking_complete"),

    path("provider-completed-jobs/", views.provider_completed_jobs, name="provider_completed_jobs"),
    # Reviews
    path("review/add/<int:booking_id>/", views.add_review, name="add_review"),
    path("my-reviews/", views.customer_reviews, name="customer_reviews"),
    path("provider-reviews/", views.provider_reviews, name="provider_reviews"),


    path("favorite/add/<int:service_id>/",views.add_favorite,name="add_favorite"),
    path("favorite/remove/<int:service_id>/",views.remove_favorite, name="remove_favorite"),
    path("my-favorites/", views.customer_favorites,name="customer_favorites"),

    # ============================================================
# NOTIFICATIONS
# ============================================================
    path("notifications/",views.notifications_list, name="notifications_list"),
    path("notification/read/<int:id>/",views.notification_read,name="notification_read"),
    path("notifications/read-all/",views.notifications_mark_all_read,name="notifications_mark_all_read"),
    path("notification/delete/<int:id>/",views.notification_delete,name="notification_delete"),


    

    # ============================================================
# ADMIN CONTACT ENQUIRIES
# ============================================================

    path("admin-enquiries/", views.admin_enquiry_list,name="admin_enquiry_list"),
    path("admin-enquiry/<int:id>/", views.admin_enquiry_detail,name="admin_enquiry_detail"),

    path("admin-enquiry/resolve/<int:id>/",views.admin_enquiry_resolve,name="admin_enquiry_resolve"),

    path("admin-enquiry/delete/<int:id>/", views.admin_enquiry_delete, name="admin_enquiry_delete"),

    

]