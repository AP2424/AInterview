from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StudyProgram, InterviewModel, Question, User, Applicant, ConductedInterview, InterviewAnswer

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )

admin.site.register(StudyProgram)
admin.site.register(InterviewModel)
admin.site.register(Question)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Applicant)
admin.site.register(ConductedInterview)
admin.site.register(InterviewAnswer)