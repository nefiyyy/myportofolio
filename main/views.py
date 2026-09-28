import datetime
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from main.models import Experience, Certification
from main.forms import ExperienceForm, CertificationForm


def is_editor(user):
    """True kalau user sudah login dan termasuk grup Editor."""
    return user.is_authenticated and user.groups.filter(name="Editor").exists()


def show_main(request):
    last_login = request.COOKIES.get("last_login", "Belum ada sesi login / Cookie tidak ditemukan")
    context = {
        "name": "Nafisa Naila Andian",
        "npm": "2506657125",
        "study_program": "Sistem Informasi",
        "bio": "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik pada pengembangan perangkat lunak dan pendidikan.",
        "last_login": last_login,
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
        "is_editor": is_editor(request.user),
    }
    return render(request, "certification.html", context)


def show_certification_detail(request, id):
    certification = get_object_or_404(Certification, pk=id)
    context = {
        "name": "Nafisa Naila Andian",
        "certification": certification,
        "is_editor": is_editor(request.user),
    }
    return render(request, "certification_detail.html", context)


# Tambah & hapus: hanya superuser (pemilik portofolio)
@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied

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


@login_required(login_url="/login/")
def create_certification(request):
    if not request.user.is_superuser:
        raise PermissionDenied

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


# Edit: superuser ATAU editor
@login_required(login_url="/login/")
def edit_certification(request, id):
    if not (request.user.is_superuser or is_editor(request.user)):
        raise PermissionDenied

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


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
    return redirect("main:show_experience")


@login_required(login_url="/login/")
def delete_certification(request, id):
    if not request.user.is_superuser:
        raise PermissionDenied

    certification = get_object_or_404(Certification, pk=id)
    if request.method == "POST":
        certification.delete()
        messages.success(request, "Sertifikasi berhasil dihapus!")
    return redirect("main:show_certification")


# API JSON: publik, relasi user tampil sebagai username (bukan id database)
def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experiences_json = serializers.serialize("json", experiences, use_natural_foreign_keys=True)
    return HttpResponse(experiences_json, content_type="application/json")


def get_certification_json(request):
    certifications = Certification.objects.all()
    certifications_json = serializers.serialize("json", certifications, use_natural_foreign_keys=True)
    return HttpResponse(certifications_json, content_type="application/json")


# Autentikasi
def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")
    return render(request, "register.html", {"name": "Nafisa Naila Andian", "form": form})


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        response.set_cookie("last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return response
    return render(request, "login.html", {"name": "Nafisa Naila Andian", "form": form})


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


# Star: semua user yang sudah login boleh
@login_required(login_url="/login/")
def toggle_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        if request.user in experience.starred_by.all():
            experience.starred_by.remove(request.user)
        else:
            experience.starred_by.add(request.user)
    return redirect("main:show_experience")


@login_required(login_url="/login/")
def toggle_certification_star(request, id):
    certification = get_object_or_404(Certification, pk=id)
    if request.method == "POST":
        if request.user in certification.starred_by.all():
            certification.starred_by.remove(request.user)
        else:
            certification.starred_by.add(request.user)
    return redirect("main:show_certification")