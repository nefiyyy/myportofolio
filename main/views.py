from django.shortcuts import render

from main.models import Experience

def show_main(request):
    context = {
        "name": "Nafisa Naila Andian",
        "npm": "2506657125",
        "study_program": "Sistem Informasi",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik pada pengembangan perangkat lunak dan pendidikan."
        ),
    }
    return render(request, "index.html", context)

def show_experience(request):
    context = {
        "name": "Nafisa Naila Andian",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)
