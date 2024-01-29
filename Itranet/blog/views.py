import json
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from account.models import Account as BaseAccount
from friend.models import FriendList
from .models import Post, Comment, PollValue, Poll, Content
import random
from .forms import (
	PostCreationForm,
	PollCreationForm,
	PollUpdateForm,
	PostUpdateForm,
	EditCommentForm,
	)
from account.models import AccountSettings as UserChannel
from main_asgi.models import Notification
from account.utils import create_or_update_settings as get_create_update_channel

origin = "blog"

"""
Creates the content objects which is the base of the post/poll
"""
def create_content(kind, author, title, category, visibility, draft):
	content = Content.objects.create(
			author=author,
			kind=kind,
			title=title,
			category=category,
			visibility=visibility,
			draft=draft,
		)
	content.save()
	return content

"""
Creates post objects and links them to content objs
"""
@login_required(login_url="login")
def create_post_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user

	if not auth_user.is_authenticated:
		return redirect("error:forbidden", origin=origin)

	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		if request.method == "POST" and request.POST:
			form = PostCreationForm(request.POST)
			if form.is_valid():

				kind = "Post"
				title = form.cleaned_data['title']
				text = form.cleaned_data['text']
				category = form.cleaned_data['category']
				visibility = form.cleaned_data['visibility']
				draft = form.cleaned_data['draft']

				content = create_content(
						kind=kind,
						author=auth_user_account,
						title=title,
						category=category,
						visibility=visibility,
						draft=draft,
					)
				content.post = Post.objects.create(content=content, text=text)
				content.text = text
				content.save()
				return redirect("blog:post", post_id=content.post.id)

			else:
				form = PostCreationForm(request.POST)
				context['form'] = form
		else:
			form = PostCreationForm()
			context['form'] = form
	else:
		return redirect('home')

	context["con_general"] = True
	return render(request, "blog/post/create.html", context)


"""
Creates post objects and links them to content objs
"""
@login_required(login_url="login")
def create_poll_view(request, *args, **kwargs):

	context = {}
	auth_user = request.user

	if not auth_user.is_authenticated:
		return redirect("error:forbidden", origin=origin)

	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		if request.method == "POST" and request.POST:
			form = PollCreationForm(request.POST)
			if form.is_valid():

				kind = "Poll"
				title = form.cleaned_data['title']
				text = form.cleaned_data['text']
				category = form.cleaned_data['category']
				visibility = form.cleaned_data['visibility']
				draft = form.cleaned_data['draft']

				content = create_content(
						kind=kind,
						author=auth_user_account,
						title=title,
						category=category,
						visibility=visibility,
						draft=draft,
					)
				poll = Poll.objects.create(content=content)
				poll.save()
				content.text = text
				content.save()
				options = text.replace('\r','').split('\n')
				if len(options) <= 1:
					form = PollCreationForm(request.POST)
					context['form'] = form		
				else:
					for option in options:
						poll_value = PollValue.objects.create(poll=poll, value=option)
						poll_value.save()
						poll.poll_values.add(poll_value)
						poll.save()

					content.poll = poll 
					content.save()
					poll.save()
					return redirect("blog:poll", poll_id=poll.id)
				

			else:
				form = PollCreationForm(request.POST)
				context['form'] = form
		else:
			form = PollCreationForm()
			context['form'] = form
	else:
		return redirect('home')
	context["con_general"] = True
	return render(request, "blog/poll/create.html", context)

"""
Update posts
"""
@login_required(login_url="login")
def update_post_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	post_id = kwargs.get('post_id')

	if not auth_user.is_authenticated:
		return redirect("error:forbidden", origin=origin)

	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		try:
			post = Post.objects.get(id=post_id)
			if (not post.content.is_active or post.content.draft) and post.content.author != auth_user_account:
				return redirect("error:does_not_exist", origin=origin)

		except Post.DoesNotExist:
			return redirect("error:does_not_exist", origin=origin)

		if request.method == "POST" and request.POST:
			form = PostUpdateForm(request.POST)

			if form.is_valid():
				form.save(instance=post)
				return redirect('blog:post', post_id=post.id)
			else:
				form = PostUpdateForm(request.POST)
				context['form'] = form
		else:
			context['post'] = post
	else:
		print("[-]	Red flag : update_post_view")
		return redirect('home')
	context["con_general"] = True
	return render(request, "blog/post/update.html", context)



