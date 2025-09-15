"""
URL configuration for SmartWorkflowClub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from events import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Public pages
    path('', views.index, name='index'),
    path('home/', views.index, name='home'),

    # Authentication
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/club/', views.club_register, name='club_register'),


    #admin_pages
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('club/manage/', views.admin_club_manage, name='admin_club_manage'),
    path('event/manage/', views.admin_event_manage, name='admin_event_manage'),

    

    # Admin actions
    path('approve_event/<int:event_id>/', views.approve_event, name='approve_event'),
    path('reject_event/<int:event_id>/', views.reject_event, name='reject_event'),
    path('approve_club/<int:club_id>/', views.approve_club, name='approve_club'),
    path('suspend_club/<int:club_id>/', views.suspend_club, name='suspend_club'),


    #club
    path('club/dashboard/', views.club_dashboard, name='club_dashboard'),
    path('club/add_event/', views.add_event, name='add_event'),
    path('club/edit_event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('club/delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('club/manage/events/', views.manage_event, name='manage_event'),



    path('events/feedbacks/<int:id>/', views.feedbacks_view, name='feedbacks'),
    path('events/club_view_feedbacks/', views.club_view_feedbacks, name='club_view_feedbacks'),
    path('contact-messages/', views.view_contact_messages, name='view_contact_messages'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)