from main_asgi.models import UserChannel


def get_create_update_channel(user, view):
	try:
		channel = UserChannel.objects.filter(user=user)
		if len(channel) == 1:
			channel[0].state = view
			channel[0].save()
			return channel[0]
		elif len(channel) == 0:
			channel = UserChannel.objects.create(user=user, state=view)
			channel.save()
			return channel
		else:
			return None
	except Exception as e:
		print(f"[>> get_create_update_channel : {e}")