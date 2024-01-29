from django.http import HttpResponse
from django.shortcuts import render, redirect
from account.models import Account as BaseAccount
from blog.models import Poll, Post
from .forms import ResourceForm, UpdateResourceForm
from .models import Resource
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
import os
import cv2
import json
import base64
import requests
from django.core import files
from django.conf import settings
from django.contrib.auth.decorators import login_required
# Create your views here.

TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"

@login_required(login_url="login")
def resources_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	if not auth_user.is_authenticated:
		return redirect('login')
	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		try:
			resources = Resource.objects.all()		
			context['resources'] = resources
		except:
			return redirect("error", code=404)
	
	channel = get_create_update_channel(user=auth_user_account, view="resources")
	context["channel"] = channel
	context["con_general"] = True
	return render(request, "feature/resource/home.html", context)

@login_required(login_url="login")
def resource_view(request, *args, **kwargs):
	auth_user = request.user
	context = {}
	resource_id = kwargs.get("resource_id")
	if auth_user.is_authenticated:
		try:
			auth_user_account = BaseAccount.objects.get(username=auth_user.username)
			resource = Resource.objects.get(id=resource_id)
		except:
			return redirect("error:does_not_exist", origin="resources")

		if resource:
			context['resource'] = resource
		else:
			return redirect("unique:resources")
	
	channel = get_create_update_channel(user=auth_user_account, view="resources")
	context["channel"] = channel
	context["con_general"] = True
	return render(request, "feature/resource/details.html", context)

@login_required(login_url="login")
def create_resource_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	if not auth_user.is_authenticated:
		return redirect('login')
	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)

		if request.method == "POST" and request.POST:
			auth_user_account = BaseAccount.objects.get(username=auth_user.username)
			form = ResourceForm(request.POST)
			if form.is_valid():
				resource = form.save(commit=False)
				resource.author = auth_user_account
				resource.save()
				return redirect('feature:res_update', resource_id=resource.id)
			else:
				form = ResourceForm(request.POST)
				context['form'] = form
		else:
			context['form'] = ResourceForm

	channel = get_create_update_channel(user=auth_user_account, view="resources")
	context["channel"] = channel
	context["con_general"] = True
	return render(request, "feature/resource/create.html", context)

@login_required(login_url="login")
def update_resource_view(request, *args, **kwargs):

	context = {}
	auth_user = request.user
	resource_id = kwargs.get("resource_id")
	if not auth_user.is_authenticated:
		return redirect('login')
	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		resource = Resource.objects.get(id=resource_id)


		if request.method == "POST" and request.POST and resource_id:
			auth_user_account = BaseAccount.objects.get(username=auth_user.username)
			
			if resource:
				form = UpdateResourceForm(request.POST, request.FILES)
				if form.is_valid():
					print(request.POST)
					form.save(resource=resource, commit=True)
					return redirect('feature:res_details', resource_id=resource.id)
			else:
				form = UpdateResourceForm(request.POST)
				context['form'] = form
		else:
			context['form'] = UpdateResourceForm
	
	context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
	context['resource'] = resource
	channel = get_create_update_channel(user=auth_user_account, view="resources")
	context["channel"] = channel
	context["con_general"] = True
	return render(request, "feature/resource/update.html", context)

def save_temp_profile_image_from_base64String(imageString, resource):
	INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
	try:
		if not os.path.exists(settings.TEMP):
			os.mkdir(settings.TEMP)
		if not os.path.exists(settings.TEMP + "/" + str(resource.pk)):
			os.mkdir(settings.TEMP + "/" + str(resource.pk))
		url = os.path.join(settings.TEMP + "/" + str(resource.pk),TEMP_PROFILE_IMAGE_NAME)
		storage = FileSystemStorage(location=url)
		image = base64.b64decode(imageString)
		with storage.open('', 'wb+') as destination:
			destination.write(image)
			destination.close()
		return url
	except Exception as e:
		print("exception: " + str(e))
		# workaround for an issue I found
		if str(e) == INCORRECT_PADDING_EXCEPTION:
			imageString += "=" * ((4 - len(imageString) % 4) % 4)
			return save_temp_profile_image_from_base64String(imageString, resource)
	return None

@login_required(login_url="login")
def crop_image_view(request, *args, **kwargs):
	payload = {}
	auth_user = request.user
	resource_id = kwargs.get("resource_id")
	if resource_id != None:
		resource = Resource.objects.get(id=resource_id)

	if request.POST and auth_user.is_authenticated:
		try:
			imageString = request.POST.get("image")
			url = save_temp_profile_image_from_base64String(imageString, resource)
			img = cv2.imread(url)

			cropX = int(float(str(request.POST.get("cropX"))))
			cropY = int(float(str(request.POST.get("cropY"))))
			cropWidth = int(float(str(request.POST.get("cropWidth"))))
			cropHeight = int(float(str(request.POST.get("cropHeight"))))
			if cropX < 0:
				cropX = 0
			if cropY < 0: # There is a bug with cropperjs. y can be negative.
				cropY = 0
			crop_img = img[cropY:cropY+cropHeight, cropX:cropX+cropWidth]

			cv2.imwrite(url, crop_img)

			# delete the old image
			resource.image.delete()

			# Save the cropped image to user model
			resource.image.save("image.png", files.File(open(url, 'rb')))
			resource.save()

			payload['result'] = "success"
			payload['cropped_profile_image'] = resource.image.url

			# delete temp file
			os.remove(url)
			
		except Exception as e:
			print("exception: " + str(e))
			payload['result'] = "error"
			payload['exception'] = str(e)
	return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required(login_url="login")
def news_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	if not auth_user.is_authenticated:
		return redirect('login')
	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)

	return render(request, "feature/news/main.html",context)



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



