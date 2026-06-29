from django.db import models
from django.contrib.auth.models import User

class Exam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Subject(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100)
    weightage_marks = models.IntegerField(default=100)
    
    @property
    def completion_percentage(self):
        total_topics = self.topics.count()
        if total_topics == 0:
            return 0
        completed_topics = self.topics.filter(is_completed=True).count()
        return int((completed_topics / total_topics) * 100)
        
    @property
    def current_earned_score(self):
        return round((self.completion_percentage / 100) * self.weightage_marks, 1)

    def __str__(self):
        return f"{self.name} - {self.exam.name}"

class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=200)
    weightage_marks = models.IntegerField(default=10)
    is_completed = models.BooleanField(default=False)
    time_spent_seconds = models.IntegerField(default=0)

    def __str__(self):
        return self.name