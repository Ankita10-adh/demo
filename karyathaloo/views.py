from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import*
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
import pytz
from datetime import date






def index(request):
    return render(request,'index.html')



def admin_login(request):
    error = ""
    if request.method == "POST":
        u = request.POST.get("uname")   # safer than ['uname']
        p = request.POST.get("pwd")     # safer than ['pwd']

        user = authenticate(username=u, password=p)
        if user is not None:   # check if user exists
            if user.is_staff:  # only allow staff/admin
                login(request, user)  # start session
                error = "No"   # success
            else:
                error = "yes"  # not staff
        else:
            error = "yes"      # invalid credentials

    d = {'error': error}
    return render(request, "admin_login.html", d)

def user_login(request):
    error = ""
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)

        if user is not None:
            login(request, user)
            error = "No"
            return redirect("user_home")   
        else:
            error = "yes"

    return render(request, "user_login.html", {"error": error})








"""def recruiter_login(request):
    error=""
    if request.method=="POST":
        u=request.POST['uname'];
        p=request.POST['pwd'];
        user=authenticate(username=u,password=p)
        if user:
            try:
                user1= Recruiter.objects.get(user=user)
                if user1.type=="recruiter" and user1.status!="pending":
                    login(request,user)
                    error="No"
                else:
                    error="Not"  
            except:
                error="yes"    
        else:
            error="yes"
    d={'error':error}       
   
    return render(request,'recruiter_login.html',d)"""




def recruiter_login(request):
    error = ""
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']

        user = authenticate(username=u, password=p)

        if user:
            try:
                recruiter = Recruiter.objects.get(user=user)
                
                if recruiter.type == "recruiter":
                    if recruiter.status == "Accept":
                        login(request, user)
                        return redirect('recruiter_home')
                    elif recruiter.status == "Pending":
                        error = "Your account is still pending approval by admin."
                    elif recruiter.status == "Reject":
                        error = "Your account has been rejected by admin."
                    else:
                        error = "Invalid account status. Contact admin."
                else:
                    error = "You are not a recruiter."
            except Recruiter.DoesNotExist:
                error = "Recruiter profile not found."
        else:
            error = "Invalid username or password."

    d = {'error': error}
    return render(request, 'recruiter_login.html', d)



def user_signup(request):
    error = ""
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        i = request.FILES.get('image')  # safer to use get()
        p = request.POST['pwd']
        e = request.POST['email']
        c = request.POST['contact']
        g = request.POST['gender']

        try:
            # 1. Create the User
            user = User.objects.create_user(username=e, first_name=f, last_name=l, password=p)
            
            # 2. Create the UserProfile
            UserProfile.objects.create(user=user, mobile=c, image=i, gender=g, type="")

            error = "No"  # no error
        except Exception as ex:
            print("Signup error:", ex)
            error = "yes"  # error occurred

    return render(request, 'user_signup.html', {'error': error})



