from django.shortcuts import render
from main.models import Experience, Certification

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

def show_certification(request):
    context = {
        "name": "Nafisa Naila Andian",
        "certification_list": Certification.objects.all(),
    }
    return render(request, "certification.html", context) 

def show_certification_detail(request, id):
    certification = Certification.objects.get(pk=id)
    context = {
        "name": "Nafisa Naila Andian",
        "certification": certification,
    }
    return render(request, "certification_detail.html", context)
