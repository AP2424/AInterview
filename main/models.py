from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password

class User(AbstractUser):
    ROLE_CHOICES = (
        ('applicant', 'Applicant'),
        ('commitee', 'Commitee Member'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def save(self, *args, **kwargs):
        if self._state.adding or not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


class StudyProgram(models.Model):
    STUDYLEVEL_CHOICES = (
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'))
    
    courseName = models.CharField(max_length=50)
    courseCode = models.CharField(max_length=10, unique=True)
    studyLevel = models.CharField(max_length=10, choices=STUDYLEVEL_CHOICES)
    courseDescription = models.TextField()
    courseLanguage = models.CharField(max_length=5)
    numberOfPlaces = models.IntegerField(default=0)
    coursePicture = models.ImageField(upload_to='course_pictures/', null=True, blank=True)
    def __str__(self):
        return f'{self.courseName}({self.courseCode})'


class Applicant(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='applicant')
    profilePicture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
class InterviewModel(models.Model):
    STATUS_CHOICES = (
        ('complete', 'Complete'),
        ('uncomplete', 'Uncomplete'))
    studyProgram = models.OneToOneField(StudyProgram, on_delete=models.SET_NULL, null=True, related_name="interviewModel")
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='uncomplete')
    
    
class Question(models.Model):
    TYPE_CHOICES = (
        ('factual', 'General Question'),
        ('knowledge', 'With right answer'))
    position = models.SmallIntegerField(default=0)
    questionText = models.CharField(max_length=500)
    type = models.CharField(max_length=12, choices=TYPE_CHOICES)
    maxTime = models.IntegerField(default=60, null=True) # maximum time allowed to answer in seconds
    answer = models.CharField(max_length=500, default='', null=True, blank=True)
    model = models.ForeignKey(InterviewModel, on_delete=models.CASCADE, default='')
    
    def __str__(self):
        return f"{self.position}: {self.questionText}"
  

class ConductedInterview(models.Model):
    STATUS_CHOICES = (
        ('complete', 'Complete'),
        ('in progress', 'In Progress'),)
    questions = models.ForeignKey(InterviewModel, on_delete=models.SET_NULL, null=True)
    applicant = models.ForeignKey(Applicant, on_delete=models.SET_NULL, null=True)
    startTime = models.DateTimeField(default=datetime.now)
    endTime = models.DateTimeField(default=datetime.now)
    recording = models.FileField(upload_to='videos/')
    score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0.0) # in a range from 0 to 10
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='in progress')

class InterviewAnswer(models.Model):
    interview = models.ForeignKey(ConductedInterview, on_delete=models.CASCADE)
    question_number = models.IntegerField(default=0)
    answer = models.CharField(max_length=1000, default='', null=True, blank=True)
    timeTaken = models.IntegerField(default=0)
    audio_response = models.FileField(upload_to='audio_responses/', null=True, blank=True)
    score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0.0) # in a range from 0 to 10
    model_comment = models.CharField(max_length=500, default='', null=True, blank=True)