def user_home(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
        
    user = request.user

    try:
        juser = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # handle the case where profile doesn't exist
        return redirect('user_signup')

    error = ""

    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        c = request.POST['contact']
        g = request.POST['gender']

        # Update User model
        juser.user.first_name = f
        juser.user.last_name = l
        juser.user.save()  # Save User object

        # Update UserProfile model
        juser.mobile = c
        juser.gender = g   

        if 'image' in request.FILES:
            juser.image = request.FILES['image']

        try:
            juser.save()
            error = "No"
        except:
            error = "yes"

    return render(request, 'user_home.html', {'juser': juser, 'error': error})


def admin_home(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    return render(request, 'admin_home.html', {"user": request.user})

def recruiter_home(request):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')
    return render(request,'recruiter_home.html')


def Logout(request):
    logout(request)
    return redirect('index')
    
def recruiter_signup(request):
    error = ""
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        i = request.FILES.get('image')
        p = request.POST['pwd']
        e = request.POST['email']
        con = request.POST['company']
        g = request.POST['gender']
        c = request.POST['contact']

        try:
            # ✅ Create a User first
            user = User.objects.create_user(
                first_name=f,
                last_name=l,
                username=e,
                password=p,
                email=e
            )

            # ✅ Then create Recruiter linked to that User
            Recruiter.objects.create(
                user=user,
                mobile=c,
                image=i,
                gender=g,
                company=con,
                type="recruiter",
                status="pending"
            )

            error = "No"
        except Exception as e:
            print("Error in recruiter_signup:", e)  # useful for debugging
            error = "yes"

    d = {'error': error}
    return render(request, 'recruiter_signup.html', d)



def recruiter_home(request):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')

    user = request.user
    recruiter = Recruiter.objects.get(user=user)
    error = ""

    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        c = request.POST['contact']
        g = request.POST['gender']

        # Update related User model
        recruiter.user.first_name = f
        recruiter.user.last_name = l
        recruiter.user.save()  # important: save the User object

        # Update Recruiter model
        recruiter.mobile = c
        recruiter.gender = g   

        if 'image' in request.FILES:
            recruiter.image = request.FILES['image']

        try:
            recruiter.save()
            error = "No"
        except:
            error = "yes"

    d = {'recruiter': recruiter, 'error': error}
    return render(request, 'recruiter_home.html', d)



def view_user(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    data= UserProfile.objects.all()      # fetech all the data of job seeker from the users models
    d={'data':data}                 # dictionary variable
    return render(request,'view_user.html',d)



def delete_user(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    try:
        employee = UserProfile.objects.get(id=pid)
        employee.delete()
    except UserProfile.DoesNotExist:
        pass  # Optionally handle error (e.g., show message)

    # ✅ Redirect to the user list page
    return redirect('view_user')





"""def delete_recruiter(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    # Safely fetch the recruiter
    recruiter = get_object_or_404(Recruiter, id=pid)

    # Delete linked user first (optional)
    recruiter.user.delete()

    # Delete recruiter object
    recruiter.delete()

    return redirect('recruiter_all')"""

def delete_recruiter(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    recruiter = get_object_or_404(Recruiter, id=pid)

    # Delete the linked user first
    if recruiter.user:
        recruiter.user.delete()

    # Delete the recruiter itself
    recruiter.delete()

    return redirect('recruiter_all')


def recruiter_pending(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    # Fetch pending requests from the database
    data = Recruiter.objects.filter(status='pending')
    
    context = {
        'data': data
    }
    return render(request, 'recruiter_pending.html', context)

def change_status(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error=""

    # Fetch pending requests from the database
    recruiter = Recruiter.objects.get(id=pid)
    if request.method=="POST":
        s=request.POST['status']
        recruiter.status=s
        try:
            recruiter.save()
            error="No"
        except:
            error="yes"
    context = {'recruiter': recruiter, 'error':error}
    
    return render(request, 'change_status.html', context)

def recruiter_accept(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    # Fetch pending requests from the database
    data = Recruiter.objects.filter(status='Accept')
    
    context = {
        'data': data
    }
    return render(request, 'recruiter_accept.html', context)

def recruiter_reject(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    # Fetch pending requests from the database
    data = Recruiter.objects.filter(status='Reject')
    
    context = {
        'data': data
    }
    return render(request, 'recruiter_reject.html', context)

def recruiter_all(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    # Fetch pending requests from the database
    data = Recruiter.objects.all()
    
    context = {
        'data': data
    }
    return render(request, 'recruiter_all.html', context)


def change_passwordadmin(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error=""

    # Fetch pending requests from the database
    
    if request.method=="POST":
        c=request.POST['currentpassword']
        n=request.POST['newpassword']
        
        try:
            u=UserProfile.objects.get(id=request.user.id)
            if u.check_password(c) :
                u.set_password(n)
                u.save()
                error="No"
            else:
                error="Not"
        except:
            error="yes"

    context = {'error':error}
    
    return render(request, 'change_passwordadmin.html', context)

def change_passworduser(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    error=""

    # Fetch pending requests from the database
    
    if request.method=="POST":
        c=request.POST['currentpassword']
        n=request.POST['newpassword']
        
        try:
            u=UserProfile.objects.get(id=request.user.id)
            if u.check_password(c) :
                u.set_password(n)
                u.save()
                error="No"
            else:
                error="Not"
        except:
            error="yes"

    context = {'error':error}
    
    return render(request, 'change_passworduser.html', context)

def change_passwordrecruiter(request):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')
    error=""

    # Fetch pending requests from the database
    
    if request.method=="POST":
        c=request.POST['currentpassword']
        n=request.POST['newpassword']
        
        try:
            u=UserProfile.objects.get(id=request.user.id)
            if u.check_password(c) :
                u.set_password(n)
                u.save()
                error="No"
            else:
                error="Not"
        except:
            error="yes"

    context = {'error':error}
    
    return render(request, 'change_passwordrecruiter.html', context)




def add_job(request):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')  # Ensure recruiter is logged in

    try:
        recruiter = Recruiter.objects.get(user=request.user)
    except Recruiter.DoesNotExist:
        return render(request, 'add_job.html', {'message': 'Recruiter profile not found.'})

    if request.method == "POST":
        title = request.POST.get('title')
        company = request.POST.get('company')
        logo = request.FILES.get('logo')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        salary = request.POST.get('salary')
        experience = request.POST.get('experience')
        location = request.POST.get('location')
        skills = request.POST.get('skills')
        job_type = request.POST.get('job_type')
        work_mode = request.POST.get('work_mode')
        description = request.POST.get('description')

        try:
            Job.objects.create(
                recruiter=recruiter,
                title=title,
                company=company,
                logo=logo,
                start_date=start_date,
                end_date=end_date,
                salary=salary,
                experience=experience,
                location=location,
                skills=skills,
                job_type=job_type,
                work_mode=work_mode,
                description=description
            )
            # Redirect immediately to prevent duplicate POST
            return redirect('job_list')
        except Exception as e:
            print("Error:", e)
            return render(request, 'add_job.html', {'message': 'Failed to add job. Try again.'})

    return render(request, 'add_job.html')






def edit_jobdetails(request, pid):
    job = get_object_or_404(Job, id=pid)
    error = ""

    if request.method == "POST":
        job.title = request.POST.get("title", job.title)
        job.company = request.POST.get("company", job.company)

        # Handle logo safely
        if request.FILES.get("logo"):
            job.logo = request.FILES.get("logo")

        # Handle start and end dates safely
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        try:
            if start_date:
                job.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if end_date:
                job.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            error = "Invalid date format. Use YYYY-MM-DD."

        # Assign remaining fields safely
        job.salary = request.POST.get("salary", job.salary)
        job.description = request.POST.get("description", job.description)
        job.experience = request.POST.get("experience", job.experience)
        job.location = request.POST.get("location", job.location)
        job.skills = request.POST.get("skills", job.skills)
        job.job_type = request.POST.get("job_type", job.job_type)
        job.work_mode = request.POST.get("work_mode", job.work_mode)

        # Save if no error
        if not error:
            try:
                job.save()
                return redirect("job_list")  # redirect to job listing page
            except Exception as e:
                error = f"Unable to update job: {e}"

    return render(request, "edit_jobdetails.html", {"job": job, "error": error})






def job_list(request):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')
    user=request.user
    recruiter = Recruiter.objects.get(user=request.user)
    jobs=Job.objects.filter(recruiter=recruiter)
    d={'jobs':jobs}
    return render(request, 'job_list.html',d)

def latest_jobs(request):
    jobs = Job.objects.all().order_by('-start_date')  
    context = {'jobs': jobs}  
    return render(request, 'latest_jobs.html', context)

def user_latestjobs(request):
    jobs = Job.objects.all().order_by('-start_date')  
    
    user = request.user
    try:
        student = UserProfile.objects.get(user=user)  # ✅ fixed: was `users`
    except UserProfile.DoesNotExist:
        student = None

    li = []
    if student:
        data = Apply.objects.filter(student=student)
        li = [i.job.id for i in data]  # ✅ cleaner way to collect job ids

    context = {
        'jobs': jobs,
        'li': li
    }  

    return render(request, 'user_latestjobs.html', context)

def job_detail(request, pid):
    job = get_object_or_404(Job, id=pid)
    return render(request, "job_detail.html", {"job": job})






def apply_job(request, pid):
    if not request.user.is_authenticated:
        return redirect('user_login')

    error = ""
    user = request.user

    try:
        student = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        error = "User profile not found"
        return render(request, 'apply_job.html', {'error': error})

    job = get_object_or_404(Job, id=pid)
    today = date.today()

    if job.end_date < today:
        error = "Application form closed"
    elif job.start_date > today:
        error = "Form not open yet"
    else:
        if request.method == 'POST':
            resume = request.FILES.get('resume')
            if resume:
                Apply.objects.create(
                    job=job,
                    student=student,
                    resume=resume
                )
                error = "Applied Successfully!"
            else:
                error = "Please upload a resume"

    context = {
        'job': job,
        'error': error
    }
    return render(request, 'apply_job.html', context)









def applied_candidatelist(request):
    if not request.user.is_authenticated:
        return redirect("recruiter_login")

    # Get recruiter
    recruiter = get_object_or_404(Recruiter, user=request.user)

    # Fetch all applications for this recruiter’s jobs
    applications = Apply.objects.filter(job__recruiter=recruiter).select_related("student__user", "job")

    if request.method == "POST":
        app_id = request.POST.get("application_id")
        status = request.POST.get("status")
        try:
            application = Apply.objects.get(id=app_id, job__recruiter=recruiter)
            application.status = status
            application.save()
        except Apply.DoesNotExist:
            pass

        return redirect("applied_candidatelist")  # add the missing 'e'


    return render(request, "Applied_candidatelist.html", {"applications": applications})







def recruiter_job_view(request, pid):
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('recruiter_login')
    
    # Get the recruiter object linked to the logged-in user
    recruiter = get_object_or_404(Recruiter, user=request.user)
    
    # Get the job that belongs to this recruiter
    job = get_object_or_404(Job, id=pid, recruiter=recruiter)
    
    # Render the job details
    return render(request, 'recruiter_job_view.html', {'job': job})



def recruiter_applicant(request, job_id):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')

    recruiter = get_object_or_404(Recruiter, user=request.user)
    job = get_object_or_404(Job, id=job_id, recruiter=recruiter)

    message = ""  # For alerts

    if request.method == 'POST':
        action = request.POST.get('action')
        apply_id = request.POST.get('apply_id')
        application = get_object_or_404(Apply, id=apply_id, job=job)

        if action == 'accept':
            application.status = 'Accepted'
            message = f"{application.student.user.first_name} has been accepted!"
        elif action == 'reject':
            application.status = 'Rejected'
            message = f"{application.student.user.first_name} has been rejected!"

        application.save()

    applicants = Apply.objects.filter(job=job)

    return render(request, 'recruiter_applicant.html', {
        'job': job,
        'applicants': applicants,
        'message': message
    })




def delete_job(request, job_id):
    # Check if recruiter is logged in
    if not request.user.is_authenticated:
        return redirect('recruiter_login')

    # Get the recruiter profile
    recruiter = get_object_or_404(Recruiter, user=request.user)

    # Get the job, ensure it belongs to the logged-in recruiter
    job = get_object_or_404(Job, id=job_id, recruiter=recruiter)

    # Delete the job
    job.delete()

    # Redirect back to the recruiter job list or dashboard
    return redirect('job_list')  # replace 'job_list' with your recruiter job list URL name




def recruiter_applied_candidates(request):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')   # only recruiters can access

    try:
        recruiter = Recruiter.objects.get(user=request.user)
    except Recruiter.DoesNotExist:
        return redirect('recruiter_login')

    if request.method == "POST":
        app_id = request.POST.get("application_id")
        new_status = request.POST.get("status")
        if app_id and new_status:
            try:
                application = Apply.objects.get(id=app_id, job__recruiter=recruiter)
                application.status = new_status
                application.save()
            except Apply.DoesNotExist:
                pass

    # fetch only applications for jobs posted by this recruiter
    applications = Apply.objects.filter(job__recruiter=recruiter).select_related("student__user", "job")

    return render(request, "applied_candidates.html", {"applications": applications})


def recruiter_contact(request, job_id):
    # Get the job first
    job = get_object_or_404(Job, id=job_id)

    # Get recruiter from the job
    recruiter = job.recruiter

    return render(request, "recruiter_contact.html", {
        "job": job,
        "recruiter": recruiter
    })



"""
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import NewsletterForm
from .models import Subscriber

def newsletter(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            # Honeypot check
            if form.cleaned_data.get('website'):
                return JsonResponse({'error': 'Spam detected'}, status=400)

            email = form.cleaned_data['email']

            # Save subscriber if new
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            if created:
                # Send confirmation to subscriber
                send_mail(
                    'Newsletter Subscription',
                    'Thank you for subscribing to our newsletter!',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                # Notify admin
                send_mail(
                    'New Subscriber',
                    f'New subscriber: {email}',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )

            return JsonResponse({'message': 'Subscription successful'})

        else:
            return JsonResponse({'error': 'Invalid submission'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)"""

import requests
from django.http import JsonResponse
from .forms import NewsletterForm
from django.conf import settings

def newsletter(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # Verify reCAPTCHA
        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not result.get('success'):
            return JsonResponse({"error": "Invalid reCAPTCHA. Please try again."}, status=400)

        # Check form validity
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Thank you for subscribing!"})
        else:
            error_msg = list(form.errors.values())[0][0]
            return JsonResponse({"error": error_msg}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
