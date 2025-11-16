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

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile

def user_signup(request):
    if request.method == 'POST':
        fname = request.POST.get('fname', '').strip()
        lname = request.POST.get('lname', '').strip()
        email = request.POST.get('email', '').strip()
        contact = request.POST.get('contact', '').strip()
        password = request.POST.get('pwd', '')
        confirm_password = request.POST.get('cpwd', '')
        gender = request.POST.get('gender', '').strip()
        image = request.FILES.get('image')  # optional

        # Validation
        if not all([fname, lname, email, password, confirm_password, gender]):
            messages.error(request, "All fields are required.")
            return render(request, 'user_signup.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'user_signup.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'user_signup.html')

        try:
            # Create the user
            user = User.objects.create_user(
                username=email,
                first_name=fname,
                last_name=lname,
                email=email,   # Save email correctly
                password=password
            )

            # Create user profile
            UserProfile.objects.create(
                user=user,
                mobile=contact,
                image=image,
                gender=gender,
                type=""  # Can be set later if needed
            )

            messages.success(request, "Signup successful. You can now log in.")
            return redirect('user_login')  # Redirect to login after signup

        except Exception as ex:
            print("Signup error:", ex)
            messages.error(request, "Something went wrong. Please try again.")
            return render(request, 'user_signup.html')

    # GET request
    return render(request, 'user_signup.html')





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
    return render(request,'recruiter_home.html', {'recruiters': recruiters})





def Logout(request):
    logout(request)
    return redirect('index')
    
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Recruiter  # Assuming this is your recruiter profile model

def recruiter_signup(request):
    error = ""

    if request.method == 'POST':
        f = request.POST.get('fname', '').strip()
        l = request.POST.get('lname', '').strip()
        e = request.POST.get('email', '').strip()
        p = request.POST.get('pwd', '')
        cp = request.POST.get('cpwd', '')
        con = request.POST.get('company', '').strip()
        g = request.POST.get('gender', '').strip()
        c = request.POST.get('contact', '').strip()
        i = request.FILES.get('image')  # optional

        # 1️⃣ Check password match
        if p != cp:
            error = "password_mismatch"

        # 2️⃣ Check if email already exists
        elif User.objects.filter(username=e).exists():
            error = "email_exists"

        # 3️⃣ Check if gender selected
        elif not g:
            error = "gender_missing"

        else:
            try:
                # Create User
                user = User.objects.create_user(
                    username=e,
                    first_name=f,
                    last_name=l,
                    password=p,
                    email=e
                )

                # Create Recruiter profile
                Recruiter.objects.create(
                    user=user,
                    mobile=c,
                    image=i,
                    gender=g,
                    company=con,
                    type="recruiter",
                    status="pending"
                )

                error = "No"  # success
            except Exception as ex:
                print("Error in recruiter_signup:", ex)
                error = "yes"

    return render(request, 'recruiter_signup.html', {'error': error})




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


from django.shortcuts import render, redirect
from .models import UserProfile, Apply

