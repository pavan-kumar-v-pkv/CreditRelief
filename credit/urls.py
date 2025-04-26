from django.urls import path
from .views import RegisterUserView, ApplyLoanView, MakePaymentsView

urlpatterns = [
    path('register-user/', RegisterUserView.as_view(), name='register-user'),
    path('apply-loan/', ApplyLoanView.as_view(), name='apply-loan'),
    path('make-payment/', MakePaymentsView.as_view(), name='make-payment'),
]