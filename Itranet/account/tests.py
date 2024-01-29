from django.test import TestCase, Client
from django.utils import timezone

# Create your tests here.
import datetime
import random

from .models import Account

def password_gen(length, char_selection):

	chars = {
		1 : "0123456789",
		2 : "qwertyuioplkjhgfdsazxcvbnm",
		3 : "QWERTYUIOPLKJHGFDSAZXCVBNM",
		4 : "_-*$#@!.,[](){}",
		0 : "",
	}

	chars = "".join([chars[char] for char in char_selection])
	random_chars = "".join(random.sample(chars, length))
	return random_chars

class AccountModelTestCase(TestCase):
	
	def test_account_registration(self):
		continent = random.choice([
			'Africa',
			'Australia',
			'Asia',
			'Europe',
			'North America',
			'Antarctica',
			'Greenland',
			'South America',
		])

		gender = random.choice(['Male', 'Female', 'Other'])
		dob = timezone.now().date() - datetime.timedelta(days=5110)

		client = Client(follow=False)
		client_two = Client(follow=False)

		client.post("/register/", {
			"username": "user1",
			"email": "user@email.com",
			"name":"user1",
			"surname": "user1",
			"password1": "root.1352",
			"password2": "root.1352",
			"dob": dob,
			"continent": continent,
			"gender": gender,
			"accept": True,
		})


		account = Account.objects.get(pk=1)


		print(f"""[+] User : {account.username} | {account.continent}""")

		client.post("/account/setup_profile/", {
			"bio": "The quick brown fox jumped over the lazy dog",	
			"stack": "user",
			"youtube": "user",
			"github": "user",
			"stack": "user",
			"insta": "user",	
		})


		print(f"[+] User settings : {hasattr(account, 'settings')}")
		print(f"[+] User appdata : {hasattr(account, 'app_data')}")
		print(f"[+] User friend list : {hasattr(account, 'friend_list')}")

		client.get("/logout/")
		client.post("/login/", {
			"email": "user@email.com",
			"password": "root.1352"
		})

		client_two.get("/logout/")
		client_two.post("/login/", {
			"email": "user2@email.com",
			"password": "root.1352"
		})

		client.post('/account/update_settings/', {
			"email_visi": "Friends",
			"personal_info_visi": "Friends",
			"chat_perm": "Friends",
			"continent_visi": "Friends",
			"friend_list_visi": "Friends",
			"timeline_visi": "Friends",
			"social_links_visi": "Friends",
			"passphrase": "Friends",
		})

		client.post("/register/", {
			"username": "user1Updated",
			"email": "userUpdated@email.com",
			"name":"user1Updated",
			"surname": "user1Updated",
			"continent": continent,
			"accept": True,
			"bio": "Updated fox jump baby",
		})

		print(f"[+] Updated user : | {account.username} | {account.email_visi} | {account.bio}")
