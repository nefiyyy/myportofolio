from django.urls import path
from main.views import (
    show_main,
    show_experience,
    show_certification,
    show_certification_detail,
    create_experience,
    get_experience_json,
    delete_experience,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("certification/", show_certification, name="show_certification"),
    path("certification/<uuid:id>/", show_certification_detail, name="show_certification_detail"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
]