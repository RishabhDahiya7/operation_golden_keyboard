from django.db import models
from django.contrib.auth.models import User


class Hostel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    handle = models.CharField(max_length=50, unique=True)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='participants')

    def __str__(self):
        return self.handle


class Mission(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('boss_level', 'Boss Level'),
    ]
    STATUS_CHOICES = [
        ('unclaimed', 'Unclaimed'),
        ('in_progress', 'In Progress'),
        ('cracked', 'Cracked'),
        ('expired', 'Expired'),
    ]

    codename = models.CharField(max_length=100)
    brief = models.TextField()
    points = models.PositiveIntegerField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unclaimed')
    deadline = models.DateTimeField()

    claimed_by = models.ForeignKey(
        Participant, on_delete=models.SET_NULL, null=True, blank=True, related_name='missions'
    )
    hostel = models.ForeignKey(
        Hostel, on_delete=models.SET_NULL, null=True, blank=True, related_name='missions'
    )

    def __str__(self):
        return self.codename