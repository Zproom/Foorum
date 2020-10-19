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
from django.forms import ModelForm, Textarea, ClearableFileInput
from django.core.paginator import Paginator
from django.db.models import Count
from .models import User, Post, Board
from django.http import HttpResponseBadRequest


# Defines a form for creating posts. Comments are created 
# using JavaScript
class NewPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'thumb', 'video']
        widgets = {
            'content': Textarea(
                attrs={
                    'id': 'post-textarea',
                    'placeholder': 'Start typing your thoughts here...'
                }
            ),
            'thumb': ClearableFileInput(
                attrs={
                    'id': 'image-upload-button'
                }
            ),
            'video': Textarea(
                attrs={
                    'id': 'post-textarea-small',
                    'placeholder': 'Add a link to a YouTube video or SoundCloud song (optional)...'
                }
            )
        }
        labels = {
            'content': '',
            'thumb': 'Attach an Image (Optional)',
            'video': ''
        }


# Defines a form for creating a board
class NewBoardForm(ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'thumb', 'description']
        widgets = {
            'name': Textarea(
                attrs={
                    'id': 'post-textarea-small',
                    'placeholder': 'Enter the name of your board.'
                }
            ),
            'thumb': ClearableFileInput(
                attrs={
                    'id': 'image-upload-button'
                }
            ),
            'description': Textarea(
                attrs={
                    'id': 'post-textarea',
                    'placeholder': 'Enter a description for your board.'
                }
            )
        }
        labels = {
            'name': '',
            'thumb': 'Attach an Image (Optional)',
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
        board = NewBoardForm(request.POST, request.FILES)

        # Error handling
        if board.is_valid():
            new_board = Board(
                name=board.cleaned_data.get("name"),
                thumb=board.cleaned_data.get("thumb"),
                description=board.cleaned_data.get("description"))
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

    # Variable that is used to display the appropriate elements
    # of the posts.html template
    board_page = True

    # Query for requested board
    try:
        board = Board.objects.get(pk=board_id)
    except Board.DoesNotExist:
        return HttpResponse("Error: Page does not exist.")

    # Check the sorting criteria. Order the posts accordingly and paginate.
    # If no GET parameter is supplied, set sort to "" (sort by new to old)
    sort = request.GET.get("q", "")
    if sort == "likes_high_low":
        posts = board.posts.filter(parent=None) \
            .annotate(num_likes=Count('like_users')).order_by("-num_likes")
        page_obj = paginate(request, posts)
    elif sort == "likes_low_high":
        posts = board.posts.filter(parent=None) \
            .annotate(num_likes=Count('like_users')).order_by("num_likes")
        page_obj = paginate(request, posts)
    elif sort == "comments_high_low":
        posts = board.posts.filter(parent=None) \
            .annotate(num_comments=Count('child_posts')).order_by('-num_comments')
        page_obj = paginate(request, posts)
    elif sort == "comments_low_high":
        posts = board.posts.filter(parent=None) \
            .annotate(num_comments=Count('child_posts')).order_by('num_comments')
        page_obj = paginate(request, posts)
    elif sort == "timestamp_new_old":
        posts = board.posts.filter(parent=None) \
            .order_by("-timestamp")
        page_obj = paginate(request, posts)
    elif sort == "timestamp_old_new":
        posts = board.posts.filter(parent=None) \
            .order_by("timestamp")
        page_obj = paginate(request, posts)
    else:
        posts = board.posts.filter(parent=None) \
            .order_by("-timestamp")
        page_obj = paginate(request, posts)

    # User creates a post
    if request.method == "POST":
        post = NewPostForm(request.POST, request.FILES)

        # Error handling
        if post.is_valid():
            new_post = Post(
                author=request.user,
                board=board,
                content=post.cleaned_data.get("content"),
                thumb=post.cleaned_data.get("thumb"),
                video=post.cleaned_data.get("video"))
            new_post.save()
            return HttpResponseRedirect(reverse(
                "view-board",
                args=(board.id,)))
        else:
            return render(request, "forum/posts.html", {
                "board": board,
                "form": post,
                "page_obj": page_obj,
                "board_page": board_page
            })
    else:
        return render(request, "forum/posts.html", {
            "board": board,
            "form": NewPostForm(),
            "page_obj": page_obj,
            "board_page": board_page
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
    comments = post.child_posts.all().order_by("-timestamp")
    return render(request, "forum/comments.html", {
        "post": post,
        "form": NewPostForm(),
        "comments": comments
    })


# View the user sees after clicking on a username in a post
def view_user(request, username):

    # Variable that is used to display the appropriate elements
    # of the posts.html template
    user_page = True

    # Query for requested user
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse("Error: Page does not exist.")

    # List the posts associated with the profile in reverse chronological
    # order and paginate
    profile_posts = user.posts.filter(parent=None) \
        .order_by("-timestamp")
    page_obj = paginate(request, profile_posts)

    # Check if the user is viewing their own profile
    own_profile = False
    if request.user == user:
        own_profile = True

    # Check if the user is already following this profile and
    # set the button text accordingly
    try:
        already_following = request.user.following \
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
        # profile from their following field
        if already_following:
            request.user.following.remove(user)
            follow_button_text = "Follow"

        # Otherwise, add the profile to the user's following field
        else:
            request.user.following.add(user)
            follow_button_text = "Unfollow"

    # Check the number of users the user follows (following)
    # and the number of followers the user has (followers)
    # and set the grammatical number accordingly
    followers_count = user.following_users.count()
    following_count = user.following.count()
    if followers_count == 1:
        followers_count_text = "1 Follower"
    else:
        followers_count_text = f"{followers_count} Followers"
    if following_count == 1:
        following_count_text = f"{user.username} follows 1 user."
    else:
        following_count_text = f"{user.username} follows " \
                               f"{following_count} users."
    return render(request, "forum/posts.html", {
        "username": user.username,
        "followers_count_text": followers_count_text,
        "following_count_text": following_count_text,
        "own_profile": own_profile,
        "follow_button_text": follow_button_text,
        "page_obj": page_obj,
        "user_page": user_page
    })


# View the user sees after clicking on the Following link
def view_following(request):

    # Variable that is used to display the appropriate elements
    # of the posts.html template
    following_page = True
    following_posts = Post.objects.filter(parent=None) \
        .filter(author__in=request.user.following.all()).order_by("-timestamp")
    page_obj = paginate(request, following_posts)
    return render(request, "forum/posts.html", {
        "page_obj": page_obj,
        "following_page": following_page
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

        # The below code is used to update image files with PUT requests (this is
        # not straightforward with Django). Source: 
        # https://dzone.com/articles/parsing-unsupported-requests-put-delete-etc-in-dja
        # Bug fix: if _load_post_and_files has already been called, for
        # example by middleware accessing request.POST, the below code to
        # pretend the request is a POST instead of a PUT will be too late
        # to make a difference. Also calling _load_post_and_files will result
        # in the following exception:
        # AttributeError: You cannot set the upload handlers after the upload has been processed.
        # The fix is to check for the presence of the _post field which is set
        # the first time _load_post_and_files is called (both by wsgi.py and
        # modpython.py). If it's set, the request has to be 'reset' to redo
        # the query value parsing in POST mode.
        if hasattr(request, '_post'):
            del request._post
            del request._files
        try:
            request.method = "POST"
            request._load_post_and_files()
            request.method = "PUT"
        except AttributeError:
            request.META['REQUEST_METHOD'] = 'POST'
            request._load_post_and_files()
            request.META['REQUEST_METHOD'] = 'PUT'
        request.PUT = request.POST
        if request.is_ajax():
            content = request.PUT['content']
            image = request.FILES.get('img_file')
            video = request.PUT['video_link']

        # Check the content length
        if not content or len(content) > 1000:
            return JsonResponse({
                "error": ("Your post content must not be empty"
                          "and cannot exceed 1000 characters.")
            }, status=400)

        # Update the post or comment fields
        post.content = content
        post.thumb = image
        post.video = video
        post.save()
        return JsonResponse(post.serialize())

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
    if request.is_ajax():
        content = request.POST['content']
        image = request.FILES.get('img_file')
        video = request.POST['video_link']

    # Check the content length
    if not content or len(content) > 1000:
        return JsonResponse({
            "error": ("Your post content must not be empty"
                      "and cannot exceed 1000 characters.")
        }, status=400)

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponse("Error: Post does not exist.")

    # Create a new comment and save it to the database
    comment = Post(
        author=request.user,
        board=post.board,
        parent=post,
        content=content,
        thumb=image,
        video=video
    )
    comment.save()
    return JsonResponse(comment.serialize())


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
            user.is_active = False
            user.save()
        except IntegrityError:
            return render(request, "forum/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "forum/register.html")