""" 
Update polls and their content
"""
@login_required(login_url="login")
def update_poll_view(request, *args, **kwargs):
	
	context = {}
	auth_user = request.user
	poll_id = kwargs.get("poll_id")

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:

		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		try:
			poll = Poll.objects.get(id=poll_id)
			if not poll.content.is_active:
				return redirect("error:does_not_exist", origin=origin)
		except:
			return redirect("error:does_not_exist", origin=origin)

		if poll_id:
			context['poll'] = poll
			poll_values = PollValue.objects.filter(poll=poll, is_active=True).order_by('value')
			context['poll_values'] = poll_values
			if len(poll_values) == 2:
				context['cannot_delete'] = True

			if len(poll_values) <= 1:
				return redirect("error:does_not_exist", origin=origin)

			if poll.content.author == auth_user_account:
				context['is_mine'] = True
			else:
				context['is_mine'] = False
		else:
			return redirect("error:does_not_exist", origin=origin)


		if request.method == "POST" and request.POST:

			if poll:
				form = PollUpdateForm(request.POST)
				if form.is_valid():
					form.save(instance=poll, commit=True)
					print("Poll updated")
					return redirect("blog:poll", poll_id=poll_id)

				else:
					form = PostUpdateForm(request.POST)
					context['form'] = form
			else:
				return redirect("error:does_not_exist", origin=origin)
	else:
		return redirect('home')

	context["con_general"] = True
	return render(request, "blog/poll/update.html", context)

"""
Update the poll values using AJAX 
"""
@login_required(login_url="login")
def update_value_view(request, *args, **kwargs):
	payload = {}
	auth_user = request.user
	value_id = kwargs.get("value_id")
	poll_id = kwargs.get("poll_id")

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:

		if value_id and poll_id:
			if request.method == "POST" and request.POST:
				try:
					value = PollValue.objects.get(id=value_id, is_active=True)
					poll = Poll.objects.get(id=poll_id)
					if not poll.content.is_active or poll.content.draft:
						return redirect("error:does_not_exist", origin=origin)

				except Exception as e:
					return redirect("error:does_not_exist", origin=origin)

				if value.poll == poll:
					new_value = request.POST.get("value")
					if new_value:
						value.value = new_value
						value.save()
						payload['response'] = "Value updated successfully"
						return redirect("blog:poll", poll_id=poll_id)
					else:
						return redirect("blog:poll", poll_id=poll_id)
				else:
					return redirect("error:forbidden", origin=origin)
			else:
				pass
		else:
			return redirect('error:does_not_exist', origin=origin)
	else:
		print("[+]	Red flag : update_value_view")

	return HttpResponse(json.dumps(payload), content_type="application/json")
"""
Creates new poll values using existing polls
"""
@login_required(login_url="login")
def create_poll_value_view(request, *args, **kwargs):
	payload = {}
	auth_user = request.user
	poll_id = kwargs.get("poll_id")

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:

		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		try:
			poll = Poll.objects.get(id=poll_id)
			if not poll.content.is_active:
				return redirect("error:does_not_exist", origin=origin)
		except:
			return redirect("error:does_not_exist", origin=origin)	

		try:
			print("creating")
			value = request.POST.get("new_value")
			new_value = PollValue.objects.create(poll=poll, value=value, is_active=True)
			new_value.save()
			payload['response'] = "Value creation successful"
		except Exception as e:
			payload['response'] = "Value creaion unsuccessful"

	return HttpResponse(json.dumps(payload), content_type="application/json")
