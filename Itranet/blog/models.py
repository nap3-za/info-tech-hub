from django.db import models
from django.conf import settings
from django.utils import timezone

import datetime

# Create your models here.

categories = [

	('General', 'General'),
	('Linux', 'Linux'),
	('Windows', 'Windows'),
	('Hardware', 'Hardware'),
	('Software', 'Software'),
	('Programming / Coding', "Programming / Coding"),
	('School', 'School'),
]

visibility_options = [
	('Friends', 'Friends'),
	('Public', 'Public'),
]

types = [
	('Post', 'Post'),
	('Poll', 'Poll'),
]


class Content(models.Model):
	author 		= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	title 		= models.CharField(verbose_name="title", max_length=200, null=True, blank=True, unique=False)
	kind 		= models.CharField(choices=types, verbose_name="kind", max_length=50, default="Post")
	category 	= models.CharField(choices=categories, verbose_name="category", default="General", max_length=30)

	text  		= models.TextField(blank=True, null=True)

	comments 	= models.ManyToManyField('Comment', related_name="comments", blank=True)
	views 		= models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="views")
	likes 		= models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="likes")
	dislikes 	= models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="dislikes")

	draft 		= models.BooleanField(verbose_name="draft", default=True)
	visibility 	= models.CharField(verbose_name="visibility", choices=visibility_options, default="Friends", max_length=100)

	timestamp 	= models.DateTimeField(verbose_name="timestamp", auto_now_add=True)	
	is_active 	= models.BooleanField(default=True, verbose_name="is_active")

	def __str__(self):
		return self.kind + ' | ' + self.title

	def add_like(self, user):
		if user in self.dislikes.all():
			self.dislikes.remove(user)
			self.save()
			return True 
		else:
			if user in self.likes.all():
				return True
			self.likes.add(user)
			self.save()
			return True 
	
	def add_dislike(self, user):
		if user in self.likes.all():
			self.likes.remove(user)
			self.save()
			return True
		else:
			if user in self.dislikes.all():
				return True 
			self.dislikes.add(user)
			self.save()
			return True 

	def unlike(self, user):
		if user in self.likes.all(): 
			self.likes.remove(user)
			self.save()
			return True

	def undislike(self, user):
		if user in self.dislikes.all():
			self.dislikes.remove(user)
			self.save()
			return True

	def was_published_recently(self):
		now = timezone.now()
		return now - datetime.timedelta(days=31) <= self.pub_date <= now


class Post(models.Model):

	content   	= models.OneToOneField('Content', on_delete=models.CASCADE, null=True, blank=False)
	text  	 	= models.TextField(verbose_name="text", max_length=5000, null=True, blank=False, unique=False)

	def __str__(self):
		return self.content.title

class Poll(models.Model):

	content   	= models.OneToOneField('Content', on_delete=models.CASCADE, null=True, blank=False)
	poll_values	= models.ManyToManyField('PollValue', related_name="poll_values", blank=False)

	def __str__(self):
		return self.content.title

	def clean_values(self, user):
		try:
			poll_values = self.poll_values.all()
			for poll_value in poll_values:
				poll_value.remove_vote(user=user)
				poll_value.save()

			self.save()
			return True
		except Exception as e:
			print(f"[-] Failed : {e}")
			return False

		viewers = self.views.all()
		return viewers

class PollValue(models.Model):

	poll 		= models.ForeignKey('Poll', verbose_name="poll", on_delete=models.CASCADE)
	value 		= models.CharField(verbose_name="value", max_length=100, unique=False)
	votes  		= models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="votes")
	timestamp 	= models.DateTimeField(verbose_name="timestamp", auto_now_add=True)
	is_active 	= models.BooleanField(default=True, verbose_name="is_active")
	
	
	def __str__(self):
		return self.value

	def add_vote(self, user):
		if not user in self.votes.all():
			self.votes.add(user)
			self.save()
		else:
			return False

	def remove_vote(self, user):
		if user in self.votes.all():
			self.votes.remove(user)
			self.save()
			return True
		else:
			return False

	def change_vote(self, user, value):

		if user in self.votes() and not user in value.votes():
			self.votes.remove_vote(user)
			value.add_vote(user)
			value.save()
			return True
		else:
			return False

class Comment(models.Model):

	author  		= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	text 	 		= models.CharField(verbose_name="text", max_length=250, null=False, blank=True)
	content			= models.ForeignKey('Content', verbose_name="content", on_delete=models.CASCADE, blank=False, null=True)

	visibility  	= models.CharField(verbose_name="visibility", choices=visibility_options, default="Friends", max_length=100)
	is_reply 		= models.BooleanField(verbose_name="is_reply", default=False)
	replies  		= models.ManyToManyField('Comment', related_name="comment_replies", blank=True)

	timestamp 		= models.DateTimeField(verbose_name="timestamp", auto_now_add=True)
	is_active 		= models.BooleanField(default=True, verbose_name="is_active")

	def __str__(self):
		return self.author.username

	def add_reply(self, comment):
		if not comment in self.replies.all():
			self.replies.add(comment)
			return True
		else:
			return False


