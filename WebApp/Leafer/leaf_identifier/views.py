from django.shortcuts import redirect,render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Leaf
from .ml_utils import predict_image
from .functionality.statoc_trivia import trivia_data
from random import shuffle,sample
from django.conf import settings
from .Trivia import promptGen,QwenScraper as AI
from accounts.models import Score,UserProfile
import os
import shutil
from django.http import JsonResponse, HttpResponseRedirect,HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Leaf
import os
import shutil
import json
from django.conf import settings


from .functionality import statoc_trivia
from blogs.models import Notification
def home(request):
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user, read=False
        ).count()
    
    return render(request,"leaf_identifier/home.html", {
        'unread_notifications': unread_notifications
    })


def trivia(request):
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user, read=False
        ).count()
    static_trivia=sample(statoc_trivia.trivia_data,20)
    if request.method=='GET' and 'generate' in request.GET:
        prompt=promptGen.generate_trivia_prompt()

        try :
            output=AI.scrape_with_input()
        except:
            print("Enter prompt to the LLM :",prompt)
            print("---------------------------------------------------------------------")
            from .Trivia.Local_LLM_Zeph import generate_trivia
            import io
             
            lines = []
            trivia_string = generate_trivia(prompt)
            lines = [line.strip() for line in trivia_string.split('\n') if line.strip()]
            output=lines
        
        return render(request,"leaf_identifier/trivia.html",{"output":output,"triviaS":static_trivia,'unread_notifications': unread_notifications})


    return render(request,"leaf_identifier/trivia.html",{"triviaS":static_trivia,'unread_notifications': unread_notifications})


#add trivia, quizez and a blog maybe 
@login_required(login_url="login")
def upload(request):
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user, read=False
        ).count()
    if request.method=='POST':
        #maybe use a if conf less than smt reupload
        leaf_img=request.FILES.get('img')
        leaf = Leaf(img=leaf_img)  # Save without prediction first
        #here we create a Leaf without saving prediction and else 
        leaf.save()
        #after that we should update not create

        request.session['last_leaf_id'] = leaf.id 
        
        prediction_result=predict_image(leaf.img)
        #save the prediciton result in leaf directly 
        leaf.leaf_diagnose,leaf.confidence=prediction_result 
        leaf.confidence=int(leaf.confidence*100)
        #maybe use leaf_type for real so we can expand the site further more in the future while already having data in it
        # add a constraint so it shows a message and redirects if the image is less than 80 conf or smt  
        leaf.save()
        leaf.img.close()
        ###maybe clear session data after use ? 
        return redirect('result')
    return render(request,"leaf_identifier/upload_image.html",{"unread_notifications":unread_notifications})


#this will return the leaf data , prediciton and confidence of the prediciton
def result(request):
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user, read=False
        ).count()
    leaf_id=request.session.get('last_leaf_id')
    del request.session['last_leaf_id']
    leaf=Leaf.objects.get(id=leaf_id)
    return render(request,"leaf_identifier/result.html",{"leaf":leaf,"unread_notifications":unread_notifications})



def show_reports(request):
    return HttpResponse(request,"reports")

@login_required
def show_all(request):
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user, read=False
        ).count()
    if request.user.profile.role != "analyst":
        return redirect('home')

    leafs = Leaf.objects.all()
    diagnoses = [
        'bacterial_spot',
        'early_blight',
        'healthy',
        'late_blight',
        'powdery_mildew',
        'rust',
        'not_leaf',
    ]

    return render(request, "leaf_identifier/show_all.html", {
        "leafs": leafs,
        "diagnoses": diagnoses,"unread_notifications":unread_notifications
    })


