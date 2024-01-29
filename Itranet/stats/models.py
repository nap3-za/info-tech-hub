from django.db import models
from account.models import Account

# Create your models here.


class UserAppData(models.Model):

	user	 				= models.OneToOneField(Account, related_name="app_data", on_delete=models.SET_NULL, null=True, blank=True)

	question_count			= models.IntegerField(verbose_name="questions", default=0, null=True, blank=True)
	feedback_count			= models.IntegerField(verbose_name="feedback", default=0, null=True, blank=True)
	content_count	 		= models.IntegerField(verbose_name="content_count", default=0, null=True, blank=True)
	Interactions     		= models.OneToOneField('Interactions', on_delete=models.SET_NULL, related_name="interactions", null=True)
	# Responses of questions the user might have asked
	positive_responses 		= models.IntegerField(verbose_name="positive_responses", default=0, null=True, blank=True)
	negative_responses 		= models.IntegerField(verbose_name="negative_responses", default=0, null=True, blank=True)

	reports		 			= models.ManyToManyField('Report', related_name="reports", blank=True)

	def increment(self, target):
		try:
			if target != None:

				if target == "question_count":
					self.question_count += 1
					self.save()
				elif target == "feedback_count":
					self.feedback_count += 1
					self.save()
				elif target == "content_count":
					self.content_count += 1
					self.save()
				elif target == "positive_responses":
					self.positive_responses += 1
					self.save()
				elif target == "negative_responses":
					self.negative_responses += 1
					self.save()
			else:
				return Exception("Target is none")
		except Exception as e:
			print(f"[>> increment in interaction : {e}")


	def __str__(self):
		return self.user.username

report_types = [
	('Account', 'Account'),
	('Post', 'Post'),
	('Poll', 'Poll'),
	('Resource', 'Resource'),
	('Comment', 'Comment'),
]

report_reasons = [
	('Contains sensetive/inappropriate content', 'Contains sensetive/inappropriate content'),
	('Racist', 'Racist'),
	('False facts', 'False facts'),

]


class Report(models.Model):

	subject 				= models.CharField(verbose_name="subject", max_length=500, choices=report_types)
	subject_id 				= models.IntegerField(verbose_name="subject_id", default=0, null=False, blank=False)

	reason 					= models.CharField(verbose_name="reason", max_length=1000, choices=report_reasons, blank=False, null=False, default="default")

	timestamp 				= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.subject


class Interactions(models.Model):

	user 					= models.OneToOneField(Account, related_name="interactions_user", on_delete=models.SET_NULL, null=True, blank=True)

	likes 					= models.IntegerField(verbose_name="likes", default=0, null=True, blank=True)
	dislikes 				= models.IntegerField(verbose_name="dislikes", default=0, null=True, blank=True)
	comments 			 	= models.IntegerField(verbose_name="comments", default=0, null=True, blank=True)
	
	sent_friendreq 			= models.IntegerField(verbose_name="sent_friendreq", default=0, null=True, blank=True) 				
	received_friendreq 		= models.IntegerField(verbose_name="received_friendreq", default=0, null=True, blank=True)

	def __str__(self):
		return self.user.username


	def increment(self, target):
		try:
			if target != None:

				if target == "likes":
					self.likes += 1
					self.save()
				elif target == "dislikes":
					self.dislikes += 1
					self.save()
				elif target == "comments":
					self.comments += 1
					self.save()
				elif target == "sent_friendreq":
					self.sent_friendreq += 1
					self.save()
				elif target == "received_friendreq":
					self.received_friendreq += 1
					self.save()
			else:
				return Exception("Target is none")
		except Exception as e:
			print(f"[>> increment in interaction : {e}")