from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Your main app URLs
    path('', include('karyathaloo.urls')),
    path("chatbot/", include("chatbot.urls")),
    

    
    


   




]
