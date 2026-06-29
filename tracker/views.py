from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Exam, Subject, Topic, SubTopic
import json

def login_view(request):
    if request.user.is_authenticated:
        return redirect('study_arena')
    error = None
    if request.method == 'POST':
        uid = request.POST.get('userid')
        pas = request.POST.get('password')
        user = authenticate(username=uid, password=pas)
        if user is not None:
            login(request, user)
            return redirect('study_arena')
        else:
            error = "Invalid User ID or Password"
    return render(request, 'tracker/login.html', {'error': error})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('study_arena')
    if request.method == 'POST':
        uid = request.POST.get('userid')
        pas = request.POST.get('password')
        first_name = request.POST.get('name')
        last_name = request.POST.get('surname')
        mobile = request.POST.get('mobile')
        
        request.session['signup_data'] = {
            'username': uid, 'password': pas, 'first_name': first_name, 
            'last_name': last_name, 'mobile': mobile
        }
        return redirect('verify_profile')
    return render(request, 'tracker/signup.html')

def verify_view(request):
    signup_data = request.session.get('signup_data')
    if not signup_data:
        return redirect('signup')
    if request.method == 'POST':
        data = signup_data
        user = User.objects.create_user(
            username=data['username'], password=data['password'],
            first_name=data['first_name'], last_name=data['last_name']
        )
        login(request, user)
        del request.session['signup_data']
        return redirect('select_exam')
    return render(request, 'tracker/verify.html', {'mobile': signup_data.get('mobile')})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def select_or_create_exam(request):
    if request.method == 'POST':
        selected_exam = request.POST.get('exam_dropdown')
        custom_name = request.POST.get('custom_exam_name', '').strip()
        exam_name = custom_name if selected_exam == 'CUSTOM' else selected_exam
        
        if exam_name:
            exam = Exam.objects.create(user=request.user, name=exam_name)
            defaults = ["History & Art Culture", "Geography", "Indian Polity", "Economy", "Environment & Science"]
            for sub in defaults:
                Subject.objects.create(exam=exam, name=sub, weightage_marks=100, target_minutes=6000)
            return redirect('study_arena')
    return render(request, 'tracker/exam_select.html')

@login_required
def study_arena_view(request):
    exam = Exam.objects.filter(user=request.user).order_by('-created_at').first()
    if not exam:
        return redirect('select_exam')
    return render(request, 'tracker/study_arena.html', {'exam': exam, 'subjects': exam.subjects.all()})

@login_required
def get_global_matrix_details(request):
    exam = Exam.objects.filter(user=request.user).order_by('-created_at').first()
    if not exam:
        return JsonResponse({'status': 'error'}, status=404)
        
    subjects_data = []
    for s in exam.subjects.all().order_by('id'):
        topics_data = []
        for t in s.topics.all().order_by('id'):
            sub_list = [{'id': sub.id, 'name': sub.name, 'is_completed': sub.is_completed, 'notes': sub.notes} for sub in t.subtopics.all()]
            topics_data.append({
                'id': t.id, 'name': t.name, 'weightage': t.weightage_marks,
                'pct': t.completion_percentage, 'earned': t.earned_marks,
                'set_hours': t.set_hours, 'time_needed': t.time_needed_to_complete,
                'logged_time_str': t.formatted_logged_time, 'subtopics': sub_list
            })
        subjects_data.append({
            'id': s.id, 'name': s.name, 'weightage': s.weightage_marks,
            'target_hours': round(s.target_minutes / 60), 'pct': s.completion_percentage,
            'earned': s.earned_marks, 'topics': topics_data
        })
    return JsonResponse({'status': 'success', 'subjects': subjects_data})

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
def update_topic_metrics(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        topic = Topic.objects.get(id=data.get('topic_id'), subject__exam__user=request.user)
        if 'set_hours' in data and data.get('set_hours') is not None:
            topic.set_hours = float(data.get('set_hours'))
        if 'completion_pct' in data and data.get('completion_pct') is not None:
            topic.manual_completion_pct = int(data.get('completion_pct'))
        topic.save()
        return JsonResponse({'status': 'success'})

@login_required
def sync_chronometer_seconds(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        topic = Topic.objects.get(id=data.get('topic_id'), subject__exam__user=request.user)
        topic.logged_seconds += int(data.get('added_seconds', 0))
        topic.save()
        return JsonResponse({'status': 'success', 'new_time_str': topic.formatted_logged_time})

@login_required
def delete_topic_node(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        topic = Topic.objects.get(id=data.get('topic_id'), subject__exam__user=request.user)
        topic.delete()
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