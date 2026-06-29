import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import UserProfile, SubjectBlock, TopicTarget

def signup_view(request):
    error_msg = ""
    step = 1
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    mobile = request.POST.get('mobile_number', '')
    otp = request.POST.get('otp', '')
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == "submit_info":
            # Strip spaces or country code characters to check raw digits length
            clean_mobile = re.sub(r'\D', '', mobile)
            if len(clean_mobile) != 10:
                error_msg = "Validation failed: Mobile number must be exactly 10 digits long."
            elif first_name and last_name and mobile: 
                step = 2
            else: 
                error_msg = "Please fill in all identity fields."
                
        elif action == "verify_otp":
            if otp == "1234": 
                step = 3
            else: 
                error_msg = "Invalid OTP verification code. Try again."; step = 2
                
        elif action == "create_account":
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            # Match parameters securely
            if password != confirm_password:
                error_msg = "Authentication rule failure: Passwords do not match."; step = 3
            elif len(password) < 8 or len(password) > 20 or not re.search(r"\d", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                error_msg = "Password criteria failed: Must be 8-20 characters with at least 1 number and 1 special symbol."; step = 3
            else:
                clean_mobile = re.sub(r'\D', '', mobile)
                username = f"user_{clean_mobile}"
                if User.objects.filter(username=username).exists():
                    error_msg = "Authentication block: Mobile number already registered."; step = 1
                else:
                    new_user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
                    UserProfile.objects.create(user=new_user, mobile_number=clean_mobile, is_verified=True)
                    return redirect('login_route')
                    
    return render(request, 'tracker/signup.html', {
        'step': step, 
        'error_msg': error_msg, 
        'first_name': first_name, 
        'last_name': last_name, 
        'mobile_number': mobile
    })

def login_view(request):
    error_msg = ""
    if request.method == "POST":
        mobile = request.POST.get('mobile_number', '')
        password = request.POST.get('password', '')
        
        clean_mobile = re.sub(r'\D', '', mobile)
        username = f"user_{clean_mobile}"
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error_msg = "Authentication failed: Invalid mobile number or password parameters matched."
            
    return render(request, 'tracker/login.html', {'error_msg': error_msg})

@login_required(login_url='login_route')
def dashboard_view(request):
    CORE_SUBJECTS = ["Polity", "Geography", "History", "Economics", "Environment & Ecology", "Current Affairs"]
    for sub in CORE_SUBJECTS:
        SubjectBlock.objects.get_or_create(user=request.user, name=sub)

    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == "update_subject_time":
            subject_id = request.POST.get('subject_id')
            sb = get_object_or_404(SubjectBlock, id=subject_id, user=request.user)
            sb.allocated_subject_hours = float(request.POST.get('allocated_subject_hours', 0))
            sb.save()
            return redirect('dashboard')

        elif action == "add_topic":
            subject_id = request.POST.get('subject_id')
            sb = get_object_or_404(SubjectBlock, id=subject_id, user=request.user)
            TopicTarget.objects.create(
                subject_block=sb,
                topic_name=request.POST.get('topic_name', 'New Chapter'),
                allocated_hours=float(request.POST.get('allocated_hours', 0)),
                completion_percentage=int(request.POST.get('completion_percentage', 0)),
                user_comments=request.POST.get('user_comments', '')
            )
            return redirect('dashboard')
            
        elif action == "update_row":
            topic_id = request.POST.get('topic_id')
            target_topic = get_object_or_404(TopicTarget, id=topic_id, subject_block__user=request.user)
            target_topic.topic_name = request.POST.get('edit_topic_name')
            target_topic.allocated_hours = float(request.POST.get('edit_hours', 0))
            target_topic.completion_percentage = int(request.POST.get('edit_percentage', 0))
            target_topic.user_comments = request.POST.get('edit_comments', '')
            target_topic.save()
            return redirect('dashboard')

    subjects = SubjectBlock.objects.filter(user=request.user)
    subject_data_list = []
    total_subject_scores_sum = 0
    active_subjects_count = 0
    
    for sb in subjects:
        targets = sb.targets.all()
        if sb.allocated_subject_hours > 0:
            total_spent_hours = sum(t.spent_hours for t in targets)
            sub_avg = round((total_spent_hours / sb.allocated_subject_hours) * 100, 1)
            if sub_avg > 100: sub_avg = 100.0
        else:
            sub_avg = 0.0
            
        total_subject_scores_sum += sub_avg
        active_subjects_count += 1
            
        subject_data_list.append({
            'obj': sb,
            'targets': targets,
            'subject_avg': sub_avg
        })
        
    overall_avg_completion = 0
    if active_subjects_count > 0:
        overall_avg_completion = round(total_subject_scores_sum / active_subjects_count, 1)

    return render(request, 'tracker/dashboard.html', {
        'subject_data_list': subject_data_list,
        'overall_avg_completion': overall_avg_completion
    })

def logout_action(request):
    logout(request)
    return redirect('login_route')