from django.shortcuts import render, get_object_or_404, redirect
from .models import Job,Application

def home(request):
    jobs = Job.objects.all()
    return render(request, 'jobs/home.html', {'jobs' : jobs})

def job_detail(request, id):
    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        # check if user already applied
        already_applied = Application.objects.filter(
            job=job,
            applicant=request.user
        ).exists()

        if not already_applied:
            Application.objects.create(
                job=job,
                applicant=request.user
            )

        return redirect('job_detail', id=id)

    return render(request, 'jobs/job_detail.html', {'job': job})