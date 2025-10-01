from django.urls import path
from . import views

urlpatterns = [
    path('delete-account/', views.delete_user_account, name='delete_user_account'),
    path('cached-list/', views.cached_message_list, name='cached_message_list'),
]