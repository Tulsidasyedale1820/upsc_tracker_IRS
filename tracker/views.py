from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Exam, Subject, Topic

# Predefined syllabus structural blueprints
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
    # This acts as our main dashboard control hub
    return render(request, 'tracker/study_arena.html')
    from django.http import JsonResponse
import json

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
            
            # Calculate total time spent on the entire subject for instant dashboard updates
            total_subject_seconds = sum(t.time_spent_seconds for t in topic.subject.topics.all())
            
            return JsonResponse({
                'status': 'success', 
                'topic_time': topic.time_spent_seconds,
                'subject_time': total_subject_seconds
            })
        except Topic.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Topic not found'}, status=404)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)