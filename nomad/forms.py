from django import forms
from .models import Feedback, Question

class FeedbackForm(forms.ModelForm):

    class Meta:
        model = Feedback
        fields = ('content',)

    def clean(self):
        if self.is_valid():
            content = self.cleaned_data['content'].replace(" ","")
            if len(content) <= 20:
                raise forms.ValidationError("Your feedback should be over 20 characters in length")

class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('question',)

    def clean(self):
        if self.is_valid():
            question = self.cleaned_data['question'].replace(" ","")
            if len(question) <= 20:
                raise forms.ValidationError("Your question should be over 20 characters in length , be more detailed")

