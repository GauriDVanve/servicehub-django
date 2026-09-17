# Import Django models
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):

    # Category name
    name = models.CharField(max_length=100, unique=True)

    # Category description
    description = models.TextField(blank=True)

    # Display category name
    def __str__(self):
        return self.name



class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


# Provider Profile
class ProviderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    business_name = models.CharField(max_length=150, blank=True)
    experience = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username


class Service(models.Model):

    # Service Provider
    provider = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Service Category
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    # Service Name
    name = models.CharField(max_length=150)

    # Service Description
    description = models.TextField()

    # Service Price
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Service Status
    is_active = models.BooleanField(default=True)

    # Created Date
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ============================================================
# BOOKING MODEL
# ============================================================

class Booking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )

    provider = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE
    )

    booking_date = models.DateField()
    booking_time = models.TimeField()

    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username} - {self.service.name}"


# ============================================================
# REVIEW MODEL
# ============================================================

class Review(models.Model):

    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    # One booking can have only one review
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE
    )

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )

    provider = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.customer.user.username} - {self.service.name} - {self.rating} Star"


# ============================================================
# FAVORITE MODEL
# ============================================================

class Favorite(models.Model):

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="favorites"
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Same service cannot be added twice
        unique_together = ("customer", "service")

    def __str__(self):
        return f"{self.customer.user.username} - {self.service.name}"

# ============================================================
# NOTIFICATION MODEL
# ============================================================

class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ("booking", "Booking"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
        ("review", "Review"),
        ("general", "General"),
    ]

    # Notification receiver
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default="general"
    )

    title = models.CharField(
        max_length=150
    )

    message = models.TextField()

    # Optional booking reference
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ContactEnquiry(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("resolved", "Resolved"),
    ]

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    subject = models.CharField(
        max_length=200
    )

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} - {self.subject}"