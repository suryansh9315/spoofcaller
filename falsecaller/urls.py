# projectname/urls.py
from django.contrib import admin
from django.urls import path, include
from authentication.views import index 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),  
    path('api/',include('api.urls')),
    path('', index, name='index'),
]
