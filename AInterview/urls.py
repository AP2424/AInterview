import django
from django.contrib import admin
from django.urls import path
from main.views import (CoursesMain, editor, profile, interview, loginmain, 
student_login, committee_login, start_interview, save_recording, save_start_time, applicantDashboard)
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', loginmain, name='login'),
    path('student-login/', student_login, name='student-login'),
    path('commitee-login/', committee_login, name='committee-login'),
    path('interviewEditor/', CoursesMain, name='courses'),
    path('interviewEditor/<str:code>/', editor, name='editor'),
    path('applicant/', applicantDashboard, name='dashboard'),
    path('interview/<int:pk>/', interview, name='interview'),
    path('interview/<int:pk>/start/', start_interview, name='start-interview'),
    path('profile/', profile, name='profile'),
    path('save-recording/', save_recording, name='save-recording'),
    path('save-start-time/', save_start_time, name='save-start-time'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)