def view_user(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    # All registered users
    all_users = UserProfile.objects.select_related('user').all()
    
    # All applications ordered by student
    all_applications = Apply.objects.select_related('student__user','job').order_by('student', 'apply_date')
    
    # Aggregate applications per student and store application id per job
    applicant_dict = {}
    for app in all_applications:
        student_id = app.student.id
        job_info = {
            'title': app.job.title,
            'job_type': app.job.job_type,
            'application_id': app.id  # store application id for delete button
        }
        if student_id not in applicant_dict:
            applicant_dict[student_id] = {
                'student': app.student,
                'jobs': [job_info]
            }
        else:
            applicant_dict[student_id]['jobs'].append(job_info)
    
    unique_applicants = list(applicant_dict.values())
    
    context = {
        'all_users': all_users,
        'job_applicants': unique_applicants
    }
    
    return render(request, 'view_user.html', context)





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Apply

def delete_application(request, application_id):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    
    # Fetch the application object or return 404 if not found
    application = get_object_or_404(Apply, id=application_id)
    
    # Optional: You can store info for messages
    applicant_name = f"{application.student.user.first_name} {application.student.user.last_name}"
    job_title = application.job.title
    
    # Delete the application
    application.delete()
    
    # Show a success message (optional)
    messages.success(request, f"Application of {applicant_name} for '{job_title}' has been deleted successfully.")
    
    # Redirect back to the view user page
    return redirect('view_user')




def delete_user(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    # Get the UserProfile object
    profile = get_object_or_404(UserProfile, id=pid)

    # Delete the linked User (cascades and removes UserProfile automatically)
    profile.user.delete()

    # Redirect back to the user list page
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
        student = UserProfile.objects.get(user=user)  
    except UserProfile.DoesNotExist:
        student = None

    li = []
    if student:
        data = Apply.objects.filter(student=student)
        li = [i.job.id for i in data]  

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

    return JsonResponse({'error': 'Invalid request'}, status=400)

"""import requests
from django.http import JsonResponse
from .forms import NewsletterForm
from django.conf import settings

def newsletter(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # Verify reCAPTCHA
        recaptcha_data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=recaptcha_data)
        result = r.json()

        if not result.get('success'):
            return JsonResponse({"error": "Invalid reCAPTCHA. Please try again."}, status=400)

        # Honeypot check
        if form.data.get('website'):
            return JsonResponse({"error": "Spam detected."}, status=400)

        # Check form validity
        if form.is_valid():
            # Save subscriber if not already exists
            email = form.cleaned_data['email']
            subscriber, created = form.Meta.model.objects.get_or_create(email=email)
            if created:
                return JsonResponse({"message": "Thank you for subscribing!"})
            else:
                return JsonResponse({"message": "You are already subscribed."})
        else:
            error_msg = list(form.errors.values())[0][0]
            return JsonResponse({"error": error_msg}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)"""

# In your existing views.py file

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Recruiter, UserProfile, Apply, RecruiterPayout, PaymentTransaction # Import new models
# Other imports...

@login_required
def recruiter_payout_initiation(request, application_id):
    """
    Recruiter initiates the payment process for an accepted application.
    """
    try:
        recruiter = Recruiter.objects.get(user=request.user)
    except Recruiter.DoesNotExist:
        messages.error(request, "Access denied. You are not a Recruiter.")
        return redirect('recruiter_dashboard')

    application = get_object_or_404(Apply, id=application_id, job__recruiter=recruiter)

    # Check if the application status is 'Accepted' (Required for payout)
    if application.status != 'Accepted':
        messages.error(request, "Cannot initiate payment. Employee status is not 'Accepted'.")
        return redirect('recruiter_application_detail', application_id=application_id)

    # Check if a Payout record already exists to prevent duplicate payment attempts
    if RecruiterPayout.objects.filter(application=application).exists():
        messages.warning(request, "Payment for this application has already been initiated or recorded.")
        return redirect('recruiter_application_detail', application_id=application_id)

    # Determine the payout amount (using the Job salary as the reference)
    payout_amount = application.job.salary # You might adjust this based on your business logic

    try:
        with transaction.atomic():
            # 1. Create the internal Payout Ledger entry
            payout = RecruiterPayout.objects.create(
                application=application,
                recruiter=recruiter,
                student=application.student,
                amount=payout_amount,
                payout_status='INITIATED'
            )
            
            # 2. **INTEGRATE EXTERNAL GATEWAY HERE**
            # Instead of a real API call, we simulate a successful transaction for the demo.
            # In a real system, this would call your payment service (e.g., PayPal, Bank API).
            
            external_txn_id = f"TXN-{application.id}-{payout.id}-{payout.created_at.timestamp()}" # Placeholder ID
            
            # 3. Create the Transaction Detail record
            PaymentTransaction.objects.create(
                payout=payout,
                transaction_id=external_txn_id,
                gateway_name='Simulated Bank Transfer',
                transaction_status='SUCCESS', # Simulate success for demo
                processed_at=timezone.now() # Requires `from django.utils import timezone`
            )
            
            # 4. Update the Payout Ledger status
            payout.payout_status = 'COMPLETED'
            payout.save()

            messages.success(request, f"Payout of Rs. {payout_amount} successfully processed for {application.student.user.username}.")
            
    except Exception as e:
        messages.error(request, f"An error occurred during payment processing: {e}")
        # Optionally, update Payout status to FAILED here

    return redirect('recruiter_application_detail', application_id=application_id)


# --- Dashboard Views ---

@login_required
def recruiter_payment_history(request):
    """
    Recruiter dashboard to view all payout transactions they initiated.
    """
    try:
        recruiter = Recruiter.objects.get(user=request.user)
    except Recruiter.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect('naviagtion')

    # Get all payouts initiated by this recruiter
    payouts = RecruiterPayout.objects.filter(recruiter=recruiter).order_by('-created_at')

    # Template name: core/recruiter_payout_history.html
    return render(request, 'payments/recruiter_payout_history.html', {'payouts': payouts})


@login_required
def user_payment_history(request):
    """
    User/Employee dashboard to view all payments they received.
    """
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect('navigation')

    # Get all payouts where this user is the student
    received_payments = RecruiterPayout.objects.filter(student=user_profile, 
                                                       payout_status='COMPLETED').order_by('-created_at')

    # Template name: core/user_payment_history.html
    return render(request, 'payments/user_payment_history.html', {'received_payments': received_payments})

from django.shortcuts import render, redirect
# from django.core.mail import send_mail # You'll need this for real email sending

# 1. Mission and Story (Renders about_mission.html)
def about_mission(request):
    """Renders the company's mission and story page."""
    return render(request, 'about_mission.html')

# 2. How It Works (Renders about_how_it_works.html)
def about_how_it_works(request):
    """Renders the guide explaining platform functionality for users and recruiters."""
    return render(request, 'about_how_it_works.html')
# 3. Contact Us (Handles GET and POST requests)
def contact_us(request):
    """
    Handles displaying the contact form (GET) and processing the message submission (POST).
    """
    message_context = {}

    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Simple Validation (You should expand this!)
        if not name or not email or not subject or not message:
            message_context['message'] = 'Error: Please fill in all fields.'
        else:
            try:
                # --- PROCESSING ACTION (E.g., Sending Email) ---
                
                # To make this functional, you must configure Django's EMAIL_HOST settings.
                # Example:
                # send_mail(
                #     f"New Contact Form Submission: {subject}",
                #     f"From: {name} ({email})\n\nMessage:\n{message}",
                #     email,  # Sender email address
                #     ['admin@yourjobportal.com'], # Recipient list
                #     fail_silently=False,
                # )
                
                # --- SUCCESS ---
                message_context['message'] = 'Thank you! Your message has been sent successfully. We will respond soon.'
            
            except Exception:
                # --- ERROR ---
                message_context['message'] = 'A system error occurred while sending your message. Please try again later.'
            
            # Note: You can optionally redirect here after success instead of re-rendering.
            # return redirect('contact_us') 

    # Renders the template, passing any message context
    return render(request, 'about_contact.html', message_context)