import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse

from allauth.socialaccount.models import SocialAccount
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from blog.models import PersonalBlog, Post


FEEDBACK_CHOICES = (
    ('N', 'New'),
    ('R', 'Replied'),
)


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides selfupdating
    created and modified fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Feedback(models.Model):
    """
    Collect feedback from users about bugs & enhancements
    """
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    feedback = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.name, self.email)


class User(AbstractUser):
    """
    Extended User class
    """
    def get_user_image_upload_path(instance, filename):
        return os.path.join('users/' + str(instance.id) + '/' + filename)

    bio = models.CharField(max_length=1000, blank=True, null=True,
        help_text="Let people know who's behind the articles.")
    image = ProcessedImageField(blank=True, null=True,
                               upload_to=get_user_image_upload_path,
                               processors=[ResizeToFill(250, 250)],
                               format='JPEG',
                               options={'quality': 70},
                               help_text="A nice picture of yours truly")

    def __str__(self):
        return self.email

    def user_blog(self):
        # detect if the current user has started their own blog
        try:
            blog = PersonalBlog.objects.get(owner=self)
            return blog
        except PersonalBlog.DoesNotExist:
            return None
