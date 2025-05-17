from asyncio.windows_events import NULL
import datetime
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.core.files import File
from django.core.files.base import ContentFile
from .models import ConductedInterview
from .models import StudyProgram, InterviewModel, Question, User

def CoursesMain(request):
    programs = StudyProgram.objects.all()
    return render(request, 'main/programs.html', context={'programs': programs})

@csrf_exempt
def editor(request, code):
    program = StudyProgram.objects.get(courseCode=code)
    model, created = InterviewModel.objects.get_or_create(studyProgram=program)
    questions = Question.objects.filter(model=model).order_by('position')
    if request.method == "POST":
        data = request.POST
        index = 1
        print(data)
        while f'question_{index}' in data or questions.filter(position=index):
            if questions.filter(position=index) and not f'question_{index}' in data:
               questions_below = questions.filter(position__gt=questions[index-1].position)
               for q in questions_below:
                   q.position -= 1
                   q.save()
                   print(q.questionText, q.position)
               questions[index-1].delete()
               print("deleted")
               break
            else:
                question = data.get(f'question_{index}')
                maxtime = data.get(f'maxtime_{index}')
                type_checked = data.get(f'qtype_{index}')
                answer = data.get(f'answer_{index}')
                form_data = {
                    "position": index,
                    "questionText": question,
                    "type": type_checked,
                    "maxTime": maxtime,
                    "answer": answer
                }   
                obj, created = Question.objects.update_or_create(
                    position=index, model=model, defaults=form_data, create_defaults=form_data)
                obj.save()
                print(created)
            index += 1
        if request.POST.get('complete') == 'yes':
            print(11)
            model.status = 'complete'
            model.save()
        return JsonResponse({"status": "success"})
    return render(request, 'main/editor.html', context={'program': program, 'questions': questions})

def applicantDashboard(request):
    programs = StudyProgram.objects.all()
    completed_interviews = ConductedInterview.objects.filter(
        applicant=request.user.applicant, status='complete').values_list('questions__studyProgram_id', flat=True)
    
    return render(request, 'main/dashboard.html', 
                  context={'programs': programs,
                  'completed_interviews': list(completed_interviews)})

def interview(request, pk):
    program = StudyProgram.objects.get(id=pk)
    model = InterviewModel.objects.get(studyProgram=program)
    questions = Question.objects.filter(model=model).order_by('position')
    serialized_questions = serialize('json', questions)
    return render(request, 'main/interview.html', context={'questions': serialized_questions})

def start_interview(request, pk):
    program = StudyProgram.objects.get(id=pk)
    model = InterviewModel.objects.get(studyProgram=program)
    questions = Question.objects.filter(model=model)
    time = round(sum(question.maxTime/60 for question in questions) + 5) # introduction minutes
    return render(request, 'main/start_interview.html', context={'program': program, 'questions_num': questions.count(),
                                                                 'time': time})

def loginmain(request):
    return render(request, 'main/loginmain.html')

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None and user.role == 'applicant':
            login(request, user)
            return HttpResponseRedirect(reverse('start-interview', args=[user.applicant.studyProgram.id]))
        else:
            return render(request, 'main/studentlogin.html', {'error': 'Invalid credentials'})
    return render(request, 'main/studentlogin.html')

def committee_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None and user.role == 'commitee':
            login(request, user)
            return HttpResponseRedirect(reverse('interviewEditor'))
        else:
            return render(request, 'main/committeelogin.html', {'error': 'Invalid credentials'})
    return render(request, 'main/committeelogin.html')

def profile(request):
    user = User.objects.get(username=request.user.username)
    return render(request, 'main/profile.html', context={'applicant': user.applicant})

@csrf_exempt
def save_recording(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        end_time = request.POST.get('end_time')
        # Get or create ConductedInterview instance
        interview = ConductedInterview.objects.filter(
            applicant=request.user.applicant,
            status='in progress').first()
        interview.endTime = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        interview.status = 'complete'
        # Save the video file
        interview.recording.save(
            f'interview_{interview.id}.webm',
            ContentFile(video_file.read()),
            save=True
        )
        interview.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def save_start_time(request):
    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        
        # Convert ISO string to datetime
        start_datetime = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        # Create new interview instance with exact start time
        interview = ConductedInterview.objects.create(
            applicant=request.user.applicant,
            questions=InterviewModel.objects.get(studyProgram=request.user.applicant.studyProgram),
            startTime=start_datetime,
            status = 'in progress',
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)