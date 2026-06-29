from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Exam, Subject, Topic, SubTopic
import json

@login_required
def study_arena_view(request):
    active_exam_id = request.session.get('active_exam_id')
    exam = Exam.objects.filter(user=request.user).order_by('-created_at').first()
    if not exam:
        exam = Exam.objects.create(user=request.user, name="UPSC Blueprint Engine")
        # Standard default core subject setup
        Subject.objects.create(exam=exam, name="Indian Polity & Governance", weightage_marks=100)
        Subject.objects.create(exam=exam, name="History & Art Culture", weightage_marks=100)
    
    request.session['active_exam_id'] = exam.id
    return render(request, 'tracker/study_arena.html', {'exam': exam, 'subjects': exam.subjects.all()})

@login_required
def get_subject_matrix_details(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id, exam__user=request.user)
        topics_data = []
        for t in subject.topics.all().order_by('id'):
            sub_list = [{
                'id': s.id, 'name': s.name, 'is_completed': s.is_completed, 'notes': s.notes, 'time': s.time_spent_mins
            } for s in t.subtopics.all()]
            
            topics_data.append({
                'id': t.id, 'name': t.name, 'weightage': t.weightage_marks, 'target_mins': t.target_minutes,
                'pct': t.completion_percentage, 'earned': t.earned_marks, 'subtopics': sub_list, 'time': t.time_spent_mins
            })
        return JsonResponse({
            'status': 'success', 'subject_name': subject.name, 'weightage': subject.weightage_marks,
            'pct': subject.completion_percentage, 'earned': subject.earned_marks, 'topics': topics_data
        })
    except Subject.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

@login_required
def save_configuration_matrix(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            subject = Subject.objects.get(id=data.get('subject_id'), exam__user=request.user)
            subject.weightage_marks = int(data.get('weightage', 100))
            subject.target_minutes = int(data.get('target_hours', 100)) * 60
            subject.save()
            return JsonResponse({'status': 'success'})
        except Subject.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)

@login_required
def append_topic_node(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subject = Subject.objects.get(id=data.get('subject_id'), exam__user=request.user)
        Topic.objects.create(
            subject=subject, name=data.get('name'), 
            weightage_marks=int(data.get('weightage', 20)),
            target_minutes=int(data.get('target_hours', 10)) * 60
        )
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
        topic_id = data.get('topic_id')
        added_mins = int(data.get('minutes', 1))
        topic = Topic.objects.get(id=topic_id, subject__exam__user=request.user)
        topic.time_spent_mins += added_mins
        topic.save()
        return JsonResponse({'status': 'success'})