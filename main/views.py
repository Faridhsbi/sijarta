from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

# # Create your views here.

@login_required(login_url='/auth')
def show_main(request):
    context = {"user": request.user}   
    return render(request, "main.html", context)