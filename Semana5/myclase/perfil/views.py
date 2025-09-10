# app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")  # o a donde quieras
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile_edit.html", {"form": form})

@login_required
def profile_view(request):
    return render(request, "profile.html", {"profile": request.user.profile})
