import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.forms import ModelForm, Textarea
from django.core.paginator import Paginator
from django.db.models import Count
from .models import User, Post, Board, Comment


# Defines a form for creating posts and comments.
# Since the post and comment models are so similar,
# the post form can be repurposed for new comments
class NewPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image_link']
        widgets = {
            'content': Textarea(
                attrs={
                    'id': 'post-textarea',
                    'placeholder': 'Start typing your thoughts here...'}),
            'image_link': Textarea(
                attrs={
                    'id': 'post-image-link',
                    'placeholder': 'Insert image link (optional)'})
        }
        labels = {
            'content': '',
            'image_link': ''
        }


# Defines a form for creating a board
class NewBoardForm(ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'description']
        widgets = {
            'name': Textarea(
                attrs={
                    'id': 'post-image-link',
                    'placeholder': 'Enter the name of your board.'}),
            'description': Textarea(
                attrs={
                    'id': 'post-textarea',
                    'placeholder': 'Enter a description for your board.'})
        }
        labels = {
            'name': '',
            'description': ''
        }


def index(request):

    # Display a list of all of the Boards
    boards = Board.objects.all()

    # Check if the user has permission to create a new
    # Board. If the user has the required permission,
    # display a form to create a new Board
    if request.user.has_perm('forum.add_board'):
        has_permission = True
    else:
        has_permission = False

    # User creates a board
    if request.method == "POST":
        board = NewBoardForm(request.POST)

        # Error handling
        if board.is_valid():
            new_board = Board(
                name=board.cleaned_data["name"],
                description=board.cleaned_data["description"])
            new_board.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "forum/index.html", {
                "boards": boards,
                "has_permission": has_permission,
                "form": board
            })
    return render(request, "forum/index.html", {
        "boards": boards,
        "has_permission": has_permission,
        "form": NewBoardForm()
    })


# View the user sees after clicking on a Board name on the
# index page
def view_board(request, board_id):

    # Query for requested board
    try:
        board = Board.objects.get(pk=board_id)
    except Board.DoesNotExist:
        return HttpResponse("Error: Page does not exist.")

    # Check the sorting criteria. Order the posts accordingly and paginate.
    # If no GET parameter is supplied, set sort to "" (sort by new to old)
    sort = request.GET.get("q", "")
    if sort == "likes_high_low":
        posts = Post.objects.filter(board=board.id).order_by("-num_likes")
        page_obj = paginate(request, posts)
    elif sort == "likes_low_high":
        posts = Post.objects.filter(board=board.id).order_by("num_likes")
        page_obj = paginate(request, posts)
    elif sort == "comments_high_low":
        posts = Post.objects.filter(board=board.id) \
            .annotate(num_comments=Count('comments')).order_by('-num_comments')
        page_obj = paginate(request, posts)
    elif sort == "comments_low_high":
        posts = Post.objects.filter(board=board.id) \
            .annotate(num_comments=Count('comments')).order_by('num_comments')
        page_obj = paginate(request, posts)
    elif sort == "timestamp_new_old":
        posts = Post.objects.filter(board=board.id).order_by("-timestamp")
        page_obj = paginate(request, posts)
    elif sort == "timestamp_old_new":
        posts = Post.objects.filter(board=board.id).order_by("timestamp")
        page_obj = paginate(request, posts)
    else:
        posts = Post.objects.filter(board=board.id).order_by("-timestamp")
        page_obj = paginate(request, posts)

    # User creates a post
    if request.method == "POST":
        post = NewPostForm(request.POST)

        # Error handling
        if post.is_valid():
            new_post = Post(
                author=request.user,
                board=board,
                content=post.cleaned_data["content"],
                image_link=post.cleaned_data["image_link"])
            new_post.save()
            return HttpResponseRedirect(reverse(
                "view-board",
                args=(board.id,)))
        else:
            return render(request, "forum/board.html", {
                "board": board,
                "form": post,
                "page_obj": page_obj
            })
    else:
        return render(request, "forum/board.html", {
            "board": board,
            "form": NewPostForm(),
            "page_obj": page_obj
        })


