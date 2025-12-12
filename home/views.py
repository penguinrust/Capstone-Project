from django.shortcuts import render


def home(request):
    """Display home page"""
    return render(request, 'index.html')
