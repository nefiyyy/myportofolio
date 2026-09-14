from django.urls import path
from main.views import show_main, show_experience, show_certification

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("certification/", show_certification, name="show_certification")
]

from django.urls import path
from main.views import show_main, show_experience, show_certification, show_certification_detail

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("certification/", show_certification, name="show_certification"),
    path("certification/<uuid:id>/", show_certification_detail, name="show_certification_detail"),
]