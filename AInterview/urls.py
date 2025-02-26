import django
from django.contrib import admin
from django.urls import path
from main.views import CoursesMain, editor, applicantDashboard, interview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('interviewEditor/', CoursesMain, name='courses'),
    path('interviewEditor/<str:code>/', editor, name='editor'),
    path('applicant/', applicantDashboard, name='dashboard'),
    path('interview/<int:pk>/', interview, name='interview')
]
