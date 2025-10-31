

from django.urls import path
from . import views

app_name = 'payment'
urlpatterns = [
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('recruiter/dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
]

