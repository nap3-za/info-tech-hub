import os
import cv2
import json
import base64
import requests
import random

from django.core import files
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.conf import settings

from account.models import Account
from main_asgi.models import Notification, PrivateChatMessage, PrivateChatRoom
from account.utils import create_or_update_settings

TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"

class HomeView(generic.TemplateView):
	
	template_name = "main/home.html"

	def get(self, request, *args, **kwargs):
		context = {}
		if request.user.is_authenticated:
			context = {}
			auth_user_account = get_object_or_404(Account, pk=request.user.id)
			context["con_general"] = True
			context["channel_id"] = create_or_update_settings(auth_user_account, "home").id
			context['noti_count'] = len(Notification.objects.filter(target=auth_user_account, read=False))
			context['msg_count'] = len([ room.message_set.filter(read=False) for room in PrivateChatRoom.objects.filter(user1=auth_user_account)]) + len([ room.message_set.filter(read=False) for room in PrivateChatRoom.objects.filter(user2=auth_user_account)])
			
			context['welcome_msg'] = random.choice([
				'Welcome back ',
				'We\'ve missed you ',
				'Good to have you back ',
				'Now that you\'re back ',
				'Thanks for gracing us with your precense ',
				'Sup ',
			])


		return render(request, self.template_name, context)

class AboutView(generic.TemplateView):
	
	template_name = "main/about.html"

	def get(self, request, *args, **kwargs):
		context = {}
		if request.user.is_authenticated:
			context = {}
			# auth_user_account = get_object_or_404(Account, pk=request.user.id)
			# context["con_general"] = True
			# channel = get_create_update_channel(user=auth_user_account, view="about")
			# context["channel"] = channel
		return render(request, self.template_name, context)

class ContactView(generic.TemplateView):
	
	template_name = "main/contact.html"

	def get(self, request, *args, **kwargs):
		context = {}
		context["whatsapp_link"] = settings.WHATSAPP_LINK
		context["telegram_link"] = settings.TELEGRAM_LINK
		context["phone_number"] = settings.PHONE_NUMBER
		context["email"] = settings.EMAIL_HOST
		context["physical_address"] = settings.PHYSICAL_ADDRESS
		if request.user.is_authenticated:
			# auth_user_account = get_object_or_404(Account, pk=request.user.id)
			context["con_general"] = True
			# channel = get_create_update_channel(user=auth_user_account, view="home")
			# context["channel"] = channel
			# context['noti_count'] = len(Notification.objects.filter(target=auth_user_account, read=False))
			# context['msg_count'] = len(PrivateChatMessage.objects.filter(room.user1==auth_user_account, seen=False)) + len(PrivateChatMessage.objects.filter(room.user2==auth_user_account, seen=False))
		return render(request, self.template_name, context)

class LegalDocsView(generic.TemplateView):
	
	template_name = "main/legal_docs.html"

	def get(self, request, *args, **kwargs):
		context = {}
		if request.user.is_authenticated:
			context = {}

			# auth_user_account = get_object_or_404(BaseAccount, pk=request.user.id)
			# context["con_general"] = True
			# channel = get_create_update_channel(user=auth_user_account, view="legal_docs")
			# context["channel"] = channel
		return render(request, self.template_name, context)


def save_temp_profile_image_from_base64String(imageString, user):
	INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
	try:
		if not os.path.exists(settings.TEMP):
			os.mkdir(settings.TEMP)
		if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
			os.mkdir(settings.TEMP + "/" + str(user.pk))
		url = os.path.join(settings.TEMP + "/" + str(user.pk),TEMP_PROFILE_IMAGE_NAME)
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
			return save_temp_profile_image_from_base64String(imageString, user)
	return None

def crop_image_view(request, *args, **kwargs):
	payload = {}
	user = request.user
	if request.POST and user.is_authenticated:
		try:
			imageString = request.POST.get("image")
			url = save_temp_profile_image_from_base64String(imageString, user)
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
			user.profile_image.delete()

			# Save the cropped image to user model
			user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
			user.save()

			payload['result'] = "success"
			payload['cropped_profile_image'] = user.profile_image.url

			# delete temp file
			os.remove(url)
			
		except Exception as e:
			print("exception: " + str(e))
			payload['result'] = "error"
			payload['exception'] = str(e)
	return HttpResponse(json.dumps(payload), content_type="application/json")


def page_not_found_view(request, *args, **kwargs):
	return render(request, "errors/404.html")	

def perm_denied_view(request, *args, **kwargs):
	return render(request, "errors/403.html")	

def server_error_view(request, *args, **kwargs):
	return render(request, "errors/500.html")	

def bad_request_view(request, *args, **kwargs):
	return render(request, "errors/400.html")	

def dummy_view(request, *args, **kwargs):
	return HttpResponse("<h1 class='text-center serif'>Still in construction </h1>")
