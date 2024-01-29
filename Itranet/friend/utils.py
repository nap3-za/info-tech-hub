from friend.models import FriendRequest

def get_friend_request_or_false(sender, receiver):
	try:
		friend_requests = FriendRequest.objects.filter(sender=sender, receiver=receiver, is_active=True)
		if len(friend_requests) == 1:
			return friend_requests[0]

		elif len(friend_requests) > 1:
			friend_request = list(friend_requests).pop()
			for fr in friend_requests:
				fr.delete()
			return friend_request

		else:
			return False
			

	except:
		return False 