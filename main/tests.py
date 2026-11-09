from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Certification


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, reverse("api:experience-list"))
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

        api_response = self.client.get(reverse("api:experience-list"))
        self.assertEqual(api_response.data[0]["title"], self.experience.title)
        self.assertEqual(api_response.data[0]["category_display"], "Part-Time")

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada experience yang ditambahkan atau ditemukan.")
        self.assertEqual(self.client.get(reverse("api:experience-list")).data, [])

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))
        self.assertFalse(self.experience.is_ongoing)
        self.assertNotContains(response, "Sedang berlangsung")
        

class CertificationTest(TestCase):
    def setUp(self):
        self.certification = Certification.objects.create(
            title="TOEFL ITP",
            issuer="ETS",
            issued_at="2025-02-22",
        )

    def test_certification_url_is_accessible(self):
        response = self.client.get(reverse("main:show_certification"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "certification.html")

    def test_certification_page_uses_api(self):
        response = self.client.get(reverse("main:show_certification"))
        self.assertContains(response, reverse("api:certification-list"))
        self.assertIn("csrftoken", response.cookies)

        api_response = self.client.get(reverse("api:certification-list"))
        self.assertEqual(api_response.data[0]["title"], self.certification.title)
        self.assertEqual(api_response.data[0]["issuer"], self.certification.issuer)

    def test_empty_certification_page(self):
        Certification.objects.all().delete()
        response = self.client.get(reverse("main:show_certification"))
        self.assertContains(response, "Belum ada certification yang ditambahkan atau ditemukan.")
        self.assertEqual(self.client.get(reverse("api:certification-list")).data, [])