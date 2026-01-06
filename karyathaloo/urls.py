
from django.contrib import admin
from django.urls import path
from karyathaloo.views import*
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include 


urlpatterns = [
    path('',index,name='index'),
    path('admin_login',admin_login,name="admin_login"),
    path('user_login',user_login,name="user_login"),
    path('recruiter_login',recruiter_login,name="recruiter_login"),
    path('user_signup',user_signup,name="user_signup"),
    path('user_home',user_home,name="user_home"),
    path('Logout',Logout,name="Logout"),
    path('recruiter_signup',recruiter_signup,name="recruiter_signup"),
    path('recruiter_home',recruiter_home,name='recruiter_home'),
    path('admin_home',admin_home,name="admin_home"),
    path('view_user',view_user,name="view_user"),
    path('delete_application/<int:application_id>/',delete_application, name='delete_application'),
    path('delete_user/<int:pid>',delete_user,name="delete_user"),
    path('recruiter_pending',recruiter_pending,name='recruiter_pending'),
    path('change_status/<int:pid>',change_status,name="change_status"),
    path('recruiter_accept',recruiter_accept,name='recruiter_accept'),
    path('recruiter_reject',recruiter_reject,name='recruiter_reject'),
    path('recruiter_all',recruiter_all,name='recruiter_all'),
    path('delete_recruiter/<int:pid>',delete_recruiter,name="delete_recruiter"),
    path('change_passwordadmin',change_passwordadmin,name='change_passwordadmin'),
    path('change_passworduser',change_passworduser,name='change_passworduser'),
    path('change_passwordrecruiter',change_passwordrecruiter,name='change_passwordrecruiter'),
    path('add_job',add_job,name="add_job"),
    path('job_list',job_list,name="job_list"),
    path('edit_jobdetails/<int:pid>',edit_jobdetails,name="edit_jobdetails"),
    path('latest_jobs',latest_jobs,name="latest_jobs"),
    path('user_latestjobs',user_latestjobs,name="user_latestjobs"),
    path('job_detail/<int:pid>',job_detail,name="job_detail"),
    path('apply_job/<int:pid>',apply_job,name="apply_job"),
    path('apply_job/<int:pid>',apply_job,name="apply_job"),
    path('applied_candidatelist',applied_candidatelist,name="applied_candidatelist"),
    path('recruiter_job_view/<int:pid>',recruiter_job_view,name="recruiter_job_view"),
    #path('recruiter_applicant/<int:job_id>',recruiter_applicant,name="recruiter-applicant"),
    path('delete_job/<int:job_id>/',delete_job, name='delete_job'),
    path("recruiter/applicants/<int:job_id>/",recruiter_applied_candidates, name="recruiter_applied_candidates"),
    #path("recruiter/application/update/<int:app_id>/<str:new_status>/",update_applicant_status, name="update_applicant_status"),
    path("recruiter_contact/<int:job_id>/",recruiter_contact, name="recruiter_contact"),
    path('newsletter/',newsletter, name='newsletter'),

    path('about/mission/',about_mission, name='about_mission'),
    path('about/how-it-works/',about_how_it_works, name='about_how_it_works'),
    path('contact/',contact_us, name='contact_us'),

  
    path('recruiter/jobs/',recruiter_job_list, name='recruiter_job_list'),
    #path('history/',user_payment_history, name='user_payment_history'),
    # OTP verification page
    path('signup/verify-otp/',otp_verify, name='otp_verify'),
    path('recruiter-forgot-password/', recruiter_forgot_password, name='recruiter_forgot_password'),
    path('recruiter-verify-otp/', recruiter_verify_otp, name='recruiter_verify_otp'),
    path('recruiter-new-password/', recruiter_set_new_password, name='recruiter_set_new_password'),
    path("user-forgot-password/", user_forgot_password, name="user_forgot_password"),
    path("user-reset-otp/", user_reset_otp_verify, name="user_reset_otp_verify"),
    path("user-new-password/", user_set_new_password, name="user_set_new_password"),
    path('payments/',initiate_payment, name='initiate_payment'),
    path('payments/success/',payment_success, name='payment_success'),
    path('payments/failure/',payment_failure, name='payment_failure'),
    path('payments/delete/<int:payment_id>/',delete_payment, name='delete_payment'),
    path('payments/history/',payment_history, name='payment_history'),
    path('employee/payments/',employee_payments_history, name='employee_payments_history'),
    path(
        'recruiter/job/<int:job_id>/applicants/',
        recruiter_applicants,
        name='recruiter_applicants'
    ),




]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