"""
Deletes existing poll values of polls
"""
@login_required(login_url="login")
def delete_value_view(request, *args, **kwargs):
	payload = {}
	auth_user = request.user
	value_id = kwargs.get("value_id")
	poll_id = kwargs.get("poll_id")

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		if value_id and poll_id:
			if request.method == "POST" and request.POST:
				try:
					value = PollValue.objects.get(id=value_id, is_active=True)
					poll = Poll.objects.get(id=poll_id)
					poll_values = PollValue.objects.filter(poll=poll, is_active=True)
					if not poll.content.is_active or poll.content.draft or poll.content.author != auth_user_account:
						return redirect("error:does_not_exist", origin=origin)

				except Exception as e:
					return redirect("error:does_not_exist", origin=origin)


				if value.poll == poll and len(poll_values) > 2:
					value.is_active = False
					value.save()
					payload['response'] = "Value updated successfully"
					return redirect("blog:poll", poll_id=poll_id)
				else:
					return redirect("error:forbidden", origin=origin)
			else:
				pass
		else:
			return redirect('error:does_not_exist', origin=origin)
	else:
		print("[+]	Red flag : update_value_view")

	return HttpResponse(json.dumps(payload), content_type="application/json")

"""
Creates comments for content objs using AJAX
"""
@login_required(login_url="login")
def create_comment_view(request, *args, **kwargs):
	auth_user = request.user
	payload = {}

	if not auth_user.is_authenticated:
		return redirect("error:forbidden", origin=origin)
	elif auth_user.is_authenticated:
		if request.method == "POST" and request.POST:
			content_id = kwargs.get("content_id")

			if content_id and int(request.POST.get("reply_id")) > 0:
				reply_comment = ''
				reply_comment_id = int(request.POST.get("reply_id"))
				try:
					reply_comment = Comment.objects.get(id=reply_comment_id)
				except Exception as e:
					print(str(e))
					return redirect("error:does_not_exist", origin=origin)

				comment = request.POST.get("data")
				content = Content.objects.get(id=content_id)

				if comment and content and reply_comment:
					comment = Comment.objects.create(author=auth_user, content=content, text=comment, is_reply=True)
					comment.save()
					reply_comment.add_reply(comment=comment)
					reply_comment.save()
					payload['response'] = "[+] Comment added"

					return HttpResponse("Reply added successfully")
				else:
					payload['response'] = "[-] Does not exist"
					return redirect("error:does_not_exist", origin=origin)			

			elif content_id:
				comment = request.POST.get("data")
				content = Content.objects.get(id=content_id)

				if comment and content:
					print(comment + ' ' + content.text)
					comment = Comment.objects.create(author=auth_user, content=content, text=comment)
					comment.save()
					payload['response'] = "[+] Comment added"
				else:
					payload['response'] = "[-] Does not exist"
					return redirect("error:does_not_exist", origin=origin)
			else:
				payload['response'] = "Keyword args are not valid"
				return redirect("error:does_not_exist", origin=origin)

		if payload['response'] == None:
			payload['response'] = "Default"
	else:
		return redirect('login')

	return HttpResponse(json.dumps(payload), content_type="application/json")

"""
Updates comments using AJAX
"""  
@login_required(login_url="login")
def update_comment_view(request, *args, **kwargs):
	payload = {}
	auth_user = request.user

	if not auth_user.is_authenticated:
		return redirect("error:forbidden", origin=origin)

	elif auth_user.is_authenticated:
		try:
			comment_id = kwargs.get("comment_id")
			content_id = kwargs.get('content_id')

			if content_id and comment_id:
				try:
					content = Content.objects.get(id=content_id)
					comment = Comment.objects.get(id=comment_id)
					if content and comment:
						if not comment.author == auth_user:
							return render(request, template_name="erros/not_allowed.html")

						if request.method == "POST":
							form = EditCommentForm(request.POST)
							if form.is_valid():
								text = request.POST.get("content")
								comment.text = text
								comment.save()
								if content.kind == "Post":
									return redirect("blog:post", post_id=content.post.id)
								else:
									return redirect("blog:poll", poll_id=content.poll.id)
							else:
								form = EditCommentForm(request.POST)
								context['form'] = form
					else:
						return redirect("error:does_not_exist", origin=origin)
				
				except Exception as e:
					print(str(e))
					return redirect("error:try_again", origin=origin)
		
		except Exception as e:
			return redirect("error:try_again", origin=origin)


	return redirect('blog:post', post_id=content.post.id)

