import os
import cv2
import json
import base64
import requests

from django.core import files
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.views import View
from django.utils.decorators import method_decorator

from .forms import (
	RegistrationForm,
	ProfileSetupForm,
	UpdateSettingsForm,
	AuthenticationForm,
	UpdateAccountForm,
	DeleteAccountForm,
	LockForm,
	
	)

from .models import Account
from blog.models import Post, Poll, Content, PollValue, Comment
from friend.models import FriendList, FriendRequest
from feature.models import Question
# from feature.models import Resource
from friend.friend_request_status import FriendRequestStatus
from friend.utils import get_friend_request_or_false
# from main_asgi.models import Notification, UserChannel

from .utils import get_or_create_appdata, get_or_create_frlist, create_or_update_settings


# Create your views here.

TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"


class RegisterView(View):

	form_class = RegistrationForm
	initial = {}
	template_name = "account/register.html"

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect("home")
		return render(request, self.template_name, {"con_general": False})
	def post(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect("home")

		form = self.form_class(request.POST)
		print([[error for error in field.errors] for field in form])
		if form.is_valid():
			auth_user_account = form.save()
			login(request, auth_user_account)
			try:
				get_or_create_frlist(auth_user_account)
				get_or_create_appdata(auth_user_account)
				create_or_update_settings(user=auth_user_account, state="redirect")
			except Exception as e:
				print(str(e))
				return redirect("500")
			return redirect("account:redirect")
		else:
			return render(request, self.template_name, {'form':form, "con_general": False})

@login_required(login_url="login")
def redirect_view(request, *args, **kwargs):
	context = {}
	return render(request, "account/redirect.html", context)

class LoginView(View):
	form_class = AuthenticationForm
	initial = {}
	template_name = "account/login.html"

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {"con_general": False})
	def post(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect("home")

		form = self.form_class(request.POST)
		print([[error for error in field.errors] for field in form])
		if form.is_valid():
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']
			try:
				auth_user_account = authenticate(email=email, password=password)
			except:
				return redirect("400")

			if auth_user_account != None and auth_user_account.is_active:
				login(request, auth_user_account)
				return redirect("blog:feed")
			else:
				return redirect("404")
		else:
			return render(request, self.template_name, {'form':form, "con_general": False})

@login_required(login_url="login")
def logout_view(request):
	logout(request)
	return redirect("login")

@method_decorator(login_required(login_url="login"), name="dispatch")
class ProfileSetupView(View):

	form_class = ProfileSetupForm
	initial = {}
	template_name = "account/setup_profile.html"

	def get(self, request, *args, **kwargs):
		context = {}
		auth_user_account = get_object_or_404(Account, pk=request.user.pk)
		if auth_user_account.settings.account_setup:
			return redirect("home")
		context["channel_id"] = create_or_update_settings(user=auth_user_account, state="account_setup_form")
		context["con_general"] = True
		context["DATA_UPLOAD_MAX_MEMORY_SIZE"] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
		return render(request, self.template_name, context)
	
	def post(self, request, *args, **kwargs):
		context = {}
		auth_user_account = get_object_or_404(Account, pk=request.user.pk)
		if auth_user_account.settings.account_setup:
			return redirect("home")
		form = self.form_class(request.POST, request.FILES, instance=auth_user_account)
		if form.is_valid():
			form.save(instance=auth_user_account)
			return redirect("account:update_settings")
		else:
			context["channel_id"] = create_or_update_settings(user=auth_user_account, state="account_setup_form")
			context["con_general"] = True
			context["form"] = form
			context["DATA_UPLOAD_MAX_MEMORY_SIZE"] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
			return render(request, self.template_name, context)

@method_decorator(login_required(login_url="login"), name="dispatch")
class UpdateSettingsView(View):

	form_class = UpdateSettingsForm
	initial = {}
	template_name = "account/update_settings.html"

	def get(self, request, *args, **kwargs):
		context = {}
		auth_user_account = get_object_or_404(Account, pk=request.user.pk)
		if not auth_user_account.settings.settings_setup:
			context["setup"] = True
		context["channel_id"] = create_or_update_settings(user=auth_user_account, state="settings_update_form")
		context["con_general"] = True
		return render(request, self.template_name, context)
	
	def post(self, request, *args, **kwargs):
		context = {}
		auth_user_account = get_object_or_404(Account, pk=request.user.pk)
		if auth_user_account.settings.settings_setup:
			return redirect("home")
		form = self.form_class(request.POST, instance=auth_user_account)
		print([[error for error in field.errors] for field in form])
		if form.is_valid():
			form.save(instance=auth_user_account)
			auth_user_account.settings.settings_setup = True
			auth_user_account.settings.save()
			return redirect("account:details", subject_username=auth_user_account.username)
		else:
			context["channel_id"] = create_or_update_settings(user=auth_user_account, state="settings_update_form")
			context["con_general"] = True
			context["form"] = form
			return render(request, self.template_name, context)

@method_decorator(login_required(login_url="login"), name="dispatch")
class UpdateAccountView(View):

	form_class = UpdateAccountForm
	initial = {}
	template_name = "account/update.html"

	def get(self, request, *args, **kwargs):
		context = {}
		auth_user_account = get_object_or_404(Account, pk=request.user.pk)
		
		context["channel_id"] = create_or_update_settings(user=auth_user_account, state="account_update_form")
		context["con_general"] = True
		context["DATA_UPLOAD_MAX_MEMORY_SIZE"] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
		
		return render(request, self.template_name, context)
	
	def post(self, request, *args, **kwargs):
		context = {}
		auth_user_account = get_object_or_404(Account, pk=request.user.pk)
		
		form = self.form_class(request.POST, request.FILES, instance=auth_user_account)
		if form.is_valid():
			form.save(instance=auth_user_account)
			return redirect("account:update")
		else:
			context["channel_id"] = create_or_update_settings(user=auth_user_account, state="account_update_form")
			context["con_general"] = True
			context["DATA_UPLOAD_MAX_MEMORY_SIZE"] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
			context["form"] = form
			return render(request, self.template_name, context)

@method_decorator(login_required(login_url="login"), name="dispatch")
class DeleteAccountView(View):

	form_class = DeleteAccountForm
	initial = {}
	template_name = "account/delete.html"

	def get(self, request, *args, **kwargs):
		context = {}
		auth_user_account = get_object_or_404(Account, pk=request.user.pk)
		
		context["channel_id"] = create_or_update_settings(user=auth_user_account, state="account_setup_form")
		context["con_general"] = True
		
		return render(request, self.template_name, context)
	def post(self, request, *args, **kwargs):
		context = {}
		auth_user_account = get_object_or_404(Account, pk=request.user.pk)
		
		form = self.form_class(request.POST)
		print([[error for error in field.errors] for field in form])
		if form.is_valid():
			form.save(instance=auth_user_account)
			return redirect("login")
		else:
			context["channel_id"] = create_or_update_settings(user=auth_user_account, state="account_setup_form")
			context["con_general"] = True
			context["form"] = form
			return render(request, self.template_name, context)

@method_decorator(login_required(login_url="login"), name="dispatch")
class DetailsView(View):

	template_name = "account/details.html"

	def get(self, request, *args, **kwargs):
		context = {}
		auth_user_account = get_object_or_404(Account, pk=request.user.pk)

		subject_account = get_object_or_404(Account, username=kwargs.get("subject_username"))
		context["subject"] = subject_account
		if subject_account == auth_user_account:
			context["con_general"] = False
			context["channel_id"] = create_or_update_settings(auth_user_account, "self_details_view").id
		else:
			context["con_general"] = True
			context["channel_id"] = create_or_update_settings(auth_user_account, "details_view").id
		
		if subject_account.settings.featured != None:
			context["featured"] = (subject_account.settings.featured)

		if subject_account.github or subject_account.stack or subject_account.insta or subject_account.youtube:
			context["has_social_links"] = True
		else:
			context["has_social_links"] = False
		
		# Define template variables
		is_self = True
		is_friend = False
		request_sent = FriendRequestStatus.NO_REQUEST_SENT.value # range: ENUM -> friend/friend_request_status.FriendRequestStatus

		if auth_user_account == subject_account:
			context['show_title'] = True
			is_friend = False 
			is_self = True
			try:
				friend_list = get_or_create_frlist(subject_account)
				context['friends'] = friend_list.friends.all()
				context["fr_count"] = len(FriendRequest.objects.filter(receiver=auth_user_account, is_active=True)) 			
			except Exception as e:
				print(f"[ >> ERROR 01:Detail : {e}")
				friend_requests = None

			context["q_count"] = len(Question.objects.filter(author=subject_account))

		elif auth_user_account != subject_account:

			is_self = False
			if auth_user_account.friends.filter(pk=auth_user_account.id):
				is_friend = True
			else:
				is_friend = False
				# CASE1: Request has been sent from THEM to YOU: FriendRequestStatus.THEM_SENT_TO_YOU
				if get_friend_request_or_false(sender=subject_account, receiver=auth_user_account) != False:
					request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
					print(get_friend_request_or_false(sender=subject_account, receiver=auth_user_account))
					context['pending_fr'] = get_friend_request_or_false(sender=subject_account, receiver=auth_user_account).id
				# CASE2: Request has been sent from YOU to THEM: FriendRequestStatus.YOU_SENT_TO_THEM
				elif get_friend_request_or_false(sender=auth_user_account, receiver=subject_account) != False:
					request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
				# CASE3: No request sent from YOU or THEM: FriendRequestStatus.NO_REQUEST_SENT
				else:
					request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

			if subject_account.settings.friend_list_visi == "Anyone" or (subject_account.settings.friend_list_visi == "Friends" and is_friend):
				context['friends'] = get_or_create_frlist(subject_account).friends.all()


		# Contents config
		if is_self or (subject_account.settings.timeline_visi == "Friends" and is_friend) or (subject_account.settings.timeline_visi == "Anyone") and is_friend:
			contents = []
			try:
				contents = Content.objects.filter(is_active=True, author=subject_account, draft=False).order_by('-timestamp')
			except Exception as e:
				return redirect("404")

			contents_list = []
			for content in contents:
				comments = []
				for comment in list(Comment.objects.filter(content=content, is_active=True, is_reply=False).order_by('-timestamp')[:5]):
					c_is_mine = None
					if comment.author == auth_user_account:
						c_is_mine = True
					else:
						c_is_mine = False
					replies = []
					if len(comment.replies.all()) > 0:
						replies_objs = comment.replies.all().filter(is_active=True)
						for reply in replies_objs:
							replies.append(reply)
					comments.append((comment, c_is_mine, replies))

				contents_list.append((content, comments, comment_count))
			
			if len(contents) >= 1:
				context["recent_act"] = (list(contents)[0])			

			# Pagination system required
			context['contents'] = contents_list[0:6]
		else:
			pass

		context['is_self'] = is_self
		context['is_friend'] = is_friend
		context['request_sent'] = request_sent
		return render(request, self.template_name, context)

@method_decorator(login_required(login_url="login"), name="dispatch")
class SearchAccountView(View):

	template_name = "account/search.html"

	def post(self, request, *args, **kwargs):
		context = {}
		auth_user_account = get_object_or_404(Account, pk=request.user.pk)
		search_query = request.POST.get("search_query").lower()
		if len(search_query > 1):
			if request.POST:
				accounts = Account.objects.filter(is_active=True, username__icontains=search_query)
				friend = False 
				continents = [
					"Africa",
					"Antarctica",
					"Greenland",
					"North America",
					"South America",
					"Europe",
					"Australia",
					"Asia",
					"New Zealand",
				]
				try:
					flags = request.POST.get("flags")
					
					if flags["friend"] == 1:
						for account in accounts:
							if not account in auth_user_account.friends.all():
								accounts.remove(account)
							else:
								pass

					if flags["continent"] != "None" and flags["continent"] in continents:
						accounts = accounts.filter(continent=flags["continent"])
						for account in accounts:
							if account.settings.location_search == False:
								accounts.remove(account)
							else:
								pass				

					context["accounts"] = accounts

				except Exception as e:
					print(f"[>> search : {str(e)}")

			# elif request.POST.get("search_type") == "contents":
			# 	by_friend = False 
			# 	contents = Content.objects.filter(is_active=True)
			# 	try:

			# 		for content in contents:
			# 			if content.kind == "Post":
			# 				if (content.title and search_query in content.title.lower()) or (search_query in content.post.text.lower()):
			# 					pass
			# 				else:
			# 					contents.remove(content)
			# 			elif content.kind == "Poll":
			# 				if (content.title and search_query in content.title.lower()) or (search_query in "".join([poll_val.value for poll_val in content.poll.poll_values])):
			# 					pass
			# 				else:
			# 					contents.remove(content)

			# 		flags = request.POST.get("flags")
			# 		if flags["friend"] == 1:
			# 			for account in accounts:
			# 				if not content.author in auth_user_account.friends.all():
			# 					contents.remove(content)
			# 				else:
			# 					pass
					
			# 		if flags["type"]:
			# 			content_type = flags["type"]
			# 			if content_type == "poll":
			# 				contents.filter(kind="Poll")
			# 			elif content_type == "post":
			# 				contents.filter(kind="Post")

			# 		if flags["recent"] == 1:
			# 			for content in contents:
			# 				if not content.was_published_recently():
			# 					contents.remove(content)
			# 				else:
			# 					pass
					
			# 		categories = ["Operating Systems", "Programming", "School", "Hardware", "Software"]
			# 		if flags["category"] and flags["category"] in categories:
			# 			contents.filter(category=flags["category"])

			# 		context["contents"] = contents

			# 	except Exception as e:
			# 		print(f"[>> content search : {str(e)}")
			
			# elif request.POST.get("search_type") == "resources":
			# 	by_friend = False 
			# 	resources = Resource.objects.all()
			# 	try:
			# 		for resource in resources:
			# 			if search_query in resource.title.lower() or search_query in resource.description.lower():
			# 				pass
			# 			else:
			# 				resources.remove(resource)

			# 		flags = request.POST.get("flags")
			# 		if flags["friend"] == 1:
			# 			for resource in resources:
			# 				if not resource.author in auth_user_account.friends.all():
			# 					resources.remove(resource)
			# 				else:
			# 					pass

			# 		if flags["type"]:
			# 			res_type = flags["type"]
			# 			if res_type == "article":
			# 				resources.filter(kind="Article")
			# 			elif res_type == "video":
			# 				resources.filter(res_format="Video")
			# 			elif res_type == "audio":
			# 				resources.filter(res_format="Audio")
			# 			elif res_type == "software":
			# 				resources.filter(res_format="Software")

			# 		if flags["recent"] == 1:
			# 			for resource in resources:
			# 				if not resource.was_published_recently():
			# 					resources.remove(resource)
			# 				else:
			# 					pass
			# 		context["resources"] = resources

			# 	except Exception as e:
			# 		print(f"[>> resource search : {str(e)}")

		return render(request, self.template_name, context)




