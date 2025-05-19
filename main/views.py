import datetime
import json
from django.contrib.auth import login
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.core.files.base import ContentFile
from .models import ConductedInterview, InterviewAnswer
from .models import StudyProgram, InterviewModel, Question, User, Applicant
from .forms import ApplicantRegistrationForm
from together import Together
import whisper
import re
from dotenv import load_dotenv
import os
from django.conf import settings

load_dotenv()

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
    interview = ConductedInterview.objects.create(
        applicant=request.user.applicant,
        questions=model,
        startTime=timezone.now(),
        status='in progress'
    )
    return render(request, 'main/interview.html', context={'questions': serialized_questions})

def start_interview(request, pk):
    program = StudyProgram.objects.get(id=pk)
    model = InterviewModel.objects.get(studyProgram=program)
    questions = Question.objects.filter(model=model)
    time = round(sum(question.maxTime/60 for question in questions) + 2 + len(questions)*0.5) # introduction + question preparation minutes  
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
            status='in progress').last()
        interview.endTime = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        interview.status = 'complete'
        # Save the video file
        interview.recording.save(
            f'interview_{interview.id}.webm',
            ContentFile(video_file.read()),
            save=True
        )
        TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
        client = Together(api_key=settings.TOGETHER_API_KEY)
        questions = Question.objects.filter(model=interview.questions)
        print(questions.first(), questions.last())
        total_score = 0
        for question in questions:
            print(question.position)
            answer = InterviewAnswer.objects.get(interview=interview, question_number=question.position)
            if question.type == 'knowledge':
                prompt = f"""On the question: "{question.questionText}", student gave the answer: "{answer.answer}".
                Please rate the correctness of the answer on a scale from 0 to 10 with floating point, where 0 is the worst and 10 is the best, 
                taking into account the right answer provided by the teacher: "{question.answer}". Also, provide a comprehensive explanation of the score.
                The ChatCompletion response should be in the form of a JSON object with two fields: "score" and "explanation". 
                Expected output example: {{"score": 5, "explanation": "Your explanation of the score"}}.
                Prompt response must be only this JSON, without any additional text. Enclose JSON keys in double quotes."""
                response = client.chat.completions.create(
                    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", messages=[{"role": "user", "content": prompt}], max_tokens=500)
                
            elif question.type == 'factual':
                prompt = f"""On the question: "{question.questionText}", student gave the answer: "{answer.answer}".
                Please rate the answer on a scale from 0 to 10 with floating point, where 0 is the worst and 10 is the best. 
                For grading, take into account the meaningfulness of the answer, as well as the fluency of speech,
                and the logical structure of the answer. Also, provide a comprehensive explanation of the score. The ChatCompletion response should be in the form of a JSON object with two fields: "score" and "explanation". 
                Expected output example: {{"score": 5, "explanation": "your explanation of the score"}}.
                Prompt response must be only this JSON, without any additional text. Enclose JSON keys in double quotes."""
                response = client.chat.completions.create(
                    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", messages=[{"role": "user", "content": prompt}], max_tokens=500)
                
            try:
                response = response.choices[0].message.content
                print(f"Raw response: {response}")  # Debug log
                
                # Clean and sanitize the response
                response = response.strip()
                response = response.replace('\n', '')  # Remove newlines
                response = response.replace('\\', '')  # Remove escape characters
                #response = response.replace('"', "'")  # Replace double quotes with single quotes
                
                # Validate JSON structure
                if not (response.startswith('{') and response.endswith('}')):
                    raise ValueError("Invalid JSON structure")
                
                try:
                    resp_json = json.loads(response)
                except json.JSONDecodeError as json_err:
                    print(f"JSON parse error: {json_err}")
                    print(f"Problematic response: {response}")
                    # Attempt to fix common JSON issues
                    response = response.replace('}.', '}')  # Remove trailing period
                    response = re.sub(r',\s*}', '}', response)  # Remove trailing comma
                    resp_json = json.loads(response)
                
                # Validate required fields
                if not all(key in resp_json for key in ['score', 'explanation']):
                    raise ValueError("Missing required fields in response")
                
                answer_score = float(resp_json['score'])
                # Ensure score is within bounds
                answer_score = max(0, min(10, answer_score))
                model_explanation = resp_json['explanation']
                
                answer.model_comment = model_explanation
                answer.score = answer_score
                answer.save()
                total_score += answer_score
            
            except Exception as e:
                print(f"Error processing response: {e}")
                # Fallback values in case of error
                answer.score = 5.0
                answer.model_comment = "Error processing response"
                answer.save()
                total_score += 5.0
        interview.score = total_score / len(questions)
        interview.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
def save_start_time(request):
    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        
        # Convert ISO string to datetime
        start_datetime = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def save_audio_chunk(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        question_id = request.POST.get('question_id')
        interview = ConductedInterview.objects.filter(
            applicant=request.user.applicant,
            status='in progress').last()
        obj, created = InterviewAnswer.objects.get_or_create(
                interview=interview,
                question_number=question_id)
        obj.audio_response.save(
                f'question_{question_id}.webm',
                ContentFile(audio_file.read()),
                save=True)
        model = whisper.load_model("base.en")
        transcription = model.transcribe(obj.audio_response.path)
        """print(obj.audio_response.path)
        with open(obj.audio_response.path, 'rb') as audio:
                client = InferenceClient(
                    provider="hf-inference",
                    model="openai/whisper-large-v3-turbo", 
                    token=,
                    headers={"Content-type": "audio/webm"}
                )
                # Pass the binary audio data directly
                audio_data = audio.read()
                transcription = client.automatic_speech_recognition(
                    audio_data
                )"""
        obj.answer = transcription['text']
        obj.save()
        print(obj.answer)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def ranking(request):
    interviews = ConductedInterview.objects.filter(status='complete').order_by('-score')
    return render(request, 'main/ranking.html', context={'interviews': interviews})

def score_breakdown(request, interview_id):
    interview = get_object_or_404(ConductedInterview, id=interview_id)
    answers = InterviewAnswer.objects.filter(interview=interview).order_by('question_number')
    questions = Question.objects.filter(model=interview.questions)
    
    # Combine questions and answers
    qa_pairs = []
    for answer in answers:
        question = questions.get(position=answer.question_number)
        qa_pairs.append({
            'question': question,
            'answer': answer
        })
    
    return render(request, 'main/score_breakdown.html', {
        'interview': interview,
        'qa_pairs': qa_pairs
    })


def register(request):
    if request.method == 'POST':
        form = ApplicantRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create User instance
            user = form.save(commit=False)
            user.role = 'applicant'
            user.save()
            
            # Create Applicant instance
            applicant = Applicant.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                surname=form.cleaned_data['surname'],
                profilePicture=form.cleaned_data.get('profile_picture')
            )
            
            # Log the user in
            login(request, user)
            return redirect('dashboard')
    else:
        form = ApplicantRegistrationForm()
    
    return render(request, 'main/register.html', {'form': form})