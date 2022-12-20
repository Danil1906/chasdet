from django.urls import path
from .views import *



urlpatterns = [
    path('register/', register, name='register'),
    path('promocode/', auth_promo, name='auth_promo'),
    path('verify_email/<uidb64>/<token>/', EmailVerify.as_view(), name='verify_email'),
    # path('register/promo', register, name='register-promo'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]