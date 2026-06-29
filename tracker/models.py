from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class SubjectBlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    # New field: Total time allowed allocated directly to the main subject
    allocated_subject_hours = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class TopicTarget(models.Model):
    subject_block = models.ForeignKey(SubjectBlock, on_delete=models.CASCADE, related_name="targets")
    topic_name = models.CharField(max_length=255)
    allocated_hours = models.FloatField(default=0.0)
    completion_percentage = models.IntegerField(default=0)
    user_comments = models.TextField(blank=True, default="")

    @property
    def spent_hours(self):
        return round((self.allocated_hours * self.completion_percentage) / 100, 2)

    @property
    def remaining_hours(self):
        return round(self.allocated_hours - self.spent_hours, 2)

    def __str__(self):
        return self.topic_name