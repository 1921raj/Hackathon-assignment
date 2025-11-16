from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('competitors/', views.competitors_list, name='competitors'),
    path('competitors/add/', views.add_competitor, name='add_competitor'),
    path('competitors/<int:pk>/', views.competitor_detail, name='competitor_detail'),
    path('competitors/<int:pk>/config/', views.monitoring_config, name='monitoring_config'),
    path('updates/', views.updates_list, name='updates'),
    path('updates/<int:pk>/', views.update_detail, name='update_detail'),
    path('trends/', views.trends_list, name='trends'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('monitor/run/', views.run_monitoring, name='run_monitoring'),
]


