from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('club', 'Club'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='club')

    def is_club(self):
        return self.role == 'club'

    def is_admin(self):
        return self.role == 'admin'


class Club(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    contact_email = models.EmailField()

    def __str__(self):
        return self.name


from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    venue = models.CharField(max_length=200, default='Campus Auditorium')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_seats = models.PositiveIntegerField()
    guest = models.CharField(max_length=255, blank=True, help_text="Name of the guest speaker or chief guest (optional)")
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} by {self.club.name}"

from django.core.validators import MinValueValidator, MaxValueValidator

class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedbacks')
    comment = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    def __str__(self):
        return f"Feedback on {self.event.title} at {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"


from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
