from django.urls import path
from .views import register_endpoint,logout_endpoint, login_endpoint

urlpatterns = [
    path('register/',register_endpoint , name='register'),
    path('login/', login_endpoint, name='login'),
    path('logout/',logout_endpoint,name='logout'),
]
