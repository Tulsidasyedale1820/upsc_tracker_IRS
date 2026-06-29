from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Exam, Subject, Topic
import json

PREDEFINED_SYLLABUS = {
    'UPSC': [
        'History of India & Art Culture',
        'Geography (Indian & World)',
        'Indian Polity & Governance',
        'Economic & Social Development',
        'Environment, Ecology & Climate Change',
        'General Science',
        'International Relations'
    ],
    'MPSC': [
        'History of India & Maharashtra',
        'Geography of Maharashtra & World',
        'Indian Polity & Maharashtra Governance',
        'Economy of Maharashtra & India',
        'Environment & General Science',
        'Maharashtra Local Self-Government'
    ]
}

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
        exam_name = request.POST.get('exam_name').strip()
        custom_name = request.POST.get('custom_exam_name', '').strip()
        final_exam_name = custom_name if exam_name == 'CUSTOM' else exam_name
        
        if final_exam_name:
            exam = Exam.objects.create(user=request.user, name=final_exam_name)
            if final_exam_name in PREDEFINED_SYLLABUS:
                for sub_name in PREDEFINED_SYLLABUS[final_exam_name]:
                    Subject.objects.create(exam=exam, name=sub_name, weightage_marks=100)
            
            request.session['active_exam_id'] = exam.id
            return redirect('study_arena')
    return render(request, 'tracker/exam_select.html')

@login_required
def study_arena_view(request):
    active_exam_id = request.session.get('active_exam_id')
    if active_exam_id:
        exam = Exam.objects.filter(id=active_exam_id, user=request.user).first()
    else:
        exam = Exam.objects.filter(user=request.user).order_by('-created_at').first()
    
    if not exam:
        return redirect('select_exam')
        
    request.session['active_exam_id'] = exam.id
    return render(request, 'tracker/study_arena.html', {'exam': exam, 'subjects': exam.subjects.all()})

@login_required
def save_time_spent(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        topic_id = data.get('topic_id')
        seconds_to_add = int(data.get('seconds', 0))
        try:
            topic = Topic.objects.get(id=topic_id, subject__exam__user=request.user)
            topic.time_spent_seconds += seconds_to_add
            topic.save()
            total_subject_seconds = sum(t.time_spent_seconds for t in topic.subject.topics.all())
            return JsonResponse({'status': 'success', 'topic_time': topic.time_spent_seconds, 'subject_time': total_subject_seconds})
        except Topic.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Topic not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def add_custom_subject(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        weightage = int(data.get('weightage', 100))
        active_exam_id = request.session.get('active_exam_id')
        exam = Exam.objects.filter(id=active_exam_id, user=request.user).first()
        
        if exam and name:
            subject = Subject.objects.create(exam=exam, name=name, weightage_marks=weightage)
            Topic.objects.create(subject=subject, name="General Overview & Introduction", weightage_marks=10)
            return JsonResponse({'status': 'success', 'id': subject.id, 'name': subject.name})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_subject_topics(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id, exam__user=request.user)
        topics = [{'id': t.id, 'name': t.name, 'weightage': t.weightage_marks, 'is_completed': t.is_completed, 'time_spent': t.time_spent_seconds} for t in subject.topics.all().order_by('id')]
        return JsonResponse({'status': 'success', 'topics': topics})
    except Subject.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

@login_required
def update_subject_weightage(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            subject = Subject.objects.get(id=data.get('subject_id'), exam__user=request.user)
            subject.weightage_marks = int(data.get('weightage', 100))
            subject.save()
            return JsonResponse({'status': 'success'})
        except Subject.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def add_custom_topic(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            subject = Subject.objects.get(id=data.get('subject_id'), exam__user=request.user)
            topic = Topic.objects.create(subject=subject, name=data.get('name', '').strip(), weightage_marks=int(data.get('weightage', 10)))
            return JsonResponse({'status': 'success'})
        except Subject.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def toggle_topic_status(request, topic_id):
    try:
        topic = Topic.objects.get(id=topic_id, subject__exam__user=request.user)
        topic.is_completed = not topic.is_completed
        topic.save()
        return JsonResponse({'status': 'success', 'is_completed': topic.is_completed})
    except Topic.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)