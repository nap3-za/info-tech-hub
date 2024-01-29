from django.db import models
from django.conf import settings

# Create your models here.



def get_resource_image_filepath(self, filename):
	return 'resource_images/' + str(self.pk) + '/image.png'

res_formats = [
	('Video', 'Video'),
	('Article', 'Article'),
	('Software', 'Software'),
	('Audio', 'Audio')
]

class Resource(models.Model):

	author              = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	title               = models.CharField(verbose_name="title", max_length=250, blank=True)
	description         = models.TextField(blank=True)
	res_format 			= models.CharField(verbose_name="res_format", max_length=250, blank=True, choices=res_formats)

	image               = models.ImageField(max_length=255, upload_to=get_resource_image_filepath, null=True, blank=True)
	# zip of scripts
	# video
	link                = models.CharField(verbose_name="link", max_length=250, blank=True)
	upvotes 			= models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="upvotes", blank=True)
	downvotes 			= models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="downvotes", blank=True)
	timestamp           = models.DateTimeField(auto_now_add=True)
	res_timestamp       = models.IntegerField(verbose_name="res_timestamp", null=True, blank=False)
	is_active           = models.BooleanField(default=False)

	def __str__(self):
		return self.title


	def add_upvote(self, user):
		if user in self.downvotes.all():
			self.downvotes.remove(user)
			self.save()
			return True 
		else:
			if user in self.upvotes.all():
				return True
			self.upvotes.add(user)
			self.save()
			return True 
	
	def add_downvote(self, user):
		if user in self.upvotes.all():
			self.upvotes.remove(user)
			self.save()
			return True
		else:
			if user in self.downvotes.all():
				return True 
			self.downvotes.add(user)
			self.save()
			return True 

	def unupvote(self, user):
		if user in self.upvotes.all(): 
			self.upvotes.remove(user)
			self.save()
			return True

	def undownvote(self, user):
		if user in self.downvotes.all():
			self.downvotes.remove(user)
			self.save()
			return True
	def was_published_recently(self):
		now = timezone.now()
		return now - datetime.timedelta(days=31) <= self.pub_date <= now


class Feedback(models.Model):
    author              = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content             = models.TextField(blank=True, null=True)
    feedback            = models.CharField(verbose_name="feedback", null=True, blank=True, max_length=1000)
    timestamp           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:20]

class Question(models.Model):
    author              = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question            = models.TextField()
    answer              = models.TextField()
    is_answered         = models.BooleanField(default=False)
    timestamp           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:20]

