from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
from account.models import BaseAccount
from .models import FriendRequest, FriendList
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from friend.friend_request_status import FriendRequestStatus
from friend.utils import get_friend_request_or_false
from main_asgi.models import PublicChatRoom, Notification, UserChannel

origin = "friend"

# Create your views here.
@login_required(login_url="login")
def friend_requests_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	
	if auth_user.is_authenticated:
		friend_requests = FriendRequest.objects.filter(receiver=auth_user, is_active=True).distinct('sender')
		context['friend_requests'] = friend_requests

		
	else:
		redirect("login")

	context["con_general"] = True
	return render(request ,"friend/friend-requests.html", context)

@login_required(login_url="login")
def send_friend_request_view(request, *args, **kwargs):
	print("[+] Send friend request view running")
	auth_user = request.user
	payload = {}
	
	if auth_user.is_authenticated and request.method == "POST":
		receiver_id = request.POST.get("receiver_user_id")
		if receiver_id:
			receiver = BaseAccount.objects.get(pk=receiver_id)
			try:
				# Get any friend requests (active and not-active)
				friend_requests = FriendRequest.objects.filter(sender=auth_user, receiver=receiver)
				# find if any of them are active (pending)
				try:
					for request in friend_requests:
						if request.is_active:
							payload['response'] = "[-] You already sent them a friend request"
					# If none are active create a new friend request
					friend_request = FriendRequest(sender=auth_user, receiver=receiver)
					friend_request.save()
					payload['response'] = "[+] Friend request sent."
					payload['receiver'] = receiver.username
					print("request sent")
				except Exception as e:
					payload['response'] = "[-] An error occured , try again"
			except FriendRequest.DoesNotExist:
				# There are no friend requests so create one.
				friend_request = FriendRequest(sender=auth_user, receiver=receiver)
				friend_request.save()
				payload['response'] = "[+] Friend request sent."
				print("request sent")

			if payload['response'] == None:
				payload['response'] = "[-] Something went wrong."
		else:
			payload['response'] = "[-] Unable to sent the friend request."
	else:
		return redirect("login")

	return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required(login_url="login")
def accept_friend_request_view(request, *args, **kwargs):
	auth_user = request.user
	payload = {}
	
	if auth_user.is_authenticated and request.method == "GET":
		#	Get the friend request id from the url
		friend_request_id = kwargs.get("friend_request_id")
		if friend_request_id:
			#	Get the friend request from the database
			friend_request = FriendRequest.objects.get(pk=friend_request_id)
			#	Confirm that it is the right one
			if friend_request.receiver == auth_user:
				if friend_request:
					#	Found it and we are accepting it
					#	We built the accept function in the model
					friend_request.accept()
					for fr in FriendRequest.objects.filter(sender=friend_request.sender, receiver=auth_user):
						fr.delete()

					# Update the allowed_friends field in their public chatrooms
					for room in list(PublicChatRoom.objects.filter(admin=friend_request.receiver)):
						if room.accessibility == "Friends":
							pub_room.allowed_friends.add(friend_request.sender)
							pub_room.save()

					for room in list(PublicChatRoom.objects.filter(admin=friend_request.sender)):
						if room.accessibility == "Friends":
							pub_room.allowed_friends.add(friend_request.receiver)
							pub_room.save()

					payload['response'] = "[+] Friend request accepted"
				else:
					payload['response'] = "[-] Something went wrong"
			else:
				payload['response'] = "[-]hat is not your request to accept"
		else:
			payload['response'] = "[-] Unable to accept that reqeust"
	elif not auth_user.is_authenticated:
		return redirect("login")
	else:
		payload['response'] = "You must be authenticated to accept a friend request"
	return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required(login_url="login")
def decline_friend_request_view(request, *args, **kwargs):
	payload = {}
	auth_user = request.user
	
	if auth_user.is_authenticated:
		#	Get the friend request id from the url
		friend_request_id = kwargs.get("friend_request_id")
		if friend_request_id:
			#	Get the friend request from the database
			friend_request = FriendRequest.objects.get(pk=friend_request_id)
			#	Confirm that it is the right one
			if friend_request.receiver == auth_user:
				if friend_request:
					#	Found it and we are accepting it
					#	We built the accept function in the model
					friend_request.decline()
					payload['response'] = "[+] Friend request declined"
				else:
					payload['response'] = "[-] Something went wrong"
			else:
				payload['response'] = "[-] That is not your request to decline"
		else:
			payload['response'] = "[-] Unable to decline that reqeust"
	else:
		payload["response"] = " "
		return redirect("login")
		
	return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required(login_url="login")
