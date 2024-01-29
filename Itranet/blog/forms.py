from django import forms 
from .models import Post, Poll, PollValue, Comment
from account.models import Account as BaseAccount


categories = [

	('General', 'General'),
	('Linux', 'Linux'),
	('Windows', 'Windows'),
	('Hardware', 'Hardware'),
	('Software', 'Software'),
	('Programming / Coding', "Programming / Coding"),
	('School', 'School'),
]

visibility_options = [
	('Friends', 'Friends'),
	('Public', 'Public'),
]

types = [
	('Post', 'Post'),
	('Poll', 'Poll'),
	('Snippet', 'Snippet'),
]


class PostCreationForm(forms.Form):

	title 			= forms.CharField(max_length=250, required=False)
	text  			= forms.CharField(widget=forms.Textarea)
	category 		= forms.ChoiceField(choices=categories)
	visibility 		= forms.ChoiceField(choices=visibility_options)
	draft 			= forms.BooleanField(required=False)

	def clean(self):
		category = self.cleaned_data['category']
		visibility = self.cleaned_data['visibility']
		draft = self.cleaned_data['draft']
		text = self.cleaned_data['text']

		if not (text, draft, category, visibility):
			raise forms.ValidationError("Please fill all the required fields")

class SnippetCreationForm(forms.Form):

	text  			= forms.CharField(widget=forms.Textarea, max_length=500)
	category 		= forms.ChoiceField(choices=categories)
	is_question		= forms.BooleanField(required=False)
	visibility 		= forms.ChoiceField(choices=visibility_options)
	draft 			= forms.BooleanField(required=False)

	def clean(self):
		category = self.cleaned_data['category']
		is_question = self.cleaned_data['is_question']
		visibility = self.cleaned_data['visibility']
		draft = self.cleaned_data['draft']
		text = self.cleaned_data['text']

		if not (text, draft, category, visibility):
			raise forms.ValidationError("Please fill all the fields")

class PollCreationForm(forms.Form):

	title 			= forms.CharField(max_length=250)
	text  			= forms.CharField(widget=forms.Textarea)
	category 		= forms.ChoiceField(choices=categories)
	visibility 		= forms.ChoiceField(choices=visibility_options)
	draft 			= forms.BooleanField(required=False)

	def clean(self):
		title = self.cleaned_data['title']
		category = self.cleaned_data['category']
		visibility = self.cleaned_data['visibility']
		draft = self.cleaned_data['draft']
		text = self.cleaned_data['text']

		if not (title, text, draft, category, visibility):
			raise forms.ValidationError("Please fill all the fields")

		options = text.replace('\r','').split('\n')

		print(options)
		if len(options) <= 1:
			raise forms.ValidationError("Poll options should be 2 or more")

class PostUpdateForm(forms.Form):

	title 			= forms.CharField(max_length=250)
	text  			= forms.CharField(widget=forms.Textarea)
	category 		= forms.ChoiceField(choices=categories)
	visibility 		= forms.ChoiceField(choices=visibility_options)
	draft 			= forms.BooleanField(required=False)

	def clean(self):
		title = self.cleaned_data['title']
		category = self.cleaned_data['category']
		visibility = self.cleaned_data['visibility']
		draft = self.cleaned_data['draft']
		text = self.cleaned_data['text']

		if not (title, text, draft, category, visibility):
			raise forms.ValidationError("Please fill all the fields")

	def save(self, instance, commit=True):
		post = instance
		post.content.title = self.cleaned_data['title']
		post.text = self.cleaned_data['text']
		post.content.draft = self.cleaned_data['draft']
		post.content.category = self.cleaned_data['category']
		post.content.visibility = self.cleaned_data['visibility']
		if commit:
			post.save()
			post.content.save()
		return post

class SnippetUpdateForm(forms.Form):

	text  			= forms.CharField(widget=forms.Textarea, max_length=500)
	category 		= forms.ChoiceField(choices=categories)
	is_question		= forms.BooleanField(required=False)
	visibility 		= forms.ChoiceField(choices=visibility_options)
	draft 			= forms.BooleanField(required=False)

	def clean(self):
		category = self.cleaned_data['category']
		is_question = self.cleaned_data['is_question']
		visibility = self.cleaned_data['visibility']
		draft = self.cleaned_data['draft']
		text = self.cleaned_data['text']

		if len(text) > 500:
			raise forms.ValidationError("Your text should be limited to 500 characters , for more create a post instead")

		if not (text, draft, category, visibility):
			raise forms.ValidationError("Please fill all the fields")

	def save(self, instance, commit=True):
		snippet = instance
		snippet.text = self.cleaned_data['text']
		snippet.content.is_question = self.cleaned_data['is_question']
		snippet.content.draft = self.cleaned_data['draft']
		snippet.content.category = self.cleaned_data['category']
		snippet.content.visibility = self.cleaned_data['visibility']
		if commit:
			snippet.save()
			snippet.content.save()
		return snippet


# class CommentCreationForm(forms.ModelForm):
# 	pass
# 	# class Meta:
# 	# 	model = Comment
# 	# 	fields = ('content',)

class EditCommentForm(forms.Form):
	content 		= forms.CharField(max_length=5000, required=True)
	comment_id 		= forms.IntegerField()

	def clean_content(self):
		content = self.cleaned_data['content']
		return content

	def clean_comment_id(self):
		comment_id = self.cleaned_data['comment_id']
		if comment_id != None:
			return comment_id

# class PollCreationForm(forms.ModelForm):
# 	pass
# 	# class Meta:
# 	# 	model = Poll 
# 	# 	fields = ('title', 'category', 'draft')

# 	# def clean(self):
# 	# 	title = self.cleaned_data['title']
# 	# 	category = self.cleaned_data['category']
# 	# 	draft = self.cleaned_data['draft']
# 	# 	if not (title, draft, category):
# 	# 		raise forms.ValidationError("Please fill all the fields")

# class PollValueCreationForm(forms.ModelForm):
# 	pass
# 	# class Meta:
# 	# 	model = PollValue 
# 	# 	fields = ('value',)

# 	# def clean(self):
# 	# 	value = self.cleaned_data['value']

# 	# 	if not (value):
# 	# 		raise forms.ValidationError("Please fill all the fields")

class PollUpdateForm(forms.Form):	

	title 			= forms.CharField(max_length=250, required=True)
	draft 			= forms.BooleanField(required=False)		

	def clean(self):
		title = self.cleaned_data['title']
		draft = self.cleaned_data['draft']

		if not (title):
			raise forms.ValidationError("Please fill all the fields")

	def save(self, instance, commit=True):
		poll = instance
		print(self.cleaned_data['title'])
		poll.content.title = self.cleaned_data['title']
		print(poll.content.title)
		poll.content.draft = self.cleaned_data['draft']
		if commit:
			poll.content.save()
		return poll