"""
Deactivates posts
"""
@login_required(login_url="login")
def delete_post_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	post_id = kwargs.get("post_id")

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:

		try:
			post = Post.objects.get(id=post_id)
			post.content.is_active = False
			post.content.save()
			return redirect('home')
			#return redirect("feed", type="random")
		except:
			return redirect("error:does_not_exist", origin=origin)



"""
Deletes comments using content id
"""
@login_required(login_url="login")
def delete_comment_view(request, *args, **kwargs):
	
	auth_user = request.user
	context = {}

	if not auth_user.is_authenticated:
		return redirect("error:forbidden", origin=origin)

	if auth_user.is_authenticated:
		comment_id = kwargs.get("comment_id")
		content_id = kwargs.get('content_id')

		if comment_id and content_id:
			try:
				comment = Comment.objects.get(id=comment_id)
				content = Content.objects.get(id=content_id)

				if comment.author == auth_user:
					comment.is_active = False
					comment.save()
					if content.kind == "Post":
						return redirect("blog:post", post_id=content.post.id)
					else:
						return redirect("blog:poll", poll_id=content.poll.id)
				else:
					return redirect("error:forbidden", origin=origin)
			except Exception as e:
				print("[-] Error : "+str(e))
				return redirect("error:does_not_exist", origin=origin)
		else:
			return redirect("error:does_not_exist", origin=origin)

"""
Deletes polls
"""
@login_required(login_url="login")
def delete_poll_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	poll_id = kwargs.get("poll_id")

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:
		try:
			poll = Poll.objects.get(id=poll_id)
			poll.content.is_active = False
			poll.content.save()
			return redirect('home')
			#return redirect('feed', type="random")
		except:
			return redirect("error:does_not_exist", origin=origin)

"""
Displays polls
"""
@login_required(login_url="login")
def poll_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	poll_id = kwargs.get("poll_id")

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		if poll_id:
			try:
				poll = Poll.objects.get(id=poll_id)
				if not poll.content.is_active or (poll.content.author != auth_user_account and poll.content.draft):
					return redirect("error:does_not_exist", origin=origin)

			except:
				return redirect("error:does_not_exist", origin=origin)

			context['poll'] = poll
			context['content'] = poll.content
			poll_values = PollValue.objects.filter(poll=poll, is_active=True).order_by('value')
			if len(poll_values) <= 1:
				return redirect("error:does_not_exist", origin=origin)

			context['poll_values'] = poll_values

			if poll.content.author == auth_user_account:
				context['is_mine'] = True
			else:
				context['is_mine'] = False
				poll.content.views.add(auth_user_account)
				poll.content.save()
				poll.save()

			comments = []
			c_is_mine = None
			for comment in Comment.objects.filter(content=poll.content, is_active=True).order_by('-timestamp'):
				if comment.author == auth_user:
					c_is_mine = True
					context['c_is_mine'] = True
				else:
					c_is_mine = False 
					context['c_is_mine'] = False
				comments.append((comment, c_is_mine))

			context['comments'] = comments

		else:
			return redirect("error:does_not_exist", origin=origin)

	context["con_general"] = True
	return render(request, "blog/poll/details.html", context)

