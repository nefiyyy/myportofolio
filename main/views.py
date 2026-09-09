from django.shortcuts import render

from django.shortcuts import render
from main.models import Experience

def show_main(request):
    context = {
        "name": "Nafisa Naila Andian",
        "npm": "2506657125",
        "study_program": "Sistem Informasi",
        "bio": (
            "Don't stop believing."
        ),
    }
    return render(request, "index.html", context)

def show_experience(request):
    context = {
        "name": "Nafisa Naila Andian",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)
