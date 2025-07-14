from django.urls import path
from ip_tracking import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
]