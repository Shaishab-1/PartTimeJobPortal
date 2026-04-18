from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Job, Application, Notification, Profile
from .forms import ProfileUpdateForm

def is_staff(user):
    return user.is_staff

def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('staff_dashboard')
    
    jobs = Job.objects.all()
    return render(request, 'jobs/home.html', {'jobs': jobs})

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type')  # 'staff' or 'normal'
        
        # Validation
        if not username or not email or not password1 or not password2 or not user_type:
            messages.error(request, 'All fields are required.')
            return render(request, 'jobs/register.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'jobs/register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'jobs/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'jobs/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'jobs/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_staff=(user_type == 'staff')
        )
        
        # Create profile for the new user
        Profile.objects.create(user=user)
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'jobs/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'jobs/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff:
                messages.success(request, f'Welcome, {user.username}! (Staff)')
                return redirect('staff_dashboard')
            else:
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'jobs/login.html')
    
    return render(request, 'jobs/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required(login_url='login')
def job_detail(request, id):
    job = get_object_or_404(Job, id=id)
    
    # Ensure profile exists for the user
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Check if profile is complete
        if not profile.is_complete:
            messages.error(request, 'Please complete your profile before applying for jobs.')
            return redirect('profile_update')

        # check if user already applied
        already_applied = Application.objects.filter(
            job=job,
            applicant=request.user
        ).exists()

        if not already_applied:
            application = Application.objects.create(
                job=job,
                applicant=request.user
            )
            # Create notification for the job poster
            notification_message = f"New application from {request.user.username} for {job.post}"
            Notification.objects.create(
                recipient=job.posted_by,
                application=application,
                notification_type='new_application',
                message=notification_message
            )
            messages.success(request, 'You have successfully applied for this job!')
        else:
            messages.warning(request, 'You have already applied for this job.')

        return redirect('job_detail', id=id)

    # Fetch application status if it exists
    application = Application.objects.filter(job=job, applicant=request.user).first()

    return render(request, 'jobs/job_detail.html', {
        'job': job, 
        'profile_is_complete': profile.is_complete,
        'user_application': application
    })

@login_required(login_url='login')
def profile_update(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('home')
    else:
        form = ProfileUpdateForm(instance=profile)
        
    return render(request, 'jobs/profile.html', {'form': form})

# Staff Views
@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def staff_dashboard(request):
    """Staff dashboard showing posted jobs and applications"""
    user_jobs = Job.objects.filter(posted_by=request.user)
    applications = Application.objects.filter(job__posted_by=request.user)
    notifications = Notification.objects.filter(recipient=request.user)
    unread_notifications = notifications.filter(is_read=False).count()
    
    context = {
        'jobs': user_jobs,
        'applications': applications,
        'total_jobs': user_jobs.count(),
        'total_applications': applications.count(),
        'unread_notifications': unread_notifications,
        'total_notifications': notifications.count(),
    }
    return render(request, 'jobs/staff_dashboard.html', context)

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def post_job(request):
    """Staff can post a new job"""
    if request.method == 'POST':
        post = request.POST.get('post')
        organization = request.POST.get('organization')
        description = request.POST.get('description')
        location = request.POST.get('location')
        work_hour = request.POST.get('work_hour')
        hourly_pay = request.POST.get('hourly_pay')
        
        # Validation
        if not all([post, organization, description, location, work_hour, hourly_pay]):
            messages.error(request, 'All fields are required.')
            return render(request, 'jobs/post_job.html')
        
        try:
            hourly_pay = int(hourly_pay)
            if hourly_pay <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'Hourly pay must be a positive number.')
            return render(request, 'jobs/post_job.html')
        
        # Create job
        Job.objects.create(
            post=post,
            organization=organization,
            description=description,
            location=location,
            work_hour=work_hour,
            hourly_pay=hourly_pay,
            posted_by=request.user
        )
        messages.success(request, 'Job posted successfully!')
        return redirect('staff_dashboard')
    
    return render(request, 'jobs/post_job.html')

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def view_job_applications(request, job_id):
    """View all applications for a specific job"""
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = Application.objects.filter(job=job)
    
    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'jobs/view_job_applications.html', context)

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def edit_job(request, job_id):
    """Edit a job posting"""
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    if request.method == 'POST':
        job.post = request.POST.get('post', job.post)
        job.organization = request.POST.get('organization', job.organization)
        job.description = request.POST.get('description', job.description)
        job.location = request.POST.get('location', job.location)
        job.work_hour = request.POST.get('work_hour', job.work_hour)
        hourly_pay = request.POST.get('hourly_pay')
        
        if hourly_pay:
            try:
                job.hourly_pay = int(hourly_pay)
                if job.hourly_pay <= 0:
                    raise ValueError
            except ValueError:
                messages.error(request, 'Hourly pay must be a positive number.')
                return render(request, 'jobs/edit_job.html', {'job': job})
        
        job.save()
        messages.success(request, 'Job updated successfully!')
        return redirect('staff_dashboard')
    
    return render(request, 'jobs/edit_job.html', {'job': job})

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def delete_job(request, job_id):
    """Delete a job posting"""
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('staff_dashboard')
    
    return render(request, 'jobs/delete_job.html', {'job': job})

# Notification Views
@login_required(login_url='login')
def notifications(request):
    """View all notifications for the current user"""
    user_notifications = Notification.objects.filter(recipient=request.user)
    unread_count = user_notifications.filter(is_read=False).count()
    
    context = {
        'notifications': user_notifications,
        'unread_count': unread_count,
    }
    return render(request, 'jobs/notifications.html', context)

@login_required(login_url='login')
def view_applicant_detail(request, notification_id):
    """View applicant details or employer update details"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    application = notification.application
    applicant = application.applicant
    job = application.job
    
    # Mark notification as read
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    
    if not request.user.is_staff:
        # Redirect job seekers to job detail to see their status
        return redirect('job_detail', id=application.job.id)

    context = {
        'notification': notification,
        'application': application,
        'applicant': applicant,
        'job': job,
    }
    return render(request, 'jobs/applicant_detail.html', context)

@login_required(login_url='login')
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

@login_required(login_url='login')
@user_passes_test(is_staff, login_url='home')
def update_application_status(request, application_id):
    """Update application status (approve/reject) and notify applicant"""
    application = get_object_or_404(Application, id=application_id, job__posted_by=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'approved', 'rejected']:
            application.status = new_status
            application.save()
            
            # Create notification for the job seeker (applicant)
            status_label = dict(Application.STATUS_CHOICES).get(new_status)
            notification_type = 'application_approved' if new_status == 'approved' else 'application_rejected'
            message = f"Your application for {application.job.post} has been {status_label.lower()}."
            
            Notification.objects.create(
                recipient=application.applicant,
                application=application,
                notification_type=notification_type,
                message=message
            )
            
            messages.success(request, f'Application status updated to {status_label} and applicant notified.')
            return redirect('view_applicant_detail', notification_id=request.POST.get('notification_id', 0))
    
    return redirect('staff_dashboard')