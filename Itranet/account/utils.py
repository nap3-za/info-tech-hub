from django.core.serializers.python import Serializer
from .models import AccountSettings
from stats.models import UserAppData
from friend.models import FriendList


class LazyAccountEncoder(Serializer):
    def get_dump_object(self, obj):
        dump_object = {}
        dump_object.update({'id': str(obj.id)})
        dump_object.update({'email': str(obj.email)})
        dump_object.update({'username': str(obj.username)})
        dump_object.update({'profile_image': str(obj.profile_image.url)})
        return dump_object


def get_or_create_frlist(user):
	if user != None:
		friend_list = None
		try:
			friend_list = FriendList.objects.get(user=user)
		except:
			friend_list = FriendList.objects.create(user=user)
			friend_list.save()
		return friend_list
	else:
		return Exception("User is none")

def get_or_create_appdata(user):
	if user != None:
		user_appdata = None
		try:
			user_appdata = UserAppData.objects.get(user=user)
		except:
			user_appdata = UserAppData.objects.create(user=user)
			user_appdata.save()

		return user_appdata

	else:
		return Exception("User is none")

def create_or_update_settings(user, state, **kwargs):
	user_settings = None
	try:
		user_settings = AccountSettings.objects.get(account=user)
		user_settings.state = state
		user_settings.save()
	except:
		user_settings = AccountSettings.objects.create(account=user, state=state)
		user_settings.save()
	return user_settings
