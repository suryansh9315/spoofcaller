from django.urls import path
from . import views

urlpatterns = [
    path('spam-report/', views.mark_spam , name='mark_spam'),
    path('search-by-name/',views.search_by_name, name='search_by_name'),
    path('search-by-number/',views.search_by_number, name='search_by_number'),
    path('spam-counter/', views.spam_counter, name="spam-counter"),
    path('display-detail/', views.display_detail, name="display-details"),
]
