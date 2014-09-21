import requests
import json
import datetime

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.db import IntegrityError
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.http import HttpResponseRedirect, HttpResponse

from main.utils import get_json_objects, get_json
from main.models import UserProfile
from blog.models import PersonalBlog, Post, Topic, UserFavorite
from blog.forms import BlogCreateForm, BlogEditForm, BlogPostCreateForm, BlogPostEditForm
from blog.utils import get_favorites, get_wave_blog_list

@staff_member_required
def blogs(request):
    '''
    show the home for searching personal blogs
    '''

    # get list of all blogs
    blogs_url = settings.BASE_URL + "/api/v1/blog/"
    blogs = get_json_objects(blogs_url)

    return render(request, "blogcontent/home.html", {'blogs':blogs})


def blog(request, **kwargs):
    '''
    individual blog page
    '''
    blog_slug = kwargs['blog']
    blog = get_object_or_404(PersonalBlog, slug=blog_slug)

    # check if the blog is in a user's blog_wave
    wave_bool_list = get_wave_blog_list(request.user)

    # get the post with a lat and a long that we want to center on. Get the
    # latest post that has a lat and a long
    eligible_posts = []
    for p in blog.post_set.all():
        if p.lat and p.long:
            eligible_posts.append(p)

    if eligible_posts:
        # assign the most recent post's loc to center loc
        center_lat = eligible_posts[0].lat
        center_long = eligible_posts[0].long
    else:
        center_lat = None
        center_long = None

    return render(request, "blogcontent/blog.html",
                  {'blog':blog, 'wave_bool_list':wave_bool_list, 'center_lat':center_lat,
                   'center_long':center_long})


def explore(request, **kwargs):
    '''
    Search for blog posts. Can search by different places/topics.
    '''

    # used in context to display selection options
    topics = Topic.objects.all()
    posts = Post.objects.all()

    # remove, for testing
    topic = ""
    place = ""

    if request.method == "POST":
        # filter requests by topic and/or place
        place = request.POST["place"]
        topic = request.POST["topic"]

        if place and topic:
            # user put in both place and topic filters
            posts = posts.filter(place=place, topic__title=topic)
        if place:
            # user put in a place filter
            posts = posts.filter(place=place)
        elif topic:
            # user put in a topic filter
            posts = posts.filter(topic__title=topic)
        else:
            # user did not put in any search criteria, take all posts
            pass

    return render(request, "blogcontent/explore.html",
                  {'posts':posts, 'topics':topics, 'topic':topic, 'place':place})


def post(request, **kwargs):
    '''
    show an individual blog post
    '''
    post_slug = kwargs['post']
    post = get_object_or_404(Post, slug=post_slug)
    id = post.id

    # record the view
    post_orm = get_object_or_404(Post, id=id)
    views = post_orm.views + 1
    post_orm.views = views
    post_orm.save()

    # get other posts to display in the template
    other_posts = Post.objects.filter(blog=post.blog).exclude(id=id)[:4]

    # detect if post is in the user's favorites
    favorites = get_favorites(request.user)

    return render(request, "blogcontent/post.html", {'post':post, 'other_posts':other_posts,
                                                     'favorites':favorites})


def topic(request, **kwargs):
    # return the posts that are listed under a certain topic
    topic_slug = kwargs["topic"]
    topic = Topic.objects.get(slug=topic_slug)
    posts = Post.objects.filter(topics__in=[topic.id])

    return render(request, "blogcontent/topic.html", {'posts':posts, 'topic':topic})


def wave(request):
    '''
    show the articles that a user has added to their stream
    '''
    user = request.user

    if user.is_authenticated():

        # get the blogs that are in a user's wave
        wave_blog_list = get_wave_blog_list(request.user)

        profile = get_object_or_404(UserProfile, user=user)
        blogs = profile.blog_wave.all()

        post_set = []
        for b in blogs:
            for p in b.post_set.all():
                post_set.append(p)

        return render(request, "blogcontent/wave.html",
                      {'blogs':blogs, 'posts':post_set, 'wave_blog_list':wave_blog_list})
    else:
        # user not logged in
        wave_blog_list = None
        return render(request, "blogcontent/wave_register.html", {})


@login_required
def add_wave(request, **kwargs):
    '''
    add a blog to a user's blog wave
    '''
    if request.method == "POST":
        if request.is_ajax():
            id = kwargs["pk"]
            action = kwargs["action"]

            profile = get_object_or_404(UserProfile, user=request.user)
            blog = get_object_or_404(PersonalBlog, id=id)

            if action == "add":
                # add the blog to the current user's blog wave
                profile.blog_wave.add(blog)
                return HttpResponse("added blog " + blog.title)
            elif action == "remove":
                # remove the blog from the current user's blog wave
                profile.blog_wave.remove(blog)
                return HttpResponse("removed blog " + blog.title)
        else:
            return HttpResponse("Not an ajax post")
    else:
        return HttpResponse("Not a Post request")

