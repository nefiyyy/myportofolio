from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.models import Experience, Certification
from main.forms import ExperienceForm, CertificationForm

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
    json_response = get_experience_json(request)
    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    experiences = [exp.object for exp in experiences]

    title_query = request.GET.get("title", "").strip()
    context = {
        "name": "Nafisa Naila Andian",
        "experience_list": experiences,
        "title_query": title_query,
    }
    return render(request, "experience.html", context)

def show_certification(request):
    json_response = get_certification_json(request)
    certifications = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    certifications = [cert.object for cert in certifications]

    context = {
        "name": "Nafisa Naila Andian",
        "certification_list": certifications,
    }
    return render(request, "certification.html", context)

def show_certification_detail(request, id):
    certification = get_object_or_404(Certification, pk=id)
    context = {
        "name": "Nafisa Naila Andian",
        "certification": certification,
    }
    return render(request, "certification_detail.html", context)

def create_experience(request):
    form = ExperienceForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Pengalaman baru berhasil ditambahkan!")
            return redirect("main:show_experience")

    context = {
        "name": "Nafisa Naila Andian",
        "form": form,
    }
    return render(request, "experience_form.html", context)

def create_certification(request):
    form = CertificationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Sertifikasi baru berhasil ditambahkan!")
            return redirect("main:show_certification")

    context = {
        "name": "Nafisa Naila Andian",
        "form": form,
    }
    return render(request, "certification_form.html", context)

def edit_certification(request, id):
    certification = get_object_or_404(Certification, pk=id)
    form = CertificationForm(request.POST or None, instance=certification)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Sertifikasi berhasil diubah!")
            return redirect("main:show_certification")

    context = {
        "name": "Nafisa Naila Andian",
        "form": form,
        "is_edit": True,
    }
    return render(request, "certification_form.html", context)

def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")

def get_certification_json(request):
    certifications = Certification.objects.all()
    certifications_json = serializers.serialize("json", certifications)
    return HttpResponse(certifications_json, content_type="application/json")

def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
        return redirect("main:show_experience")
    return redirect("main:show_experience")

def delete_certification(request, id):
    certification = get_object_or_404(Certification, pk=id)
    if request.method == "POST":
        certification.delete()
        messages.success(request, "Sertifikasi berhasil dihapus!")
    return redirect("main:show_certification")