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
    target_minutes = models.IntegerField(default=6000)

    @property
    def completion_percentage(self):
        topics = self.topics.all()
        if not topics.exists():
            return 0
        total_pct = sum(t.completion_percentage for t in topics)
        return int(total_pct / topics.count())

    @property
    def earned_marks(self):
        return round((self.completion_percentage / 100.0) * self.weightage_marks, 1)

    def __str__(self):
        return self.name

class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=200)
    weightage_marks = models.IntegerField(default=20)
    time_spent_mins = models.IntegerField(default=0)

    @property
    def completion_percentage(self):
        subtopics = self.subtopics.all()
        if not subtopics.exists():
            return 0
        total_sub = subtopics.count()
        completed = subtopics.filter(is_completed=True).count()
        return int((completed / total_sub) * 100)

    @property
    def earned_marks(self):
        return round((self.completion_percentage / 100.0) * self.weightage_marks, 1)

    def __str__(self):
        return self.name

class SubTopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subtopics')
    name = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name