"""
Displays posts
"""
@login_required(login_url="login")
def post_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	post_id = kwargs.get('post_id')

	if not auth_user.is_authenticated:
		return redirect("error:forbidden", origin=origin)

	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		try:
			post = Post.objects.get(id=post_id)
			if post.content.is_active == False or (post.content.author != auth_user_account and post.content.draft):
				print("yes")
				return redirect("error:does_not_exist", origin=origin)

			if post.content.author == auth_user:
				context['is_mine'] = True 
			else:
				context['is_mine'] = False
				post.content.views.add(auth_user)
				post.content.save()
				post.save()

			context['post'] = post
			context['content'] = post.content

			comments = []
			for comment in Comment.objects.filter(content=post.content, is_active=True, is_reply=False).order_by('-timestamp'):
				c_is_mine = None
				if comment.author == auth_user:
					c_is_mine = True
				else:
					c_is_mine = False
				replies = []
				if len(comment.replies.all()) > 0:
					replies_objs = comment.replies.all().filter(is_active=True)
					for reply in replies_objs:
						replies.append(reply)


				comments.append((comment, c_is_mine, replies))

			context['comments'] = comments

		except Post.DoesNotExist:
			return redirect("error:does_not_exist", origin=origin)

	context["con_general"] = True
	return render(request, "blog/post/details.html", context)


"""
Feed view
"""
@login_required(login_url="login")
def feed_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	if not auth_user.is_authenticated:
		return redirect("error:forbidden", origin=origin)
	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		try:
			contents = Content.objects.filter(is_active=True, draft=False).order_by('-timestamp')
		except Exception as e:
			return redirect("error:does_not_exist", origin=origin)
		
		contents_list = []
		for content in contents:
			is_friend = True
			is_mine = False
			if content.author in auth_user_account.friends.all():
				is_friend = True 
			if content.author == auth_user_account:
				is_mine = True

			comments = []
			for comment in Comment.objects.filter(content=content, is_active=True, is_reply=False).order_by('-timestamp')[:5]:
				c_is_mine = None
				if comment.author == auth_user:
					c_is_mine = True
				else:
					c_is_mine = False
				replies = []
				if len(comment.replies.all()) > 0:
					replies_objs = comment.replies.all().filter(is_active=True)
					for reply in replies_objs:
						replies.append(reply)
				comments.append((comment, c_is_mine, replies))
			
			comment_count = len(Comment.objects.filter(content=content, is_active=True, is_reply=False))

			if is_friend or content.visibility == "Public":
				if content.kind == "Poll":
					poll_values = PollValue.objects.filter(is_active=True, poll=content.poll).order_by('value')
					contents_list.append((content, is_mine, is_friend, poll_values, comments, comment_count))
				else:
					contents_list.append((content, is_mine, is_friend, comments, comment_count))

		# if kwargs.get("type") == "random":
		# 	contents_random = []
		# 	for content in contents_list:
		# 		if not content in contents_random:
		# 			contents_random.append(random.choice(contents_list))
		# 	contents_list = contents_random[:]

		# elif kwargs.get("type") == "recent":
		# 	print("recent")

		p = Paginator(contents_list, 10)
		page = request.GET.get('page')
		content_paginated = p.get_page(page)
		context['contents'] = content_paginated

		if len(contents_list) > 0:
			try:
				featured = random.choice(Content.objects.filter(is_active=True, draft=False, visibility="Public", kind="Post").order_by('-timestamp'))
				context['featured'] = featured
			except:
				pass
			



	context["con_general"] = True
	channel = get_create_update_channel(user=auth_user_account, view="home")
	context["channel"] = channel
	return render(request, "blog/feed.html", context)

"""
Displays stuff you've put out
"""
@login_required(login_url="login")
def my_content_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	if not auth_user.is_authenticated:
		return redirect("error:forbidden", origin=origin)
	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)

	context["con_general"] = True
	return render(request, "blog/my_content.html", context)

