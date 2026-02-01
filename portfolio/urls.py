from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # public
    path('', views.portfolio_index, name='home'),
    path('project/<slug:slug>/', views.project_detail, name='project_detail'),
    path('api/contact/', views.contact_api, name='contact_submit'),

    # custom admin panel
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/visitors/', views.admin_visitors, name='admin_visitors'),
    path('admin-panel/messages/', views.admin_messages, name='admin_messages'),
    path('admin-panel/updates/', views.admin_updates, name='admin_updates'),
]