from django.urls import path
from .views import RegisterUserView

urlpatterns = [
    path('register-user/', RegisterUserView.as_view(), name='register-user'),
]