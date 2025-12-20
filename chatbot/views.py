from django.http import JsonResponse

def chatbot_response(request):
    user_message = request.GET.get('message', '').lower()
    
    # --- STATIC RULES (Always work) ---
    if "contact" in user_message:
        return JsonResponse({'response': "You can email us at support@karyathalo.com or visit our office in Kathmandu."})
    
    if "signup" in user_message or "register" in user_message:
        return JsonResponse({'response': "Click the 'Register' button on the top right. You can join as a Job Seeker or a Recruiter."})

    if "esewa" in user_message or "payment" in user_message:
        return JsonResponse({'response': "Karyathalo uses eSewa for all premium job postings. It's safe and instant!"})

    # --- DYNAMIC RULES (Needs Database) ---
    try:
        # Check your folder name! If it is not 'home', change it to 'base' or 'main'
        from home.models import Job 
        
        if "job" in user_message or "count" in user_message:
            count = Job.objects.count()
            return JsonResponse({'response': f"We have {count} live job openings right now. Happy hunting!"})
            
    except Exception as e:
        # If the database part fails, we still give a general answer instead of crashing
        if "job" in user_message:
            return JsonResponse({'response': "We have many live jobs! Please check the 'Browse Jobs' section in the navigation bar."})

    # --- FALLBACK RULE ---
    return JsonResponse({'response': "I'm not sure about that. Try asking about 'jobs', 'signup', or 'payment'."})