def unfriend_view(request, *args, **kwargs):
	payload = {}
	auth_user = request.user
	
	if auth_user.is_authenticated and request.method == "POST":
		receiver_id = request.POST.get("receiver_user_id")
		if receiver_id:
			try:
				removee = BaseAccount.objects.get(pk=receiver_id)
				#	Our friend list
				friend_list = FriendList.objects.get(user=auth_user)
				#	The function was built in the models.py file
				friend_list.unfriend(removee)
				payload['response'] = "[+] Successfully removed that friend"
			except Exception as e:
				payload['response'] = "[-] Something went wrong"
				print(str(e))
		else:
			payload['response'] = "[-] An error occured, please try again"

	else:
		return redirect("login")

	return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required(login_url="login")
def cancel_friend_request_view(request, *args, **kwargs):
	print("[+] Cancell friend request view running")
	payload = {}
	auth_user = request.user
	
	if auth_user.is_authenticated and request.method == "POST":
		#	Get my user id
		receiver_id = request.POST.get("receiver_user_id")
		
		if receiver_id:
			#	Get the receiver of the friend request
			receiver = BaseAccount.objects.get(pk=receiver_id)
			try:
				#	Get all friend requests that are active between me and the receiver [ 1 ]
				friend_requests = FriendRequest.objects.filter(sender=auth_user, receiver=receiver, is_active=True)

			except Exception as e:
				payload['response'] = "[-] Nothing to cancel"

			#	If there are more than one friend requests cancell them all
			if len(friend_requests) > 1:
				for request in friend_requests:
					request.cancel()
				payload['response'] = "[+] Friend request cancelled"
			#	Cancell the single friend request
			elif len(friend_requests) == 1:
				friend_requests.first().cancel()
				payload['response'] = "[+] Friend request cancelled"
		else:
			payload['response'] = "[-] Unable to cancel that reqeust"
	else:
		return redirect("login")
		
	return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required(login_url="login")
def friend_list_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	if auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(id=int(auth_user.id))
		subject_id = kwargs.get("user_id")
		if subject_id:
			try:
				subject_account = BaseAccount.objects.get(pk=subject_id)
				# Change this_user in the template
				context['subject'] = subject_account
				friend_list = FriendList.objects.get(user=subject_account)

			except FriendList.DoesNotExist:
				friend_list = FriendList.objects.create(user=subject_account)
			
			if subject_account == auth_user_account or (subject_account.friend_list_visi == "Everyone") or (subject_account.friend_list_visi == "Friends" and auth_user_account in friend_list.friends.all()):
				friends = [] # [(friend1, True), (friend2, False), ...]
				# get the authenticated users friend list
				# Checking if any of the subject's friends are my friends
				auth_user_friend_list = FriendList.objects.get(user=auth_user)
				for friend in friend_list.friends.all():
					friends.append((friend, auth_user_friend_list.is_mutual_friend(friend)))
				context['friends'] = friends
	else:		
		return redirect("login")
	context["con_general"] = True
	return render(request, "friend/friend-list.html", context)		


@login_required(login_url="login")
def accounts_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	if auth_user.is_authenticated:
		auth_user_id = kwargs.get("user_id")
		if auth_user_id:
			try:
				auth_user_account = BaseAccount.objects.get(id=auth_user_id)
			except:
				return redirect("error:does_not_exist", origin=origin)

			accounts = []
			try:
				# Filters needed
				accounts = list(BaseAccount.objects.all())
				accounts.remove(auth_user_account)
			except:
				return redirect("error:does_not_exist", origin=origin)

			try:
				auth_user_friend_list = FriendList.objects.get(user=auth_user_account)
			except FriendList.DoesNotExist:
				auth_user_friend_list = FriendList.objects.create(user=auth_user_account)
				auth_user_friend_list.save()

			accounts_filtered = []
			for account in accounts:
				if auth_user_friend_list.is_mutual_friend(account):
					pass
				else:

					# CASE1: Request has been sent from THEM to YOU: FriendRequestStatus.THEM_SENT_TO_YOU
					if get_friend_request_or_false(sender=account, receiver=auth_user_account) != False:
						request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
					# CASE2: Request has been sent from YOU to THEM: FriendRequestStatus.YOU_SENT_TO_THEM
					elif get_friend_request_or_false(sender=auth_user_account, receiver=account) != False:
						request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
					# CASE3: No request sent from YOU or THEM: FriendRequestStatus.NO_REQUEST_SENT
					else:
						request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

					accounts_filtered.append((account, request_sent))

			p = Paginator(accounts_filtered, 50)
			page = request.GET.get('page')
			accounts_paginated = p.get_page(page)
			context['accounts'] = accounts_paginated
	try:
		channel = UserChannel.objects.get(user=auth_user_account)
		context["channel"] = channel
		noti_count = noti_count = len(Notification.objects.filter(target=auth_user_account))
		context["noti_count"] = noti_count
	except UserChannel.DoesNotExist:
		channel = UserChannel.objects.create(user=auth_user_account, is_connected=True,state="Feed")
		channel.save()
		context["channel"] = channel
		noti_count = noti_count = len(Notification.objects.filter(target=auth_user_account))
		context["noti_count"] = noti_count
	context["con_general"] = True
	return render(request, "friend/accounts.html", context)


			


