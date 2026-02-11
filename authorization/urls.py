from django.urls import path
from authorization import views

app_name = 'authorization'

urlpatterns = [
    path('roles/', views.roles_list_view, name='roles_list'),
    path('roles/<int:pk>/', views.role_detail_view, name='role_detail'),
    path('roles/<int:pk>/access-rules/', views.role_access_rules_view, name='role_access_rules'),
    
    path('business-elements/', views.business_elements_list_view, name='business_elements_list'),
    path('business-elements/<int:pk>/', views.business_element_detail_view, name='business_element_detail'),
    
    path('access-rules/', views.access_rules_list_view, name='access_rules_list'),
    path('access-rules/<int:pk>/', views.access_rule_detail_view, name='access_rule_detail'),
]