# View the user sees after clicking on the Comments button
# in a post (displays comments)
def view_comments(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponse("Error: Post does not exist.")

    # List the comments in reverse chronological order
    comments = Comment.objects.filter(post=post.id).order_by("-timestamp")
    return render(request, "forum/comments.html", {
        "post": post,
        "form": NewPostForm(),
        "comments": comments
    })


# View the user sees after clicking on a username in a post
def view_user(request, username):

    # Query for requested user
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse("Error: Page does not exist.")

    # List the posts associated with the profile in reverse chronological
    # order and paginate
    profile_posts = Post.objects.filter(author=user).order_by("-timestamp")
    page_obj = paginate(request, profile_posts)

    # Check if the user is viewing their own profile
    own_profile = False
    if request.user == user:
        own_profile = True

    # Check if the user is already following this profile and
    # set the button text accordingly
    try:
        already_following = request.user.following.all() \
            .filter(username=username).exists()

    # Handles the case where a user is not signed in
    except:
        already_following = False
    if already_following:
        follow_button_text = "Unfollow"
    else:
        follow_button_text = "Follow"

    # User clicks Follow or Unfollow button
    if request.method == "POST":

        # If the user is already following this profile, remove the
        # profile from their following field. Also, remove the user
        # from the profile user's followers field
        if already_following:
            request.user.following.remove(user)
            user.followers.remove(request.user)
            follow_button_text = "Follow"

        # Otherwise, add the profile to the user's following field and
        # add the user to the profile user's follower field
        else:
            request.user.following.add(user)
            user.followers.add(request.user)
            follow_button_text = "Unfollow"

    # Check the number of users the user follows (following)
    # and the number of followers the user has (followers)
    # and set the grammatical number accordingly
    followers_count = user.followers.count()
    following_count = user.following.count()
    if followers_count == 1:
        followers_count_text = "1 Follower"
    else:
        followers_count_text = f"{followers_count} Followers"
    if following_count == 1:
        following_count_text = f"{user.username} follows 1 user."
    else:
        following_count_text = (f"{user.username} follows" 
                                "{following_count} users.")
    return render(request, "forum/user.html", {
        "username": user.username,
        "followers_count_text": followers_count_text,
        "following_count_text": following_count_text,
        "own_profile": own_profile,
        "follow_button_text": follow_button_text,
        "page_obj": page_obj
    })


# View the user sees after clicking on the Following link
def view_following(request):
    following_posts = Post.objects \
        .filter(author__in=request.user.following.all()).order_by("-timestamp")
    page_obj = paginate(request, following_posts)
    return render(request, "forum/following.html", {
        "page_obj": page_obj
    })


# Paginates a list of posts or comments
def paginate(request, items):
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


# Handles requests to the post API route
@login_required
def post(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return post information
    if request.method == "GET":
        return JsonResponse(post.serialize())

    # Update the post's content, image link, or like count
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("content") is not None:
            post.content = data["content"]
        if data.get("image_link") is not None:
            post.image_link = data["image_link"]
        if data.get("like") is not None:

            # Check if the viewer has already liked the post
            if post in request.user.likes.all():
                post.num_likes -= 1
            else:
                post.num_likes += 1
        post.save()
        return HttpResponse(status=204)

    # Post must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


# Handles requests to the user API route
@login_required
def user(request, username):

    # Query for requested user
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    # Return user information
    if request.method == "GET":
        return JsonResponse(user.serialize())

    # Update the user's likes field
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("post_id") is not None:
            post = Post.objects.get(pk=data["post_id"])

            # Check if the viewer has already liked the post
            if post in request.user.likes.all():
                user.likes.remove(post)
            else:
                user.likes.add(post)

        # Update the user's comment likes field
        elif data.get("comment_id") is not None:
            comment = Comment.objects.get(pk=data["comment_id"])

            # Check if the viewer has already liked the comment
            if comment in request.user.comment_likes.all():
                user.comment_likes.remove(comment)
            else:
                user.comment_likes.add(comment)
        return HttpResponse(status=204)

    # User must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


# Handles requests to the compose comment API route
@login_required
def compose_comment(request, post_id):

    # Composing a new comment must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check the content length and image link length
    data = json.loads(request.body)
    content = data.get("content", "")
    image_link = data.get("image_link", "")
    if not content or len(content) > 1000:
        return JsonResponse({
            "error": ("Your post content must not be empty"
                      "and cannot exceed 1000 characters.")
        }, status=400)
    if len(image_link) > 3000:
        return JsonResponse({
            "error": "Your image URL cannot exceed 3000 characters."
        }, status=400)

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponse("Error: Post does not exist.")

    # Create a new comment and save it to the database
    comment = Comment(
        author=request.user,
        post=post,
        content=content,
        image_link=image_link
    )
    comment.save()

    return JsonResponse(comment.serialize())


# Handles requests to the comment API route
@login_required
def comment(request, comment_id):

    # Query for requested comment
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({"error": "Comment not found."}, status=404)

    # Return comment information
    if request.method == "GET":
        return JsonResponse(comment.serialize())

    # Update the comment's content, image link, or like count
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("content") is not None:
            comment.content = data["content"]
        if data.get("image_link") is not None:
            comment.image_link = data["image_link"]
        if data.get("like") is not None:

            # Check if the viewer has already liked the comment
            if comment in request.user.comment_likes.all():
                comment.num_likes -= 1
            else:
                comment.num_likes += 1
        comment.save()
        return HttpResponse(status=204)

    # Post must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "forum/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "forum/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "forum/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "forum/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "forum/register.html")
