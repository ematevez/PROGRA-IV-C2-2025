from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer
from django.shortcuts import render, redirect
from .forms import UserForm

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

def user_form(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/api/users/")  # redirige a la lista JSON
    else:
        form = UserForm()
    return render(request, "user_form.html", {"form": form})
