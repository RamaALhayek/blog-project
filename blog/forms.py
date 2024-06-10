from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
  class Meta:
    model = Comment
    fields = ['name', 'email', 'body']

class EmailForm(forms.Form):
    email = forms.EmailField()
    phone = forms.CharField(max_length=20) 
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)

class SearchForm(forms.Form):
    query = forms.CharField()    