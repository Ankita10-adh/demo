from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import uuid

from karyathaloo.models import Recruiter, Job, UserProfile  # Your main models
from .models import PaymentTransaction  # Payment model
from .utils import generate_esewa_signature  # Make sure this exists

# ---------------------------
# Payment initiation
# ---------------------------
@login_required
def initiate_payment(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        purpose = request.POST.get('purpose', '')
        receiver_id = request.POST.get('receiver_id')  # Employee ID

        # Fetch the UserProfile instance of the receiver
        receiver = get_object_or_404(UserProfile, id=receiver_id)

        transaction_uuid = str(uuid.uuid4())

        # Create PaymentTransaction
        transaction = PaymentTransaction.objects.create(
            sender=request.user,
            receiver=receiver,  # Must be UserProfile instance
            amount=amount,
            purpose=purpose,
            transaction_uuid=transaction_uuid
        )

        data_dict = {
            'total_amount': str(amount),
            'transaction_uuid': transaction_uuid,
            'product_code': settings.ESEWA_MERCHANT_CODE,
            'signed_field_names': 'total_amount,transaction_uuid,product_code'
        }

        signature = generate_esewa_signature(data_dict, settings.ESEWA_SECRET_KEY)

        context = {
            'payment_url': settings.ESEWA_PAYMENT_URL,
            'amount': amount,
            'transaction_uuid': transaction_uuid,
            'product_code': settings.ESEWA_MERCHANT_CODE,
            'success_url': settings.ESEWA_SUCCESS_URL,
            'failure_url': settings.ESEWA_FAILURE_URL,
            'signature': signature
        }

        return render(request, 'payments/esewa_payment.html', context)

    return render(request, 'payments/initiate_payment.html')


# ---------------------------
# Payment success
# ---------------------------
@csrf_exempt
def payment_success(request):
    transaction_uuid = request.GET.get('transaction_uuid')
    ref_id = request.GET.get('refId')

    try:
        transaction = PaymentTransaction.objects.get(transaction_uuid=transaction_uuid)
        transaction.status = 'success'
        transaction.ref_id = ref_id
        transaction.save()
        return render(request, 'payments/success.html', {'transaction': transaction})
    except PaymentTransaction.DoesNotExist:
        return redirect('payment_failed')


# ---------------------------
# Payment failed
# ---------------------------
def payment_failed(request):
    return render(request, 'payments/failed.html')


# ---------------------------
# Recruiter dashboard & transactions
# ---------------------------
@login_required
def recruiter_dashboard(request):
    # Recruiter linked to logged-in user
    recruiter = get_object_or_404(Recruiter, user=request.user)

    # Total spent by recruiter
    total_spent = PaymentTransaction.objects.filter(sender=request.user, status='success').aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Jobs posted by this recruiter
    jobs = Job.objects.filter(recruiter=recruiter)

    employees = []
    for job in jobs:
        # Make sure 'assigned_workers' exists on Job model and links to UserProfile
        assigned_workers = getattr(job, 'assigned_workers', [])
        for worker in assigned_workers:
            worker.job_title = job.title
            worker.payment_amount = getattr(job, 'payment_amount', 0)
            employees.append(worker)

    transactions = PaymentTransaction.objects.filter(sender=request.user).order_by('-created_at')

    context = {
        'total_spent': total_spent,
        'employees': employees,
        'transactions': transactions,
    }

    return render(request, 'payments/recruiter_dashboard.html', context)


@login_required
def recruiter_transactions(request):
    transactions = PaymentTransaction.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'payments/recruiter_transactions.html', {'transactions': transactions})


# ---------------------------
# Employee dashboard & transactions
# ---------------------------
@login_required
def employee_dashboard(request):
    user = request.user  # User instance

    transactions = PaymentTransaction.objects.filter(receiver=user).order_by('-created_at')
    total_earned = transactions.filter(status='success').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'transactions': transactions,
        'total_earned': total_earned,
        'user': user,
    }
    return render(request, 'payments/employee_dashboard.html', context)




@login_required
def employee_transactions(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    transactions = PaymentTransaction.objects.filter(receiver=user_profile).order_by('-created_at')
    return render(request, 'payments/employee_transactions.html', {'transactions': transactions})
