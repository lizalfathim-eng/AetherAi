"""
URL configuration for AetherAI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from myapp import views

urlpatterns = [
    path('loginpage_get/', views.loginpage_get),
    path('loginpage_post/', views.loginpage_post),
    path('logout_get/', views.logout_get),
    path('home_get/', views.home_get),
    path('new_home/', views.new_home),
    path('change_password_get/', views.change_password_get),
    path('change_password_post/', views.change_password_post),
    path('add_staff/', views.add_staff),
    path('add_staff_post/', views.add_staff_post),
    path('view_staff/', views.view_staff),
    path('view_more_staff/<id>', views.view_more_staff),

    path('delete_staff/<id>', views.delete_staff),
    path('edit_staff/<id>', views.edit_staff),
    path('edit_staff_post/', views.edit_staff_post),
    path('adm_view_complaint/', views.adm_view_complaint),
    path('send_reply/<id>', views.send_reply),
    path('send_reply_post/', views.send_reply_post),

    path('s_home_get/', views.s_home_get),
    path('staff_view_profile_get/', views.staff_view_profile_get),
    path('view_staff_more/<id>', views.view_staff_more),
    path('s_change_password_get/', views.s_change_password_get),
    path('s_change_password_post/', views.s_change_password_post),
    path('view_complaintreply_get/', views.view_complaintreply_get),
    path('sendcomplaint_admin_get/', views.sendcomplaint_admin_get),
    path('sendcomplaint_admin_post/', views.sendcomplaint_admin_post),
    path('upload_file/', views.upload_file),
    path('upload_file_post/', views.upload_file_post),
    path('view_upload_file/', views.view_upload_file),
    path('extract_content/<id>', views.extract_content),
    path('ask_question/', views.ask_question),
    path('ask_doubt/', views.ask_doubt),
    path('ask_question_post/', views.ask_question_post),
]