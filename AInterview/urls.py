import django
from django.contrib import admin
from django.urls import path
from main.views import CoursesMain, editor, applicantDashboard, interview, loginmain, student_login, committee_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', loginmain, name='login'),
    path('student-login/', student_login, name='student-login'),
    path('commitee-login/', committee_login, name='committee-login'),
    path('interviewEditor/', CoursesMain, name='courses'),
    path('interviewEditor/<str:code>/', editor, name='editor'),
    path('applicant/', applicantDashboard, name='dashboard'),
    path('interview/<int:pk>/', interview, name='interview')
]
