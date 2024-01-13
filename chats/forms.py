from .models import Comment
from django import forms
from .models import Post

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'Content',
                  'featured_image', 'excerpt', 'status', ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 4, 'cols': 30}),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['status'].initial = 1
        self.fields['title'].widget.attrs.update({'id': 'id_title'})
        self.fields['slug'].widget.attrs.update({'id': 'id_slug'})