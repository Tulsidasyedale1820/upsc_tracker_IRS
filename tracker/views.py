from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Exam, Subject, Topic, SubTopic
import json

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('study_arena')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('select_exam')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('study_arena')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('study_arena')
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def select_or_create_exam(request):
    if request.method == 'POST':
        exam_name = request.POST.get('exam_name', '').strip()
        if exam_name:
            exam = Exam.objects.create(user=request.user, name=exam_name)
            # Standard Predefined Core Subjects Setup
            defaults = ["History & Art Culture", "Geography", "Indian Polity", "Economy", "Environment & Science"]
            for sub in defaults:
                Subject.objects.create(exam=exam, name=sub, weightage_marks=100)
            request.session['active_exam_id'] = exam.id
            return redirect('study_arena')
    return render(request, 'tracker/exam_select.html')

@login_required
def study_arena_view(request):
    active_exam_id = request.session.get('active_exam_id')
    exam = Exam.objects.filter(user=request.user).order_by('-created_at').first()
    if not exam:
        return redirect('select_exam')
    request.session['active_exam_id'] = exam.id
    return render(request, 'tracker/study_arena.html', {'exam': exam, 'subjects': exam.subjects.all()})

@login_required
def subject_detail_view(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id, exam__user=request.user)
        return render(request, 'tracker/subject_detail.html', {'subject': subject})
    except Subject.DoesNotExist:
        return redirect('study_arena')

# --- API BINDINGS FOR BACKEND FETCH ACTIONS ---
@login_required
def get_subject_matrix_details(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id, exam__user=request.user)
        topics_data = []
        for t in subject.topics.all().order_by('id'):
            sub_list = [{'id': s.id, 'name': s.name, 'is_completed': s.is_completed, 'notes': s.notes} for s in t.subtopics.all()]
            topics_data.append({
                'id': t.id, 'name': t.name, 'weightage': t.weightage_marks, 'pct': t.completion_percentage,
                'earned': t.earned_marks, 'subtopics': sub_list, 'time': t.time_spent_mins
            })
        return JsonResponse({'status': 'success', 'pct': subject.completion_percentage, 'earned': subject.earned_marks, 'topics': topics_data})
    except Subject.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

@login_required
def save_configuration_matrix(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subject = Subject.objects.get(id=data.get('subject_id'), exam__user=request.user)
        subject.weightage_marks = int(data.get('weightage', 100))
        subject.target_minutes = int(data.get('target_hours', 100)) * 60
        subject.save()
        return JsonResponse({'status': 'success'})

@login_required
def append_topic_node(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subject = Subject.objects.get(id=data.get('subject_id'), exam__user=request.user)
        Topic.objects.create(subject=subject, name=data.get('name'), weightage_marks=int(data.get('weightage', 20)))
        return JsonResponse({'status': 'success'})

@login_required
def append_subtopic_node(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        topic = Topic.objects.get(id=data.get('topic_id'), subject__exam__user=request.user)
        SubTopic.objects.create(topic=topic, name=data.get('name'), notes=data.get('notes', ''))
        return JsonResponse({'status': 'success'})

@login_required
def toggle_subtopic_node(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subtopic = SubTopic.objects.get(id=data.get('subtopic_id'), topic__subject__exam__user=request.user)
        subtopic.is_completed = not subtopic.is_completed
        subtopic.save()
        return JsonResponse({'status': 'success'})

@login_required
def commit_timer_minutes(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        topic = Topic.objects.get(id=data.get('topic_id'), subject__exam__user=request.user)
        topic.time_spent_mins += int(data.get('minutes', 15))
        topic.save()
        return JsonResponse({'status': 'success'})