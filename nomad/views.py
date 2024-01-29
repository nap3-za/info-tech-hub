from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from account.models import BaseAccount
from .models import Question
from main_asgi.models import Notification

from .forms import FeedbackForm, QuestionForm

from .utils import get_create_update_channel
from account.utils import get_or_create_appdata


# Create your views here.


# Done
@login_required(login_url="login")
def send_feedback_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:
		auth_user_account = None
		try:
			auth_user_account = BaseAccount.objects.get(id=auth_user.id)
		except BaseAccount.DoesNotExist:
			return redirect("error", code=404)

		if request.method == "POST" and request.POST:
			form = FeedbackForm(request.POST)
			if form.is_valid():
				feedback = form.save(commit=False)
				feedback.author = auth_user_account
				feedback.save()
				return redirect("error", code=200)
			else:
				form = FeedbackForm(request.POST)
				context['form'] = form
		else:
			pass
	else:
		return redirect("home")

	context["con_general"] = True
	channel = get_create_update_channel(user=auth_user_account, view="send_feedback_form")
	context["channel"] = channel

	return render(request, "nomad/feedback/send_feedback.html", context)

# Done
@login_required(login_url="login")
def send_question_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	if not auth_user.is_authenticated:
		return redirect('login')
	elif auth_user.is_authenticated:
		auth_user_account = None
		try:
			auth_user_account = BaseAccount.objects.get(id=auth_user.id)
		except BaseAccount.DoesNotExist:
			return redirect("error", code=404)

		if request.method == "POST" and request.POST:
			form = QuestionForm(request.POST)
			if form.is_valid():
				question = form.save(commit=False)
				question.author = auth_user_account
				question.save()
				return redirect("nomad:questions")
			else:
				form = QuestionForm(request.POST)
				context['form'] = form
		else:
			pass

	context["con_general"] = True
	channel = get_create_update_channel(user=auth_user_account, view="send_question_form")
	context["channel"] = channel

	return render(request, "nomad/feedback/send_question.html", context)

# Done
@login_required(login_url="login")
def questions_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	if not auth_user.is_authenticated:
		return redirect('login')
	elif auth_user.is_authenticated:
		auth_user_account = None
		try:
			auth_user_account = BaseAccount.objects.get(id=auth_user.id)
		except:
			return redirect("error", code=404)

		questions = []
		try:
			questions = Question.objects.filter(author=auth_user_account).order_by('-timestamp')
		except Exception as e:
			print(f"[>> questions view : {e}")
			questions = []

		context['questions'] = questions

	context["con_general"] = True
	channel = get_create_update_channel(user=auth_user_account, view="questions")
	context["channel"] = channel
	return render(request, "nomad/feedback/questions.html", context)

# Done
@login_required(login_url="login")
def clear_questions_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:
		auth_user_account = None
		try:
			auth_user_account = BaseAccount.objects.get(id=auth_user.id)
		except BaseAccount.DoesNotExist:
			return redirect("error", code=404)


		try:
			questions = Question.objects.filter(author=auth_user_account)
			for question in questions:
				question.delete()
			return redirect("nomad:questions")

		except:
			return redirect("nomad:questions")
	return redirect("home")

# Done
@login_required(login_url="login")
def del_question_view(request, *args, **kwargs):
	auth_user = request.user

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:
		auth_user_account = None
		try:
			auth_user_account = BaseAccount.objects.get(id=auth_user.id)
			question_id = int(kwargs.get("question_id"))
		except:
			return redirect("error", code=404)

		try:
			if request.GET and request.GET.get("func") == "like":
				user_appdata = get_or_create_appdata(auth_user_account, 1)
				user_appdata.increment("positive_responses")
			elif request.GET and request.GET.get("func") == "dislike":
				user_appdata = get_or_create_appdata(auth_user_account, 1)
				user_appdata.increment("negative_responses")
			question = Question.objects.get(author=auth_user_account, id=question_id)
			question.delete()
			return redirect("nomad:questions")
		except:
			return redirect("error", code=404)
	else:
		return redirect("home")



