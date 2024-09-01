from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import random
from psycopg2.sql.SQL import string

from Multiplayer.models import QuizSession, Question, Answer, PlayerAnswer


# Create your views here.

@login_required
def create_quiz_session(request):
    if request.method == 'POST':
        session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        session = QuizSession.objects.create(
            code=session_code,
            host=request.user,
        )
        session.participants.add(request.user)
        return render(request, 'multiplayer/quiz_session_lobby.html', {'session': session})
    return render(request, 'multiplayer/create_quiz_session.html')

@login_required
def join_quiz_session(request):
    if request.method == 'POST':
        session_code = request.POST['session_code']
        session = get_object_or_404(QuizSession, code=session_code)
        session.participants.add(request.user)
        return render(request, 'multiplayer/quiz_session_lobby.html', {'session': session})
    return render(request, 'multiplayer/join_quiz_session.html')

@login_required
def start_quiz_session(request, session_code):
    session = get_object_or_404(QuizSession, code=session_code)
    question = Question.objects.filter(quiz_pool=session.hosted_quiz_pool).first()
    if question:
        return render(request, 'multiplayer/quiz_question.html', {
            'session': session,
            'question': question,
        })
    return redirect('quiz_session_results', session_code=session_code)

@login_required
def submit_answer(request, session_code, question_id):
    session = get_object_or_404(QuizSession, code=session_code)
    question = get_object_or_404(Question, id=question_id)
    answer_id = request.POST.get('answer')
    answer = get_object_or_404(Answer, id=answer_id)

    is_correct = answer.is_correct
    PlayerAnswer.objects.create(
        session=session,
        player=request.user,
        question=question,
        answer=answer,
        is_correct=is_correct,
    )
    next_question = Question.objects.filter(quiz_pool=session.hosted_quiz_pool, number__gt=question.number).first()
    if next_question:
        return render(request, 'multiplayer/quiz_question.html', {
            'session': session,
            'question': next_question,
        })
    return redirect('quiz_session_results', session_code=session_code)
def create_quiz_session(request):
    if request.method == 'POST':
        session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        session = QuizSession.objects.create(
            code=session_code,
            host=request.user,
        )
        session.participants.add(request.user)
        session.save()
        return render(request, 'multiplayer/quiz_session_lobby.html', {'session': session})
    return render(request, 'multiplayer/create_quiz_session.html')


def join_quiz_session(request):
    if request.method == 'POST':
        session_code = request.POST['session_code']
        try:
            session = QuizSession.objects.get(code=session_code)
            session.participants.add(request.user)
            session.save()
            return render(request, 'multiplayer/quiz_session_lobby.html', {'session': session})
        except QuizSession.DoesNotExist:
            messages.error(request, 'Invalid session code.')
            return render(request, 'multiplayer/join_quiz_session.html')
    return render(request, 'multiplayer/join_quiz_session.html')


def start_quiz_session(request, session_code):
    session = QuizSession.objects.get(code=session_code)
    question = Question.objects.filter(quiz_pool=session.hosted_quiz_pool).first()

    if question:
        return render(request, 'multiplayer/quiz_question.html', {
            'session': session,
            'question': question,
        })
    return redirect('quiz_session_results', session_code=session_code)


def quiz_session_results(request, session_code):
    session = QuizSession.objects.get(code=session_code)
    results = PlayerAnswer.objects.filter(session=session)

    return render(request, 'multiplayer/quiz_session_result.html', {
        'session': session,
        'results': results,
    })