# models.py

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    is_active = models.BooleanField(default=True)
    activation_token = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.is_active}"

class Tour(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    average_rating = models.DecimalField(max_digits=5, decimal_places=2)
    location = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('tour-detail', args=[str(self.id)])

    def __str__(self):
        return self.name

    def calculate_stars(self):
        avg_rating = self.average_rating
        if avg_rating >= 4.5:
            return "★★★★★"
        elif avg_rating >= 3.5:
            return "★★★★☆"
        elif avg_rating >= 2.5:
            return "★★★☆☆"
        elif avg_rating >= 1.5:
            return "★★☆☆☆"
        else:
            return "★☆☆☆☆"
#######################    
    def has_pending_booking(self):
        return self.booking_set.filter(status='Pending').exists()

    def has_future_bookings(self):
        return self.booking_set.filter(status='Confirmed', departure_date__gte=timezone.now()).exists()

    def delete(self, *args, **kwargs):
        if self.has_pending_booking() or self.has_future_bookings():
            raise ValueError("Không thể xóa Tour khi có đơn đặt đang chờ xử lý hoặc được xác nhận trong tương lai.")
        super().delete(*args, **kwargs)
        

class Image(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tour_images/')

    def __str__(self):
        return f"Image {self.id} for Tour {self.tour.name}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_people = models.CharField(max_length=255)
    departure_date = models.DateTimeField()
    end_date = models.DateField(null=True, blank=True, default=None)
    is_approved = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)  # Trường mới thêm vào để đánh dấu đã hủy tour


    def __str__(self):
        return f"{self.user.username} - {self.tour.name} - {self.status}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
############
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
##########
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
###################
    def get_star_rating(self):
        return "★" * self.rating
#####################
    def __str__(self):
        return f"{self.user.username} - {self.tour.name} - {self.rating}"
