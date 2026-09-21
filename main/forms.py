from django.forms import ModelForm, TextInput, Textarea, URLInput, Select, DateTimeInput, DateInput
from main.models import Experience, Certification


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "ended_at",
        ]
        labels = {
            "title": "Judul Pengalaman",
            "description": "Deskripsi",
            "category": "Kategori",
            "thumbnail": "URL Gambar",
            "ended_at": "Tanggal Selesai",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Wedding Coordination",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan pengalamanmu",
                    "rows": 3,
                }
            ),
            "category": Select(),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
             "ended_at": DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",

             ),
        }


class CertificationForm(ModelForm):
    class Meta:
        model = Certification
        fields = ["title", "issuer", "issued_at", "credential_url", "thumbnail"]
        labels = {
            "title": "Nama Sertifikasi",
            "issuer": "Penerbit",
            "issued_at": "Tanggal Terbit",
            "credential_url": "URL Sertifikat",
            "thumbnail": "URL Gambar",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "TOEFL ITP", "maxlength": 255}),
            "issuer": TextInput(attrs={"placeholder": "ETS", "maxlength": 255}),
            "issued_at": DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "credential_url": URLInput(attrs={"placeholder": "https://..."}),
            "thumbnail": URLInput(attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000"}),
        }