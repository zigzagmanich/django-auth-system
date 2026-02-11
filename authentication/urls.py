from django.urls import path
from authentication import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('me/', views.me_view, name='me'),
    path('me/', views.update_profile_view, name='update_profile'),
    path('me/delete/', views.delete_account_view, name='delete_account'),
    path('test-auth/', views.test_auth_view, name='test_auth'),
]