from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings

from blog.models import Content 
# Create your models here.


class AccountManager(BaseUserManager):
	def create_user(self, email, username, name, surname, dob, gender, continent, accept, password=None):
 
        # Authentication
		if not email:
			raise ValueError('Users must have an email address')
		if not username:
			raise ValueError('Users must have a username')
		if not accept:
			raise ValueError('You cannot continue without accepting our privacy policy and terms of use')

		user = self.model(
			email=self.normalize_email(email),
			username=username,
			name=name,
			surname=surname,
			dob=dob,
			gender=gender,
			continent=continent,
			accept=accept,
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password, name, surname, dob, gender, continent, accept):
		user = self.create_user(
			email=self.normalize_email(email),
			password=password,
			username=username,
			name=name,
			surname=surname,
			dob=dob,
			gender=gender,
			continent=continent,
			accept=accept,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user

def get_profile_image_filepath(self, filename):
	return 'account/profile_images/' + str(self.pk) +  '/profile_image.png'


"""
Create a settings model and add country and country state
"""

visibility_options = [
	('Anyone', 'Anyone'),
	('Friends', 'Friends'),
	('No One', 'No One'),
]

continents = [

	('Africa', 'Africa'),
	('Australia', 'Australia'),
	('Asia', 'Asia'),
	('Europe', 'Eeurope'),
	('North America', 'North America'),
	('South America', 'South America'),
	('Greenland', 'Greenland'),
	('Antarctica', 'Antarctica'),
]

genders = [
	('Male', 'Male'),
	('Female', 'Female'),
	('Other', 'Other'),
]

# Model
class Account(AbstractBaseUser):

	email 					= models.EmailField(verbose_name="email", max_length=60, unique=True)
	username 				= models.CharField(verbose_name="username", max_length=30, unique=True)
	name 					= models.CharField(verbose_name="name", max_length=30, unique=False)
	surname 				= models.CharField(verbose_name="surname", max_length=30, unique=False)
	gender 					= models.CharField(verbose_name="gender", choices=genders, max_length=20, default='Female', null=False, blank=False)
	dob 					= models.DateField(verbose_name="dob", auto_now_add=False, auto_now=False, unique=False, null=False, blank=False)
	continent 				= models.CharField(verbose_name="continent", choices=continents, max_length=255, default="Africa", null=False, blank=False)

	bio 					= models.TextField(blank=True, null=True)
	profile_image 			= models.ImageField(max_length=255, upload_to=get_profile_image_filepath, null=True, blank=True, default="account/profile_images/default.jpg")
	github  				= models.CharField(verbose_name="github", max_length=80, null=True, blank=True)
	stack  					= models.CharField(verbose_name="stack", max_length=80, null=True, blank=True)
	youtube					= models.CharField(verbose_name="youtube", max_length=80, null=True, blank=True)
	insta	  				= models.CharField(verbose_name="insta", max_length=80, null=True, blank=True)



	date_joined				= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login				= models.DateTimeField(verbose_name='last login', auto_now=True)

	is_admin				= models.BooleanField(verbose_name="is_admin", default=False)
	is_active				= models.BooleanField(verbose_name="is_active", default=True)
	is_staff				= models.BooleanField(verbose_name="is_staff", default=False)
	is_superuser			= models.BooleanField(verbose_name="is_superuser", default=False)
	
	accept 					= models.BooleanField(verbose_name="accept", default=True)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username', 'name', 'surname', 'gender', 'dob', 'continent', 'accept']

	objects = AccountManager()

	def __str__(self):
		return self.username

	def get_profile_image_filename(self):
		return str(self.profile_image)[str(self.profile_image).index('account/profile_images/' + str(self.pk) + "/"):]


	# For checking permissions. to keep it simple all admin have ALL permissons
	def has_perm(self, perm, obj=None):
		return self.is_admin

	# Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
	def has_module_perms(self, app_label):
		return True

chat_perm = [
	('Friends', 'Friends'),
	('Anyone', 'Anyone'),
	('No One', 'No One')
]

class AccountSettings(models.Model):

	account 				= models.OneToOneField('Account', on_delete=models.CASCADE, related_name="settings", null=True)
	
	# Visibility settings

	email_visi				= models.CharField(verbose_name="email_visi", choices=visibility_options, max_length=15, default="No One")
	personal_info_visi		= models.CharField(verbose_name="personal_info_visi", choices=visibility_options, max_length=100, default="No One")
	dob_visi 				= models.CharField(verbose_name="dob_visi", choices=visibility_options, max_length=15, default="No One")
	gender_visi				= models.CharField(verbose_name="gender_visi", choices=visibility_options, max_length=15, default="No One")
	timeline_visi 			= models.CharField(verbose_name="timeline_visi", choices=visibility_options, max_length=15, default="No One")
	friend_list_visi 		= models.CharField(verbose_name="friend_list_visi", choices=visibility_options, max_length=15, default="No One")
	social_links_visi		= models.CharField(verbose_name="social_links_visi", choices=visibility_options, max_length=15, default="No One")
	continent_visi 			= models.CharField(verbose_name="continent_visi", choices=visibility_options, max_length=15, default="No One")

	chat_perm 				= models.CharField(verbose_name="chat_perm", choices=chat_perm, max_length=10, default="Friends")
	featured	 			= models.ForeignKey(Content, on_delete=models.SET_NULL, null=True, blank=True)

	account_setup 			= models.BooleanField(verbose_name="account_setup", default=False)
	settings_setup 			= models.BooleanField(verbose_name="settings_setup", default=False)
	# Stores the current page the user is in
	state 					= models.CharField(verbose_name="state",  max_length=255, null=True, blank=True)
	
	# Store the current channel the user is subscribed to so that notis can be sent
	current_channel 		= models.CharField(verbose_name="current_channel", max_length=80, null=True, blank=True)
	is_online			 	= models.BooleanField(verbose_name="is_online", default=True)

	def __str__(self):
		return self.state

	def connect(self):
		if self.is_online:
			return True 
		else:
			self.is_online = True 
			self.save()

	def disconnect(self):
		if not self.is_online:
			return True 
		else:
			self.is_online = False
			self.save()

	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		username = self.user.username.replace(" ","-")
		return f"Channel-{username}-{self.id}"