@login_required
def move_image(request, id):
    if request.method == "POST":
        if not request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return HttpResponseRedirect("/show-all/")

        action = request.POST.get("action")
        if not action:
            return JsonResponse({"success": False, "message": "Action not provided."})

        leaf = get_object_or_404(Leaf, id=id)

        source_path = leaf.img.path
        leaf.img.close()

        if not os.path.exists(source_path):
            return JsonResponse({"success": False, "message": "Image file not found."})

        if action == "right":
            diagnosis = leaf.leaf_diagnose
        elif action == "correct_label":
            diagnosis = request.POST.get("diagnosis")
            if not diagnosis:
                return JsonResponse({"success": False, "message": "Diagnosis not provided."})
        else:
            return JsonResponse({"success": False, "message": "Invalid action."})

        data_dir = os.path.join(settings.BASE_DIR, 'Data')
        target_dir = os.path.join(data_dir, diagnosis)

        try:
            os.makedirs(target_dir, exist_ok=True)
            filename = os.path.basename(source_path)
            dest_path = os.path.join(target_dir, filename)
            shutil.move(source_path, dest_path)
            leaf.delete()
            return JsonResponse({
                "success": True,
                "message": f"Moved {filename} to Data/{diagnosis}/",
                "id": id
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error moving file: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request."})


import random
from .QuizzStuff import HardQuestions as HardQ
from .QuizzStuff import EasyQuestions as EasyQ
from .QuizzStuff import MidQuestions  as MidQ

@login_required
def quiz_home(request):
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user, read=False
        ).count()
    return render(request, 'leaf_identifier/quiz_form.html',{"unread_notifications":unread_notifications})


DIFFICULTY_SETTINGS = {
    'easy': {'questions': EasyQ.plant_questions, 'points': 3},
    'mid': {'questions': MidQ.plant_questions, 'points': 10},
    'hard': {'questions': HardQ.plant_questions, 'points': 20},
}
import random

@login_required
def run_quiz(request):
    
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user, read=False
        ).count()
    if request.method == 'POST':
        level = request.POST.get('level')

        #difficulty settings
        settings = DIFFICULTY_SETTINGS.get(level)
        if not settings:
            return redirect('quiz_home')

        all_questions = settings['questions']
        num_questions = 20

        # duplicate questions by question text
        seen = set()
        unique_questions = []
        for q in all_questions:
            question_key = q['question']  
            if question_key not in seen:
                seen.add(question_key)
                unique_questions.append(q)

        # do we have enough unique questions?
        if len(unique_questions) < num_questions:
            return render(request, 'leaf_identifier/quiz_error.html', {
                'error': f"Not enough unique {level} questions available ({len(unique_questions)} found, {num_questions} required)."
            ,"unread_notifications":unread_notifications})

        # Rndomly select 20 unique questions
        selected_questions = random.sample(unique_questions, num_questions)

        # Prepare quiz data
        quiz_data = []
        for idx, q in enumerate(selected_questions, 1):
            quiz_data.append({
                'question_number': idx,
                'question_text': q['question'],
                'answers': q['answers'],
                'correct_answer': q['correct_answer'],
            })

        # Save quiz data and level in session
        request.session['quiz_data'] = quiz_data
        request.session['quiz_level'] = level

        return render(request, 'leaf_identifier/quiz.html', {
            'quiz_data': quiz_data,"unread_notifications":unread_notifications
        })

    return redirect('quiz_home')

@login_required
def process_quiz(request):
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=request.user, read=False
        ).count()
    if request.method == 'POST':
        quiz_data = request.session.get('quiz_data', [])
        total_questions = len(quiz_data)
        score = 0
        results = []

        for i, q in enumerate(quiz_data):
            user_answer_key = request.POST.get(f'question_{i+1}')
            correct_answer_key = q['correct_answer']
            answers = q['answers']

            # Get answer texts
            user_answer_text = answers.get(user_answer_key, 'Not answered')
            correct_answer_text = answers.get(correct_answer_key, 'Unknown')

            is_correct = user_answer_key == correct_answer_key
            if is_correct:
                score += 1

            results.append({
                'question_number': q['question_number'],
                'question_text': q['question_text'],
                'user_answer_key': user_answer_key,
                'user_answer_text': user_answer_text,
                'correct_answer_key': correct_answer_key,
                'correct_answer_text': correct_answer_text,
                'is_correct': is_correct,
            })
        
        # Clear session data
        request.session.pop('quiz_data', None)
        
        score_obj, created = Score.objects.get_or_create(user=request.user, defaults={'total': 0})
        if request.session.get('quiz_level')=='easy':
            points=5
        elif request.session.get('quiz_level')=='mid':
            points=10
        elif request.session.get('quiz_level')=='hard':
            points=15
       

        if score >= 15:
            score_obj.total += points
            score_obj.save()
        
        return render(request, 'leaf_identifier/results.html', {
            'results': results,
            'score': score,
            'total': total_questions,
            'high_score': score >= 15,
            "unread_notifications":unread_notifications
        })


    return redirect('quiz_home')