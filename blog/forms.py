from django.forms import ModelForm
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit, Div

from .models import Post, PersonalBlog


class PostHelper(FormHelper):
    layout = Layout(
        Fieldset(
            '',
            Div(
                Div('title', css_class="col s12 m4"),
                Div('headline', css_class="col s12 m8"),
                css_class="row"
            ),
            Div(
                Div('image', css_class="col m6 s12"),
                Div('image_description', css_class="col m6 s12"),
                css_class="row"
            ),
            Div(
                Div('public', css_class="col m6 offset-m3 s12"),
                css_class="row"
            ),
            Div(
                Div('body', css_class="col s12"),
                css_class="row"
            )
        ),
        ButtonHolder(
            Submit('submit', 'Create', css_class='btn right hover-right')
        )
    )

class EditPostHelper(FormHelper):
    "Need to change the id of various fields because they break JS"
    layout = Layout(
        Fieldset(
            '',
            Div(
                Div('title', css_class="col s12 m4"),
                Div('headline', css_class="col s12 m8"),
                css_class="row"
            ),
            Div(
                Div('image', css_class="col m6 s12"),
                Div('image_description', css_class="col m6 s12"),
                css_class="row"
            ),
            Div(
                Div(Field('public', id="id_edit_public"),
                    css_class="col m6 offset-m3 s12"),
                css_class="row"
            ),
            Div(
                Div(Field('body', id="id_edit_body"), css_class="col s12"),
                css_class="row"
            )
        ),
        ButtonHolder(
            Submit('submit', 'Save', css_class='btn right hover-right')
        )
    )

class PostCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostCreateForm, self).__init__(*args, **kwargs)
        self.helper = PostHelper()

    class Meta:
        model = Post
        exclude = ['author', 'blog', 'lat', 'lng', 'place',
            'place_id']


class PostEditForm(PostCreateForm):
    def __init__(self, *args, **kwargs):
        super(PostEditForm, self).__init__(*args, **kwargs)
        self.helper = EditPostHelper()
        self.helper.form_id = "edit-post-form"
        self.helper.form_action = reverse('blog-edit-post', kwargs={'pk': self.instance.id})

    class Meta:
        model = Post
        exclude = ['author', 'blog', 'lat', 'lng', 'place',
            'place_id']

class BlogEditForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlogEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "edit-blog-form"
        self.helper.form_action = reverse('blog-edit', kwargs={'pk': self.instance.id})
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('title', css_class="col m6 s12"),
                    Div('image', css_class="col m6 s12"),
                    css_class="row"
                ),
                Div(
                    Div('description', css_class="col s12"),
                    css_class="row"
                ),
                Div(
                    Div('twitter', css_class="col s12 m6"),
                    Div('twitter_widget_id', css_class="col s12 m6"),
                    Div('facebook', css_class="col s12 m6"),
                    css_class="row"
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Save', css_class='btn right hover-right')
            )
        )

    class Meta:
        model = PersonalBlog
        exclude = ['owner',]
