from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=200)
    date_posted = models.DateTimeField(default=timezone.now)
    deadline = models.DateField()
    id_number = models.CharField(max_length=4)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    lead_assigned=models.CharField(max_length=20)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
COLOR_CHOICES = (
    ('green','GREEN'),
    ('blue', 'BLUE'),
    ('red','RED'),
    ('orange','ORANGE'),
    ('black','BLACK'),
)

# class lead(models.Model):
#     project = models.CharField(max_length=6, choices=, default='green')