@login_required
def create_blog(request):
    '''
    have a user create a new blog
    '''
    status = ""
    alert_message = ""
    form = BlogCreateForm()

    if request.method == "POST":
        # attempt save the blog object through the API
        form = BlogCreateForm(request.POST, request.FILES)

        if form.is_valid():
            title = request.POST["title"]
            description = request.POST["description"]

            try:
                blog = PersonalBlog(
                    owner=request.user,
                    title=title,
                    description=description
                )
                blog.save()

                # saved and redirect to create a post
                status = "new"
                form = BlogEditForm(request.POST, request.FILES)

                return render(request, "blogcontent/dashboard.html", {'status':'new', 'myblog':blog,
                                                                      'form':form})

            except IntegrityError:
                status = "error"
                alert_message = "That blog name is already taken, please choose another."
                pass
        else:
            alert_message = "Your blog data was not valid! Please fix the errors."
            status = "error"

    return render(request, "blogcontent/blog_create.html", {'form':form, 'status':status,
                                                    'alert_message':alert_message})


@login_required
def create_post(request):
    '''
    user will create a blog post
    '''
    status = ""
    alert_message = ""
    form = BlogPostCreateForm()

    if request.method == "POST":
        # attempt save the blog object
        form = BlogPostCreateForm(request.POST)

        if form.is_valid():
            try:
                user = request.user

                if request.POST['topic']:
                    topic = Topic.objects.get(id=request.POST["topic"])
                else:
                    topic = None

                post = Post(
                    author = user,
                    blog = PersonalBlog.objects.get(owner=user),
                    title = request.POST["title"],
                    body = request.POST["body"],
                    topic = topic,
                    active = request.POST["active"],
                    place_id = request.POST["place_id"],
                    place = request.POST["place"]
                )
                post.save()

                # saved and redirect to view the post
                post_url = reverse('blog-post', kwargs={'blog':post.blog.slug, 'post':slugify(post.title)})
                return HttpResponseRedirect(post_url)

            except IntegrityError:
                status = "error"
                alert_message = "You have already used that blog post title. Please choose another title."
                pass
        else:
            alert_message = form.errors
            status = "error"

    return render(request, "blogcontent/post_create.html", {'form':form, 'status':status,
                                                    'alert_message':alert_message})


@login_required
def edit_post(request, **kwargs):
    '''
    edit an existing blog post
    '''

    # check to make sure current user is the author of this post
    id = kwargs['pk']
    post = get_object_or_404(Post, id=id)
    status = ""
    alert_message = ""

    if post.author == request.user:
        if request.method == "POST":
            # save the edited post instance
            form = BlogPostEditForm(request.POST, instance=post)

            if 'submit' in request.POST:
                # user is saving the updated data. They are not trying to delete.

                if form.is_valid():
                    try:
                        user = request.user

                        if request.POST['topic']:
                            topic = Topic.objects.get(id=request.POST["topic"]),
                        else:
                            topic = None

                        # begin saving the model instance
                        form.topic = topic
                        form.save()

                        # saved and redirect to view the post
                        post_url = reverse('blog-post', kwargs={'blog':post.blog.slug, 'post':slugify(post.title)})
                        return HttpResponseRedirect(post_url)

                    except IntegrityError:
                        status = "error"
                        alert_message = "You have already used that blog post title. Please choose another title."
                        pass
                else:
                    alert_message = "Your blog post data was not valid! Please fix the errors."
                    status = "error"
            elif 'delete' in request.POST:
                # user is deleting a post
                form.delete()
        else:
            # request get, show the form with default

            form = BlogPostEditForm(instance=post)
            return render(request, "blogcontent/post_edit.html", {'post':post, 'form':form})
    else:
        # request user is not the author
        return render(request, "blogcontent/post_edit.html", {})

    return render(request, "blogcontent/post_edit.html", {'form':form, 'status':status,
                                                    'alert_message':alert_message})


@login_required
def dashboard(request, **kwargs):
    '''
    perform managerial and administrative tasks for a blog. Only
    available to the blog owner
    '''
    alert_message = ""
    status = ""

    blog_slug = kwargs['blog']
    blog = get_object_or_404(PersonalBlog, slug=blog_slug)
    blog_url = settings.BASE_URL + "/api/v1/blog/?slug=" + blog_slug + \
        "&owner__username=" + request.user.username
    myblog = get_json_objects(blog_url)[0]

    # handle the form submit to update blog data
    form = BlogEditForm(instance=blog)
    if request.method == "POST":
        if blog.owner == request.user:
            form = BlogEditForm(request.POST, request.FILES, instance=blog)

            if form.is_valid():
                form.save()

                alert_message = "Your blog data has been updated successfully"
                status = "saved"
            else:
                alert_message = "There was a problem saving the data you entered. Please correct the errors above."
                status = "error"
        else:
            alert_message = "You do not have access to update this blog's information."
            status = "error"


    return render(request, "blogcontent/dashboard.html", {'myblog':myblog, 'alert_message':alert_message,
                                                          'status':status, 'form':form})


@login_required
def favorites(request):
    '''
    display a list of posts that a user has marked as favorite
    '''
    favorites = get_favorites(request.user)['objects']

    # favorites_url = settings.BASE_URL + "/api/v1/userfavorite/?user__username=" + user.username
    # favorites = get_json(favorites_url)

    return render(request, "blogcontent/favorites.html", {'favorites':favorites})