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




from django.shortcuts import render, redirect
from .models import EmailOTP
from django.contrib import messages

def verify_signup_otp(request, user_id):
    if request.method == "POST":
        otp_entered = request.POST.get('otp')
        try:
            otp_record = EmailOTP.objects.filter(user_id=user_id).latest('created_at')
            if otp_record.is_valid() and otp_record.otp == otp_entered:
                # OTP correct, log in user
                from django.contrib.auth import login
                login(request, otp_record.user)
                messages.success(request, "Login successful!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid or expired OTP!")
        except EmailOTP.DoesNotExist:
            messages.error(request, "OTP not found! Please request a new one.")
    
    return render(request, 'verify_otp.html')


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
from .models import UserProfile, EmailOTP
import re, random
from django.core.mail import send_mail
from django.conf import settings

def user_signup(request):
    if request.method == 'POST':
        # Step 1: Check if OTP is being submitted
        if 'otp' in request.POST:
            email = request.session.get('signup_email')
            otp_input = request.POST.get('otp', '').strip()
            try:
                otp_obj = EmailOTP.objects.get(email=email)
                if otp_obj.is_expired():
                    messages.error(request, "OTP expired. Try signing up again.")
                    otp_obj.delete()
                    return redirect('user_signup')
                if otp_input == otp_obj.otp:
                    # OTP correct → create User and Profile
                    user_data = request.session.get('signup_data')
                    user = User.objects.create_user(
                        username=user_data['email'],
                        first_name=user_data['fname'],
                        last_name=user_data['lname'],
                        email=user_data['email'],
                        password=user_data['password']
                    )
                    UserProfile.objects.create(
                        user=user,
                        mobile=user_data['contact'],
                        image=user_data.get('image'),
                        gender=user_data['gender']
                    )
                    otp_obj.verified = True
                    otp_obj.save()
                    # Clear session
                    request.session.pop('signup_data')
                    request.session.pop('signup_email')
                    messages.success(request, "Signup successful! You can now log in.")
                    return redirect('user_login')
                else:
                    messages.error(request, "Incorrect OTP.")
                    return render(request, 'otp_verify.html')
            except EmailOTP.DoesNotExist:
                messages.error(request, "OTP not found. Try signing up again.")
                return redirect('user_signup')

        # Step 2: Normal signup form submission
        fname = request.POST.get('fname', '').strip()
        lname = request.POST.get('lname', '').strip()
        email = request.POST.get('email', '').strip()
        contact = request.POST.get('contact', '').strip()
        password = request.POST.get('pwd', '')
        confirm_password = request.POST.get('cpwd', '')
        gender = request.POST.get('gender', '').strip()
        image = request.FILES.get('image')

        # Validation
        if not all([fname, lname, email, password, confirm_password, gender]):
            messages.error(request, "All fields are required.")
            return render(request, 'user_signup.html')

        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messages.error(request, "Invalid email format.")
            return render(request, 'user_signup.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'user_signup.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'user_signup.html')

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(email=email, defaults={'otp': otp, 'verified': False})

        # Send email
        send_mail(
            'Your Signup OTP',
            f'Your OTP for Karyathalo signup is: {otp}. It is valid for 5 minutes.',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        # Save user data temporarily in session
        request.session['signup_data'] = {
            'fname': fname,
            'lname': lname,
            'email': email,
            'contact': contact,
            'password': password,
            'gender': gender,
            'image': image.name if image else None,
        }
        request.session['signup_email'] = email

        return render(request, 'otp_verify.html')

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


from django.contrib.auth import update_session_auth_hash

def change_passwordadmin(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    error = ""

    if request.method == "POST":
        current = request.POST['currentpassword']
        new = request.POST['newpassword']

        user = request.user  

        # Verify old password
        if user.check_password(current):
            user.set_password(new)
            user.save()
            

            error = "No"
        else:
            error = "Not"

    return render(request, 'change_passwordadmin.html', {"error": error})


"""def change_passworduser(request):
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
    
    return render(request, 'change_passworduser.html', context)"""

from django.contrib.auth import update_session_auth_hash

def change_passworduser(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    error = ""

    if request.method == "POST":
        current = request.POST['currentpassword']
        new = request.POST['newpassword']

        user = request.user  # MAIN USER (has password)

        # Verify old password
        if user.check_password(current):
            user.set_password(new)
            user.save()
            
            # Optional: keep user logged in after password change
            # update_session_auth_hash(request, user)

            error = "No"
        else:
            error = "Not"

    return render(request, 'change_passworduser.html', {"error": error})

from django.contrib.auth import update_session_auth_hash

def change_passwordrecruiter(request):
    if not request.user.is_authenticated:
        return redirect('recruiter_login')

    error = ""

    if request.method == "POST":
        current = request.POST['currentpassword']
        new = request.POST['newpassword']

        user = request.user 

        try:
            # Check old password
            if user.check_password(current):
                user.set_password(new)
                user.save()

                # Optional: keep recruiter logged in after password change
                # update_session_auth_hash(request, user)

                error = "No"
            else:
                error = "Not"

        except Exception as e:
            error = "yes"

    return render(request, "change_passwordrecruiter.html", {"error": error})


"""def change_passwordrecruiter(request):
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
    
    return render(request, 'change_passwordrecruiter.html', context)"""




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


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime, date
import magic # Requires 'python-magic' and libmagic installed
# from .models import Job, Recruiter # Your models are assumed to be imported

# --- CONFIGURATION CONSTANTS (Keep these for security) ---
MAX_LOGO_SIZE = 2 * 1024 * 1024  # 2 MB
ALLOWED_LOGO_MIME_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif',
]

def edit_jobdetails(request, pid):
    # Fetch job; uses pid (Job ID)
    job = get_object_or_404(Job, id=pid)

    # 1. Authentication Check
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to edit job details.")
        return redirect('recruiter_login')

    # 2. SECURITY: Authorization Check (Fix for ForeignKey)
    try:
        # CORRECT ACCESS: Use the reverse manager (recruiter_set) and get the first object.
        # This assumes a user will only have ONE Recruiter profile.
        recruiter_profile = request.user.recruiter_set.first()
        
        if not recruiter_profile:
            # If the user is logged in but has NO linked Recruiter object
            messages.error(request, "User profile error. Your Recruiter profile is missing. Please complete your account setup.")
            return redirect('recruiter_home')
            
    except Exception:
        # Catch unexpected database errors during lookup
        messages.error(request, "User profile lookup failed.")
        return redirect('recruiter_home')
        
    # Crucial Authorization Check!
    if job.recruiter != recruiter_profile:
        messages.error(request, "Authorization Failed: You do not have permission to edit this job post.")
        return redirect('recruiter_job_list') 

    # 3. Process POST Request
    if request.method == "POST":
        
        # --- File Upload Security Check (Logo) ---
        logo_file = request.FILES.get("logo")
        if logo_file:
            # 3a. Size Check (DoS Prevention)
            if logo_file.size > MAX_LOGO_SIZE:
                messages.error(request, f"Logo size error. Logo must be less than {MAX_LOGO_SIZE / (1024 * 1024):.0f} MB.")
                return redirect('edit_jobdetails', pid=pid)

            # 3b. MIME Type Validation (Prevents Script Injection)
            try:
                mime_type = magic.from_buffer(logo_file.read(1024), mime=True)
                logo_file.seek(0)
            except Exception:
                messages.error(request, "Server error: Could not verify logo file type.")
                return redirect('edit_jobdetails', pid=pid)

            if mime_type not in ALLOWED_LOGO_MIME_TYPES:
                messages.error(request, f"Invalid logo file type ({mime_type}). Only JPEG, PNG, or GIF images are accepted.")
                return redirect('edit_jobdetails', pid=pid)
            
            job.logo = logo_file
        
        # --- Handle Text/Date Inputs ---
        
        # Assign fields safely (ORMs defend against SQLi)
        job.title = request.POST.get("title", job.title)
        job.company = request.POST.get("company", job.company)
        job.salary = request.POST.get("salary", job.salary)
        job.description = request.POST.get("description", job.description)
        job.experience = request.POST.get("experience", job.experience)
        job.location = request.POST.get("location", job.location)
        job.skills = request.POST.get("skills", job.skills)
        job.job_type = request.POST.get("job_type", job.job_type)
        job.work_mode = request.POST.get("work_mode", job.work_mode)

        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")
        
        try:
            if start_date_str:
                job.start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if end_date_str:
                job.end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            # Business Logic: End date must be after start date
            if job.end_date and job.start_date and job.end_date < job.start_date:
                messages.error(request, "The deadline cannot be before the start date.")
                return redirect('edit_jobdetails', pid=pid)
                
            # --- Final Save ---
            job.save()
            messages.success(request, f"Job '{job.title}' details updated successfully.")
            return redirect("recruiter_job_list") 

        except ValueError:
            messages.error(request, "Invalid date format submitted. Please use YYYY-MM-DD.")
            return redirect('edit_jobdetails', pid=pid)
        except Exception as e:
            messages.error(request, f"Unable to update job due to a server error: {e}")
            return redirect('edit_jobdetails', pid=pid)
            
    # If GET request, render the form
    context = {"job": job}
    return render(request, "edit_jobdetails.html", context)





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



def job_detail(request, pid):
    job = get_object_or_404(Job, id=pid)
    return render(request, "job_detail.html", {"job": job})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Job, Apply, UserProfile


@login_required(login_url='user_login')
def user_latestjobs(request):

    # get all jobs newest first
    jobs = Job.objects.all().order_by('-start_date')

    # logged-in user
    user = request.user

    # get student profile
    student = None
    try:
        student = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        student = None

    # list of applied job IDs
    li = []
    if student:
        applied = Apply.objects.filter(student=student).values_list('job_id', flat=True)
        li = list(applied)

    context = {
        'jobs': jobs,
        'li': li,
    }

    return render(request, 'user_latestjobs.html', context)




"""def apply_job(request, pid):
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
    return render(request, 'apply_job.html', context)"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date
# Import the necessary modules/models below
# from .models import Job, UserProfile, Apply
# import magic # Ensure this is installed and libmagic is configured

# --- CONFIGURATION CONSTANTS (Define these once at the top of your views.py) ---
MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB in bytes
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

def apply_job(request, pid):
    # 1. Authentication and Profile Check
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to apply for a job.")
        return redirect('user_login')

    job = get_object_or_404(Job, id=pid)
    
    try:
       #1. linking the userprofile with the student
        student = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, "Your  profile is incomplete. Please update your profile first.")
        return redirect('user_home') # Redirect to profile update page

    # 2. Check for Previous Application (Access Control)
    if Apply.objects.filter(job=job, student=student).exists():
        messages.info(request, f"You have already applied for the job: {job.title}.")
        return redirect('user_job_detail', job_id=job.id) 

    today = date.today()
    
    # 3. Date Validation (Business Logic)
    if today < job.start_date:
        messages.warning(request, f"Form Not Open: Applications start on {job.start_date}.")
        return redirect('user_job_detail', job_id=job.id)

    if today > job.end_date:
        messages.error(request, f"Application form closed: The deadline was {job.end_date}.")
        return redirect('user_job_detail', job_id=job.id)

    # 4. Handle Submission and Security Checks
    if request.method == 'POST':
        resume = request.FILES.get('resume')
        
        if not resume:
            messages.error(request, "Submission Failed: Please select a resume file to upload.")
            return redirect('apply_job', pid=pid)

        # 4a. Size Check (DoS Prevention)
        if resume.size > MAX_RESUME_SIZE:
            messages.error(request, f"File size error. Resume must be less than {MAX_RESUME_SIZE / (1024 * 1024):.0f} MB.")
            return redirect('apply_job', pid=pid)
        
        # 4b. MIME Type Validation (Prevents Script Injection)
        try:
            
            mime_type = magic.from_buffer(resume.read(1024), mime=True)
            resume.seek(0) # Reset pointer to allow Django to read it again
        except Exception:
            messages.error(request, "Internal server error: Could not verify file type.")
            return redirect('apply_job', pid=pid)

        if mime_type not in ALLOWED_MIME_TYPES:
            messages.error(request, f"Invalid file type ({mime_type}). Only PDF and DOCX files are accepted.")
            return redirect('apply_job', pid=pid)

        # 5. Save the Application
        try:
            Apply.objects.create(
                job=job,
                student=student,
                resume=resume
            )
            messages.success(request, f"Applied Successfully! Your application for '{job.title}' has been submitted.")
            return redirect('user_job_detail', job_id=job.id)
            
        except Exception as e:
            # Catch database/save errors
            messages.error(request, f"A database error occurred during submission. Please try again. Error: {e}")
            return redirect('apply_job', pid=pid)

    # If GET request, render the form
    context = {'job': job}
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

#payment system 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from .models import Job, Recruiter, Payment
from .utils import generate_esewa_checksum, generate_tx_code
import hashlib
import os 

# --- ESEWA CONFIGURATION (Sandbox/UAT) ---
# IMPORTANT: Replace these with your actual production keys when deploying.
ESEWA_PAYMENT_URL = "https://uat.esewa.com.np/epay/main" 
ESEWA_SUCCESS_URL = "http://127.0.0.1:8000/payment/success/" # Change to your domain and path
ESEWA_FAILURE_URL = "http://127.0.0.1:8000/payment/failure/" # Change to your domain and path
ESEWA_MERCHANT_CODE = "EPAYTEST" # Sandbox Merchant Code
JOB_POST_FEE = 100.00 # Example fee for posting a job

# --- RECRUITER PAYMENT INITIATION VIEW ---

def job_payment(request, pid):
    """
    Initiates the payment process by generating a transaction, 
    saving it to the DB, and redirecting the recruiter to eSewa.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to initiate payment.")
        return redirect('recruiter_login')

    job = get_object_or_404(Job, id=pid)
    
    # 1. Authorization Check (Ensures only the job owner can pay)
    try:
        recruiter_profile = request.user.recruiter_set.first() 
        if not recruiter_profile or job.recruiter != recruiter_profile:
            messages.error(request, "Authorization Failed: You cannot pay for this job.")
            return redirect('recruiter_job_list') 
    except Exception:
        messages.error(request, "Profile error. Cannot verify recruiter status.")
        return redirect('recruiter_home')

    if job.is_paid:
        messages.info(request, f"Job '{job.title}' is already paid and active.")
        return redirect('recruiter_job_list')

    try:
        # Generate a unique transaction code (oid)
        tx_code = generate_tx_code()
        amount = JOB_POST_FEE
        
        # 2. Create PENDING Payment Record
        payment = Payment.objects.create(
            recruiter=recruiter_profile,
            job=job,
            tx_code=tx_code,
            amount=amount,
            status='PENDING'
        )
        
        # 3. Generate Checksum
        checksum = generate_esewa_checksum(tx_code, amount, ESEWA_MERCHANT_CODE)
        
        # 4. Prepare eSewa Payload (Must be sent as a POST request)
        esewa_payload = {
            'amt': amount,           # Actual amount
            'psc': 0,                # Service charge (set to 0)
            'pdc': 0,                # Delivery charge (set to 0)
            'txAmt': 0,              # Tax amount (set to 0)
            'tAmt': amount,          # Total amount (amt + psc + pdc + txAmt)
            'pid': tx_code,          # Our unique transaction code (oid)
            'scd': ESEWA_MERCHANT_CODE, # Merchant code
            'su': ESEWA_SUCCESS_URL, # Success URL
            'fu': ESEWA_FAILURE_URL, # Failure URL
            'crs': checksum,         # Checksum for validation
        }

        context = {
            'esewa_url': ESEWA_PAYMENT_URL,
            'payload': esewa_payload,
            'job': job,
            'payment': payment
        }
        
        # Render a form that auto-submits via JavaScript to eSewa
        return render(request, 'job_payment.html', context)

    except Exception as e:
        messages.error(request, f"Could not initiate payment. Server error: {e}")
        return redirect('recruiter_job_list')


# --- ESEWA CALLBACK HANDLERS ---

# Note: eSewa sends back the 'oid' (our tx_code), 'refId' (their reference ID), and 'amt' (amount) in GET request

@transaction.atomic
def payment_success(request):
    """Handles successful payment callback from eSewa."""
    # Check if this is a GET request (eSewa sends GET)
    if request.method != 'GET':
        messages.error(request, "Invalid payment callback method.")
        return redirect('recruiter_home') 

    # 1. Retrieve data from eSewa query parameters
    tx_code = request.GET.get('oid') # Our internal transaction ID
    ref_id = request.GET.get('refId') # eSewa Reference ID
    amount = request.GET.get('amt') # Amount paid

    if not tx_code or not ref_id or not amount:
        messages.error(request, "Payment callback data is incomplete.")
        return redirect('recruiter_job_list')

    try:
        payment = Payment.objects.select_for_update().get(tx_code=tx_code)
        
        # 2. Basic Validation Checks
        if payment.status == 'SUCCESS':
            messages.info(request, "This payment was already processed successfully.")
            return redirect('recruiter_job_list')

        if payment.amount != Decimal(amount):
            messages.error(request, "Payment failed: Amount mismatch.")
            # Update status to failed due to discrepancy
            payment.status = 'FAILED'
            payment.save()
            return redirect('recruiter_job_list')

        # 3. Check Payment Status with eSewa (Recommended but not implemented here for brevity)
        # In a production app, you would make a server-to-server request to eSewa 
        # to verify the transaction status using the 'ref_id' (their ID).
        # For Sandbox, we trust the successful callback and proceed.

        # 4. Mark Transaction as SUCCESS and activate the Job
        payment.ref_id = ref_id
        payment.status = 'SUCCESS'
        payment.save()

        # Activate the related job post
        payment.job.is_paid = True
        payment.job.save()
        
        messages.success(request, f"Payment successful! Reference ID: {ref_id}. Your job post is now active.")
        return redirect('recruiter_job_list')

    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found.")
        return redirect('recruiter_job_list')
    except Exception as e:
        messages.error(request, f"An unexpected error occurred during payment processing: {e}")
        return redirect('recruiter_job_list')


def payment_failure(request):

    tx_code = request.GET.get('oid')
    if tx_code:
        # Optionally, mark the existing payment record as 'FAILED'
        try:
            payment = Payment.objects.get(tx_code=tx_code, status='PENDING')
            payment.status = 'FAILED'
            payment.save()
        except Payment.DoesNotExist:
            pass # Ignore if record doesn't exist or is already marked
    
    messages.warning(request, "Payment transaction was cancelled or failed.")
    return redirect('recruiter_job_list')


# --- PAYMENT HISTORY VIEWS ---

def payment_history(request):
    """Allows a recruiter to view their job posting payment history."""
    if not request.user.is_authenticated:
        messages.error(request, "Please log in.")
        return redirect('recruiter_login')

    try:
        recruiter_profile = request.user.recruiter_set.first()
        if not recruiter_profile:
            messages.error(request, "Profile not found.")
            return redirect('recruiter_home')
            
        # Fetch all payments related to this recruiter, ordered newest first
        payments = Payment.objects.filter(recruiter=recruiter_profile).order_by('-created_at').select_related('job')
        
        context = {
            'payments': payments,
            'is_recruiter': True
        }
        return render(request, 'payment_history.html', context)
        
    except Exception as e:
        messages.error(request, f"Error fetching history: {e}")
        return redirect('recruiter_home')

#def user_payment_history(request):
    """
    (Placeholder) If regular users/students paid for a service, 
    they would use a similar view linked to their profile.
    """
    #messages.info(request, "This view is for general user payment history, assuming a different service.")
    # Implement logic similar to recruiter_payment_history, but filtering by UserProfile
    #return redirect('user_home')

def recruiter_job_list(request):
   
    # 1. Authentication Check
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to view your job list.")
        # Assumes 'recruiter_login' is the URL name for the login page
        return redirect('recruiter_login') 

    try:
        # 2. Get Recruiter Profile
        # This assumes your Recruiter model has a ForeignKey back to the User model.
        # We use .first() because the related manager might return a queryset.
        recruiter_profile = request.user.recruiter_set.first()
        
        if not recruiter_profile:
            messages.error(request, "Recruiter profile not found.")
            return redirect('recruiter_home') 
            
        # 3. Fetch Job Data
        # Filter all Job objects where the recruiter field matches the current user's profile
        jobs = Job.objects.filter(recruiter=recruiter_profile).order_by('-id')
        
        # 4. Prepare Context
        context = {
            'jobs': jobs,
            # JOB_POST_FEE must be defined as a constant at the top of views.py
            'job_post_fee': JOB_POST_FEE 
        }
        
        # 5. Render Template
        # Assumes the template is located at 'app_name/templates/recruiter_job_list.html'
        return render(request, 'recruiter_job_list.html', context)
        
    except Exception as e:
        # Log error in console and notify user
        messages.error(request, f"Error fetching job list: {e}")
        return redirect('recruiter_home')