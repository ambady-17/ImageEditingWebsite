from django import forms
from .models import ImageUploadModel


class ImageUploadForm(forms.ModelForm):
  class Meta:
	  model = ImageUploadModel
	  fields = ('description', 'document' )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Make description optional for AJAX uploads
    self.fields['description'].required = False