"""
Feed with a filter
"""
@login_required(login_url="login")
def category_view(request, *args, **kwargs):
	context = {}
	auth_user = request.user
	category = kwargs.get("category")

	if not auth_user.is_authenticated:
		return redirect("error:forbidden", origin=origin)
	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		try:
			contents = Content.objects.filter(is_active=True, draft=False, category=category).order_by('-timestamp')
		except Exception as e:
			return redirect("error:does_not_exist", origin=origin)
		
		contents_list = []
		for content in contents:
			is_friend = False
			is_mine = False
			if content.author in auth_user_account.friends.all():
				is_friend = True 
			if content.author == auth_user_account:
				is_mine = True

			if is_friend or content.visibility == "Public":
				if content.kind == "Poll":
					poll_values = PollValue.objects.filter(is_active=True, poll=content.poll).order_by('value')
					contents_list.append((content, is_mine, is_friend, poll_values))
				else:
					contents_list.append((content, is_mine, is_friend))

		if kwargs.get("type") == "random":
			contents_random = []
			for content in contents_list:
				if not content in contents_random:
					contents_random.append(random.choice(contents_list))
			contents_list = contents_random[:]


		print(contents_list)
		p = Paginator(contents_list, 5)
		page = request.GET.get('page')
		content_paginated = p.get_page(page)
		context['contents'] = content_paginated

		if len(contents_list) > 0:
			try:
				featured = random.choice(Content.objects.filter(is_active=True, draft=False, visibility="Public", kind="Post", category=category).order_by('-timestamp'))
			except:
				pass
			context['featured'] = featured
	context['category'] = category
	context["con_general"] = True
	return render(request, "blog/category.html", context)

"""
Searches for contents
"""
@login_required(login_url="login")
def search_view(request, *args, **kwargs):
	print("search")
	context = {}
	auth_user = request.user

	if not auth_user.is_authenticated:
		return redirect("error:forbidden", origin=origin)
	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		if request.method == "GET":
			search_query = request.GET.get("q")
			if len(search_query) > 0:
				try:
					contents = Content.objects.filter(is_active=True, draft=False, title__icontains=search_query, text__icontains=search_query).order_by('-timestamp').distinct()
				except Exception as e:
					return redirect("error:does_not_exist", origin=origin)
		
		contents_list = []

		for content in contents:
			is_friend = False
			is_mine = False
			friends = FriendList.objects.get(user=content.author).friends.all()
			if auth_user_account in friends:

				is_friend = True 
			if content.author == auth_user_account:
				is_mine = True

			if is_friend or content.visibility == "Public":
				if content.kind == "Poll":
					poll_values = PollValue.objects.filter(is_active=True, poll=content.poll).order_by('value')
					contents_list.append((content, is_mine, is_friend, poll_values))
				else:
					contents_list.append((content, is_mine, is_friend))

		print(contents_list)
		p = Paginator(contents_list, 5)
		page = request.GET.get('page')
		content_paginated = p.get_page(page)
		context['contents'] = content_paginated

		if len(contents_list) > 0:
			try:
				featured = random.choice(Content.objects.filter(is_active=True, draft=False, visibility="Public", kind="Post").order_by('-timestamp'))
			except:
				pass
			context['featured'] = featured

	context["con_general"] = True
	return render(request, "blog/search.html", context)

"""
Selects poll values on polls using AJAX
"""
@login_required(login_url="login")
def select_view(request, *args, **kwargs):
	payload = {}
	auth_user = request.user
	if request.method == "POST" and request.POST:
		poll_id = kwargs.get("poll_id")
		value_id = kwargs.get("value_id")

	if not auth_user.is_authenticated:
		return redirect('login')
 
	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)
		if poll_id and value_id:
			try:
				poll = Poll.objects.get(id=poll_id)
				value = PollValue.objects.get(id=value_id)
			except:
				return redirect("error:does_not_exist", origin=origin)

			if value.poll == poll:

				if auth_user_account in value.votes.all():
					poll.clean_values(user=auth_user_account)
					poll.save()
					payload['response'] = "Value already selected"
					return redirect("blog:poll", poll_id=poll_id)

				else:
					poll.clean_values(user=auth_user_account)
					poll.save()
					value.add_vote(user=auth_user_account)
					value.save()
					payload['response'] = "Successfully selected"
					return redirect("blog:poll", poll_id=poll_id)
			else:
				payload['response'] = "Action not allowed"
				return redirect("error:forbidden", origin=origin)
		else:
			payload['response'] = "Does not exist"
			return redirect("error:does_not_exist", origin=origin)

	return HttpResponse(json.dumps(payload), content_type="application/json")

