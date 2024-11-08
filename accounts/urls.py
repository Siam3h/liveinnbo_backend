from django.urls import re_path
from . import views


urlpatterns = [
    re_path('auth/signup/', views.signup),
    re_path('auth/login/', views.login),
    re_path('auth/logout/', views.logout),
    re_path('auth/test_token/', views.test_token),
    re_path('update_profile/', views.update_profile),
    re_path('delete_account/', views.delete_account)
]

