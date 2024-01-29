from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from friend.models import FriendRequest

class PrivateChatRoom(models.Model):
	"""
	A private room for people to chat in.
	"""
	user1               = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user1")
	user2               = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user2")

	# Users who are currently connected to the socket (Used to keep track of unread messages)
	connected_users     = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="connected_users")

	is_active 			= models.BooleanField(default=False)
	is_deleted 			= models.BooleanField(default=False)

	seen_timestamp 		= models.DateTimeField(null=True, blank=True)

	def connect_user(self, user):
		"""
		return true if user is added to the connected_users list
		"""
		is_user_added = False
		if not user in self.connected_users.all():
			self.connected_users.add(user)
			self.save()
			is_user_added = True
		return is_user_added 


	def disconnect_user(self, user):
		"""
		return true if user is removed from connected_users list
		"""
		is_user_removed = False
		if user in self.connected_users.all():
			self.connected_users.remove(user)
			self.save()
			is_user_removed = True
		return is_user_removed

	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return f"PrivateChatRoom-{self.id}"

class PrivateChatMessageManager(models.Manager):
	def by_room(self, room):
		qs = PrivateChatMessage.objects.filter(room=room).order_by("-timestamp")
		return qs

class PrivateChatMessage(models.Model):
	"""
	Chat message created by a user inside a Room
	"""
	user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	room                = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE, related_name="message")
	timestamp           = models.DateTimeField(auto_now_add=True)
	content             = models.TextField(unique=False, blank=False,)
	is_new_message 		= models.BooleanField(default=True, verbose_name="is_new_message")
	seen 				= models.BooleanField(default=False, verbose_name="seen")

	objects = PrivateChatMessageManager()

	def __str__(self):
		return self.content

	@property
	def msg_type(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return f"private_msg"


	def room_id(self):
		"""
		Returns the room id of the message
		"""
		return self.room.id

	@property
	def is_recent(self):
		"""
		Returns true if the message is a recent message the message
		"""
		if len(PrivateChatMessage.objects.filter(room=self.room)) > 1:
			return True  
		else:
			return False



accessibility_options = [
('All Friends', 'All Friends'),
('Selected Friends', 'Selected Friends'),
('Everyone', 'Everyone'),
]

class PublicChatRoom(models.Model):

	# Room title
	title 				= models.CharField(max_length=255, unique=False, blank=False)
	# An id
	room_name			= models.CharField(max_length=255, unique=True, blank=False, null=False)

	# all users who are authenticated and viewing the chat
	admin 				= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="admin",null=True, blank=False)
	accessibility 		= models.CharField(max_length=255, verbose_name="accessibility", choices=accessibility_options)
	allowed_friends		= models.ManyToManyField(settings.AUTH_USER_MODEL, help_text="users who are allowed to connect.", blank=True, related_name="allowed_friends")
	users 				= models.ManyToManyField(settings.AUTH_USER_MODEL, help_text="users who are connected to chat room.", blank=True, related_name="users")

	def __str__(self):
		return self.title

	def connect_user(self, user):
		"""
		return true if user is added to the users list
		"""
		is_user_added = False
		if not user in self.users.all():
			self.users.add(user)
			self.save()
			is_user_added = True
		elif user in self.users.all():
			is_user_added = True
		return is_user_added 

	def disconnect_user(self, user):
		"""
		return true if user is removed from the users list
		"""
		is_user_removed = False
		if user in self.users.all():
			self.users.remove(user)
			self.save()
			is_user_removed = True
		return is_user_removed 

	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return "PublicChatRoom-%s" % self.id

class PublicChatMessageManager(models.Manager):
    def by_room(self, room):
        qs = PublicChatMessage.objects.filter(room=room).order_by("-timestamp")
        return qs

class PublicChatMessage(models.Model):
	"""
	Chat message created by a user inside a PublicChatRoom
	"""
	user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	room                = models.ForeignKey(PublicChatRoom, on_delete=models.CASCADE)
	timestamp           = models.DateTimeField(auto_now_add=True)
	content             = models.TextField(unique=False, blank=False,)
	seen_timestamp 		= models.DateTimeField(null=True, blank=True)

	objects = PublicChatMessageManager()

	def __str__(self):
		return self.content

	def msg_type(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return f"public_msg"


	def room_id(self):
		"""
		Returns the room id of the message
		"""
		return self.room.id



class Notification(models.Model):

	# Who the notification is sent to
	target 						= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=False)

	# The user that the creation of the notification was triggered by.
	from_user 					= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="from_user")

	redirect_url				= models.CharField(max_length=500, null=True, unique=False, blank=True, help_text="The URL to be visited when a notification is clicked.")

	# statement describing the notification (ex: "Mitch sent you a friend request")
	verb 						= models.CharField(max_length=255, unique=False, blank=True, null=True)

	# When the notification was created/updated
	timestamp 					= models.DateTimeField(auto_now_add=True)

	# Some notifications can be marked as "read". (I used "read" instead of "active". I think its more appropriate)
	read 						= models.BooleanField(default=False)

	def __str__(self):
		return self.verb

	# Retuns a list of all the user's notifications
	def all(self):
		notifications = Notification.objects.filter(target=self.target)
		return notifications
