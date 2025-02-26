from asyncio.windows_events import NULL
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import StudyProgram, InterviewModel, Question

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
    return render(request, 'main/dashboard.html', context={'programs': programs})

def interview(request, pk):
    program = StudyProgram.objects.get(id=pk)
    model = InterviewModel.objects.get(studyProgram=program)
    questions = model.questionsList.all()
    return render(request, 'main/interview.html', context={'questions': questions})
