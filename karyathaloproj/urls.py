from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('karyathaloo.urls')),  # main app
    path('payment/', include(('payment.urls', 'payment'), namespace='payment')),  # payment app with namespace
]
