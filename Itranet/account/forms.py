from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.utils import timezone 

import datetime
from .models import Account, AccountSettings



class RegistrationForm(UserCreationForm):

	email = forms.EmailField(max_length=254, help_text='Add a valid email address.')

	class Meta:
		model = Account
		fields = (
			'accept',
			'email',
			'username',
			'name',
			'surname',
			'gender' ,
			'dob',
			'continent',
			'password1',
			'password2',
			)

	def clean_email(self):
		email = self.cleaned_data['email'].lower()
		accounts = Account.objects.filter(email=email, is_active=True)
		if len(accounts) >= 1:
			raise forms.ValidationError(f'Email {email} is already in use.')
		else:
			return email

	def clean_dob(self):
		dob = self.cleaned_data["dob"]
		if dob + datetime.timedelta(days=4745) > timezone.now().date():
			print("Ivalid dob")
			raise forms.ValidationError("You must be above 13 years to be eligible to register")
		elif not dob + datetime.timedelta(days=4745) > timezone.now().date():
			return dob

		
	def clean_username(self):
		username = self.cleaned_data['username']
		accounts = Account.objects.filter(username=username, is_active=True)
		if len(accounts) >= 1:
			raise forms.ValidationError(f'Username {username} is already in use.')
		else:
			return username


	def clean_accept(self):
		accept = self.cleaned_data['accept']
		if not accept:
			raise forms.ValidationError('You must accept Itranet\'s privacy policy and terms of use to continue')
		elif accept:
			return accept
	
class ProfileSetupForm(forms.ModelForm):

	class Meta:
		model = Account 
		fields = (
			'profile_image',
			'bio',
			'github',
			'stack',
			'youtube',
			'insta',
		)

	def save(self, instance, commit=True):
		account = instance
		account.profile_image = self.cleaned_data["profile_image"]
		account.bio = self.cleaned_data["bio"]
		account.github = self.cleaned_data["github"]
		account.stack = self.cleaned_data["stack"]
		account.youtube = self.cleaned_data["youtube"]
		account.insta = self.cleaned_data["insta"]
		if commit:
			account.save()
		return account

class UpdateSettingsForm(forms.ModelForm):

	class Meta:
		model = AccountSettings
		fields = (
			'email_visi',
			'personal_info_visi',
			'social_links_visi',
			'friend_list_visi',
			'chat_perm',
			'timeline_visi',
			'continent_visi',
			'gender_visi',
			)

	def save(self, instance, commit=True):
		account = instance
		account.settings.email_visi = self.cleaned_data["email_visi"]
		account.settings.personal_info_visi = self.cleaned_data["personal_info_visi"]
		account.settings.social_links_visi = self.cleaned_data["social_links_visi"]
		account.settings.friend_list_visi = self.cleaned_data["friend_list_visi"]
		account.settings.chat_perm = self.cleaned_data["chat_perm"]
		account.settings.timeline_visi = self.cleaned_data["timeline_visi"]
		account.settings.continent = self.cleaned_data["continent_visi"]
		account.settings.gender_visi = self.cleaned_data["gender_visi"]
		if commit:
			account.save()
		return account

class AuthenticationForm(forms.ModelForm):

	password = forms.CharField(label='Password', widget=forms.PasswordInput)

	class Meta:
		model = Account
		fields = ('email', 'password')

	def clean(self):
		email = self.cleaned_data['email']
		password = self.cleaned_data['password']
		try:
			account = Account.objects.get(email=email, is_active=True)
			auth_user_account = authenticate(email=email, password=password)
		except:
			raise forms.ValidationError("Invalid login")

class UpdateAccountForm(forms.ModelForm):
	pass
	class Meta:
		model = Account
		fields = (
			'username',

			'email',

			'name',
			'surname',

			'bio',
			'profile_image',

			'github',
			'stack',
			'youtube',
			'insta',

			'continent',
			)

	def clean_email(self):
		email = self.cleaned_data['email'].lower()
		accounts = Account.objects.filter(email=email, is_active=True)
		if len(accounts) > 1:
			return forms.ValidationError(f"Email {email} already in use")
		elif len(accounts) <= 1:
			return email
		else:
			raise forms.ValidationError("Invalid email")

	def clean_username(self):
		username = self.cleaned_data['username']
		accounts = Account.objects.filter(username=username, is_active=True)
		if len(accounts) > 1:
			return forms.ValidationError(f"Username {username} already in use")
		elif len(accounts) <= 1:
			return username
		else:
			raise forms.ValidationError("Invalid username")

	def save(self, instance, commit=True):
		account = instance
		account.username = self.cleaned_data['username']
		account.email = self.cleaned_data['email'].lower()
		account.name = self.cleaned_data['name']
		account.surname = self.cleaned_data['surname']
		account.bio = self.cleaned_data['bio']
		account.profile_image = self.cleaned_data['profile_image']
		account.continent = self.cleaned_data['continent']
		account.github = self.cleaned_data["github"]
		account.stack = self.cleaned_data["stack"]
		account.youtube = self.cleaned_data["youtube"]
		account.insta = self.cleaned_data["insta"]
		if commit:
			account.save()
		return account

class DeleteAccountForm(forms.Form):

	email = forms.EmailField()

	def clean_email(self):
		email = self.cleaned_data['email'].lower()
		try:
			account = Account.objects.get(email=email, is_active=True)
			return email
		except:
			raise forms.ValidationError("Invalid email")

	def save(self, instance, commit=True):
		instance.is_active = False
		instance.save()
		return instance

class LockForm(forms.Form):

	pass
