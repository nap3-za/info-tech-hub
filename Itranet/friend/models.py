from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.

class FriendList(models.Model):

    #   One friendlist per one user
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friend_list")
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="friends")

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        #   Add a new friend
        #   Chaecks if they ar friends
        if not account in self.friends.all():
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        #   Remove a friend
        #   Checks if they are friends

        if account in self.friends.all():
            self.friends.remove(account)
    
    #   Removes a person from your friend list 
    #   the remover is the person removing

    def unfriend(self, removee):

        remover_friend_list = self

        remover_friend_list.remove_friend(removee)

    #   remove the friend from the removee's friend list

        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(self.user)

    def is_mutual_friend(self, friend):

        if friend in self.friends.all():
            return  True
        return False

    
class FriendRequest(models.Model):

    #   A friend request consists of two parts
    # the sender and the receiver

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(blank=True, null=False, default=True)

    def __str__(self):
        return self.sender.username

    def accept(self):
        # Accepting a friend request and updating the sender and receiver's friend lists

        try:
            sender_friend_list = FriendList.objects.get(user=self.sender)
            self.timestamp = timezone.now()
        except FriendList.DoesNotExist:
            sender_friend_list = FriendList.objects.create(user=self.sender)
            sender_friend_list.save()

        try:
            receiver_friend_list = FriendList.objects.get(user=self.receiver)
        except FriendList.DoesNotExist:
            receiver_friend_list = FriendList.objects.create(user=self.receiver)
            receiver_friend_list.save()

        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)
            sender_friend_list = FriendList.objects.get(user=self.sender)
            if sender_friend_list:
                sender_friend_list.add_friend(self.receiver)
                sender_friend_list.save()
                receiver_friend_list.save()
                self.is_active = False
                self.save()

    def decline(self):
        #   Declines a friend request
        self.is_active = False
        self.save()

    def cancel(self):
        #   Cancelling a friend request is avtive to false
        self.is_active = False
        self.save()

    
