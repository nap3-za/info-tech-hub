
from django import forms
from .models import Resource

class ResourceForm(forms.ModelForm):

	class Meta:
		model = Resource
		fields = ('title', 'description', 'link', 'res_timestamp', 'res_format')
    
	def clean(self):
		if self.is_valid():
			desc = self.cleaned_data['description'].replace(" ","")
			res_timestamp = self.cleaned_data['res_timestamp']
			
			try:
				if int(res_timestamp) < 1950 or int(res_timestamp) > 2022:
					raise forms.ValidationError("Your resource year is incorrect")
			except Exceptrion as e:
				print(f"[>> res_form {e}")
				
			if len(desc) <= 20:
				raise forms.ValidationError("Your title should be over 20 letters")

class UpdateResourceForm(forms.ModelForm):

    class Meta:
        model = Resource
        fields = ('title', 'image', 'description', 'link', 'res_format')
    
    def clean(self):
        if self.is_valid():
            title = self.cleaned_data['title']
            if len(title) <= 5:
                raise forms.ValidationError("Your title should be over 5 letters")
            

    def save(self,resource, commit=True):
        resource.title = self.cleaned_data['title']
        resource.description = self.cleaned_data['description']
        resource.link = self.cleaned_data['link']
        resource.image = self.cleaned_data['image']
        if commit:
            resource.save()
        return resource

