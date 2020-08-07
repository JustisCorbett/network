import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator

from .models import User, Post, Following


def index(request):
    posts = Post.objects.order_by("-date").annotate(num_likes=Count('likes')).all()
    paginator = Paginator(posts, 10) # Show 10 posts per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {"page_obj": page_obj})


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


@login_required
def create_post(request):

    if request.method == "POST":
        # Gather data and save post, return error if save fails
        text = request.POST["text"]
        user = request.user

        post = Post(
            user=user,
            text=text
        )

        try:
            post.save()
        except IntegrityError:
            return render(request, "network/create_post.html", {
                "message": "Post exceeds max amount of characters!"
                })

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/create_post.html")


@login_required
def follow(request):
    
    if request.method != "PUT":
        return JsonResponse({
            "error": "PUT request required."
        }, status=405)
    else:
        
        data = json.loads(request.body)
        # get json data to determine if we add or remove m2m relation
        is_following = data.get("is_following")
        target = data.get("target")
        follower = request.user
        if is_following:
            try:
                follow = Following.objects.get(target=target, follower=follower).delete()
            except IntegrityError:
                return JsonResponse({
                    "error": "Delete following unsuccessful, check if right data."
                }, status=400)
            return JsonResponse({
                "success": "Delete following successful"
            }, status=200)
        else:
            follow = Following(
                target=target,
                follower=follower
            )
            try:
                follow.save()
            except IntegrityError:
                return JsonResponse({
                    "error": "Save following unsuccessful, check if right data."
                }, status=400)
            return JsonResponse({
                "success": "Save following successful"
            }, status=201)


@login_required
def like(request):
    
    if request.method != "PUT":
        return JsonResponse({
            "error": "PUT request required."
        }, status=405)
    else:
        # get json data to query db for post objects, and determine if we add or remove m2m relation
        data = json.loads(request.body)
        is_following = data.get("is_liked")
        post_id = data.get("post_id")

        liker = request.user
        post = Post.objects.get(pk=post_id)

        if is_following:
            try:
                post.likes.remove(liker)
            except IntegrityError:
                return JsonResponse({
                    "error": "Delete like unsuccessful, check if right data."
                }, status=400)
            return JsonResponse({
                "success": "Delete like successful"
            }, status=200)
        else:
            try:
                post.likes.add(liker)
            except IntegrityError:
                return JsonResponse({
                    "error": "Save like unsuccessful, check if right data."
                }, status=400)
            return JsonResponse({
                "success": "Save like successful"
            }, status=201)