"""
fixing needed , do not redirect but increase the like count
"""
@login_required(login_url="login")
def like_view(request, *args, **kwargs):
	payload = {}
	auth_user = request.user
	try:
		content_id = request.GET.get("content_id")
		func = request.GET.get("function")
		like_origin = request.GET.get("like_origin")
		print(str(content_id)+ '\n' +  func + '\n' + like_origin)
	except:
		return redirect("error:does_not_exist", origin=origin)

	if not auth_user.is_authenticated:
		return redirect('login')
 
	elif auth_user.is_authenticated:
		auth_user_account = BaseAccount.objects.get(username=auth_user.username)

		if content_id:
			try:
				content = Content.objects.get(id=content_id, is_active=True)
			except:
				return redirect("error:does_not_exist", origin=origin)

			if func == "like":
				content.undislike(user=auth_user_account)
				content.save()
				if auth_user_account in content.likes.all():
					content.unlike(user=auth_user_account)
					content.save()
					if like_origin == "feed":
						return redirect("blog:feed", type="random")

					elif like_origin == "post_details":
						return redirect("blog:post", post_id=content.post.id)
						
					elif like_origin == "poll_details":
						return redirect("blog:poll", poll_id=content.poll.id)

				elif auth_user_account not in content.likes.all():
					content.add_like(user=auth_user_account)
					content.save()
					if like_origin == "feed":
						return redirect("blog:feed", type="random")
					elif like_origin == "post_details":
						return redirect("blog:post", post_id=content.post.id)
						
					elif like_origin == "poll_details":
						return redirect("blog:poll", poll_id=content.poll.id)
			

			elif func == "dislike":
				content.unlike(user=auth_user_account)
				content.save()
				if auth_user_account in content.dislikes.all():
					content.undislike(user=auth_user_account)
					content.save()
					if like_origin == "feed":
						return redirect("blog:feed", type="random")
					elif like_origin == "post_details":
						return redirect("blog:post", post_id=content.post.id)
					elif like_origin == "poll_details":
						return redirect("blog:poll", poll_id=content.poll.id)

				elif auth_user_account not in content.likes.all():
					content.add_dislike(user=auth_user_account)
					content.save()
					if like_origin == "feed":
						return redirect("blog:feed", type="random")
					elif like_origin == "post_details":
						return redirect("blog:post", post_id=content.post.id)
						
					elif like_origin == "poll_details":
						return redirect("blog:poll", poll_id=content.poll.id)

		else:
			return redirect("error:does_not_exist", origin=origin)

@login_required(login_url="login")
def set_featured_view(request, *args, **kwargs):
	payload = {}
	auth_user = request.user

	if not auth_user.is_authenticated:
		return redirect('login')

	elif auth_user.is_authenticated:
		auth_user_account = None
		try:
			auth_user_account = BaseAccount.objects.get(id=auth_user.id)
			content_id = request.GET.get("content_id")
		except BaseAccount.DoesNotExist:
			return redirect("error", code=400)


		try:
			content = Content.objects.get(id=int(content_id))
		except:
			payload["response"] = "An error occured"
			return redirect("error", code=404)

		auth_user_account.featured = content
		auth_user_account.save()
		payload["response"] = "Changes saved successfully"


	return HttpResponse(json.dumps(payload), content_type="application/json")