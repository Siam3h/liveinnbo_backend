from django.urls import path
from . import views

urlpatterns = [
    path('process/<int:event_id>/', views.process_payment, name='process-payment'),
    path('verify_payment/', views.verify_payment, name='verify-payment'),
    path('thankyou/<int:transaction_id>/', views.thankyou, name='thankyou'),
]
