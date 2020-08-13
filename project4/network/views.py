import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import Count, Q
from django.core.paginator import Paginator

from .models import User, Post, Following


def index(request, message=None):
    posts = Post.objects.order_by("-date").all().annotate(
        num_likes=Count("likes"),
        user_likes=Count("likes", filter=Q(likes=user.id))
    )
    paginator = Paginator(posts, 10) # Show 10 posts per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "message": message
        })


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):
    profile_user = User.objects.filter(username=username).annotate(
        num_targets=Count("targets"),
        num_followers=Count("followers")
        ).first()
    posts = Post.objects.order_by("-date").filter(user=profile_user).annotate(
        num_likes=Count("likes"),
        user_likes=Count("likes", filter=Q(likes=user.id))
    )
    user = request.user
    # Check if current user is following profiled user
    follow = profile_user.followers.filter(follower_id=user.id)

    if follow:
        is_following = True
    else:
        is_following = False

    paginator = Paginator(posts, 10) # Show 10 posts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "is_following": is_following,
        "page_obj": page_obj,
    })


@login_required
def follows(request):
    user = request.user
    # Query for users following targets for filtering posts
    follows = Following.objects.filter(follower_id=user.id).values("target_id")
    posts = Post.objects.order_by("-date").filter(user__in=follows).annotate(
        num_likes=Count("likes"),
        user_likes=Count("likes", filter=Q(likes=user.id))
    )
    print(posts.values())
    paginator = Paginator(posts, 10) # Show 10 posts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/follows.html", {
        "page_obj": page_obj,
    })


@login_required
def create_post(request):
    if request.method == "POST":
        # Gather data and save post, return error if save fails.
        text = request.POST["text"]
        text_length = len(text)
        user = request.user
        print(text_length)

        # For some reason django doesnt validate max_length on textfields so I built it here.
        if ( text_length > 500 ) or ( text_length < 5 ):
            message = "Post must be more than 5 characters and less than 500!"
            return HttpResponseRedirect(reverse("index_message", kwargs={"message": message}))

        post = Post(
            user=user,
            text=text
        )

        post.save()

        return HttpResponseRedirect(reverse("index"))


@login_required
def follow_user(request):
    data = json.loads(request.body)
    # get json data and determine if we add or remove m2m relation
    target = data.get("target")
    follower = request.user

    if request.method == "DELETE":
        follow = get_object_or_404(Following, target=target, follower=follower)
        try:
            follow.delete()
        except IntegrityError:
            return JsonResponse({
                "error": "Delete following unsuccessful, check if right data!"
            }, status=400)
        return JsonResponse({
            "success": "Delete following successful!"
        }, status=200)
    elif request.method == "PUT":
        follow = Following(
            target=target,
            follower=follower
        )
        try:
            follow.save()
        except IntegrityError:
            return JsonResponse({
                "error": "Save following unsuccessful, check if right data!"
            }, status=400)
        return JsonResponse({
            "success": "Save following successful!"
        }, status=201)
    else:
        return JsonResponse({
            "error": "Must use PUT or DELETE."
        }, status=400)


@login_required
def like_post(request):
    # get json data to query db for post objects, and determine if we add or remove m2m relation
    data = json.loads(request.body)
    post_id = data.get("post_id")
    liker = request.user
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "DELETE":
        try:
            post.likes.remove(liker)
        except IntegrityError:
            return JsonResponse({
                "error": "Delete like unsuccessful, check if right data!"
            }, status=400)
        return JsonResponse({
            "success": "Delete like successful!"
        }, status=200)
    elif request.method == "PUT":
        try:
            post.likes.add(liker)
        except IntegrityError:
            return JsonResponse({
                "error": "Save like unsuccessful, check if right data!"
            }, status=400)
        return JsonResponse({
            "success": "Save like successful!"
        }, status=201)
    else:
        return JsonResponse({
            "error": "Must use PUT or DELETE."
        }, status=400)


@login_required
def edit_post(request):
    if request.method != "PUT":
        return JsonResponse({
            "error": "Must use PUT to edit post."
        }, status=400)
    else:
        data = json.loads(request.body)
        post_id = data.get("post_id")
        post_text = data.get("text")
        user = request.user
        # make sure the user editing the post is the creator
        post = get_object_or_404(Post, pk=post_id, user=user)

        post.text = post_text
        try:
            post.save()
        except IntegrityError:
            return JsonResponse({
                "error": "Post cant be updated!"
            }, status=400)
        return JsonResponse({
            "success": "Post updated!",
            "post": post
        }, status=200)