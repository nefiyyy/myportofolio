import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Certification


class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.experience = Experience.objects.create(
            title="Portfolio", description="My website", category="internship",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "New experience", "description": "A useful role", "category": "research",
            "thumbnail": "https://example.com/image.png",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.experience.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_experience(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Experience.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
            ({"category": "not-a-category"}, "category"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Experience.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.description, "My website")
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_experiences(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CertificationAPITest(APITestCase):
    """Test API Certification untuk keempat peran: pengunjung, pengguna biasa, Editor, pemilik."""

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.user = User.objects.create_user(
            username="user", password="test-password", email="user@example.com",
        )
        self.editor = User.objects.create_user(username="editor", password="test-password")
        self.editor.groups.add(Group.objects.create(name="Editor"))

        self.certification = Certification.objects.create(
            title="TOEFL ITP", issuer="ETS", issued_at="2025-02-22",
            credential_url="https://example.com/toefl",
        )
        self.list_url = reverse("api:certification-list")
        self.detail_url = reverse("api:certification-detail", args=[self.certification.id])
        self.star_url = reverse("api:certification-star", args=[self.certification.id])
        self.payload = {
            "title": "OSA Certificate", "issuer": "Universitas Indonesia",
            "issued_at": "2025-08-01", "credential_url": "https://example.com/osa",
            "thumbnail": "https://example.com/osa.jpg",
        }

    def assert_certification_unchanged(self):
        """Isi database harus tetap sama setelah permintaan yang ditolak."""
        self.assertEqual(Certification.objects.count(), 1)
        self.certification.refresh_from_db()
        self.assertEqual(self.certification.title, "TOEFL ITP")
        self.assertEqual(self.certification.issuer, "ETS")

    # ----- Membaca data (semua peran) -----

    def test_guest_can_read_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.certification.id))
        self.assertEqual(response.data[0]["star_count"], 0)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_response_has_no_sensitive_account_data(self):
        self.certification.starred_by.add(self.user)
        response = self.client.get(self.detail_url)
        body = response.content.decode()
        self.assertEqual(response.data["starred_by_names"], "user")
        self.assertNotIn("user@example.com", body)
        self.assertNotIn("password", body)

    def test_search_with_query_parameter(self):
        Certification.objects.create(title="Google Data Analytics", issuer="Google", issued_at="2024-01-01")
        response = self.client.get(self.list_url, {"title": "toefl"})
        self.assertEqual([c["title"] for c in response.data], ["TOEFL ITP"])
        response = self.client.get(self.list_url, {"title": "tidak-ada"})
        self.assertEqual(response.data, [])

    def test_missing_certification_returns_404(self):
        url = reverse("api:certification-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_404_NOT_FOUND)

    # ----- Pengunjung & pengguna biasa: semua penulisan ditolak -----

    def test_guest_and_regular_user_cannot_write(self):
        for account in (None, self.user):
            self.client.force_authenticate(user=account)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Diubah"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assert_certification_unchanged()

    # ----- Editor: boleh PUT/PATCH, tidak boleh POST/DELETE -----

    def test_editor_can_patch_and_put(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"title": "TOEFL ITP 2025"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.certification.refresh_from_db()
        self.assertEqual(self.certification.title, "TOEFL ITP 2025")
        self.assertEqual(self.certification.issuer, "ETS")  # PATCH tidak menyentuh field lain

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.certification.refresh_from_db()
        self.assertEqual(self.certification.issuer, "Universitas Indonesia")

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assert_certification_unchanged()

    # ----- Pemilik: boleh membuat, mengubah, menghapus -----

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Certification.objects.filter(pk=response.data["id"], title="OSA Certificate").exists())

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Certification.objects.filter(pk=self.certification.id).exists())

    def test_put_requires_all_fields(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.detail_url, {"title": "Hanya judul"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_certification_unchanged()

    # ----- Validasi input -----

    def test_invalid_input_returns_400_and_saves_nothing(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"issuer": "<b></b>"}, "issuer"),
            ({"issued_at": "bukan-tanggal"}, "issued_at"),
            ({"credential_url": "javascript:alert(1)"}, "credential_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Certification.objects.count(), 1)

    def test_html_tags_are_stripped(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "title": "<b>OSA</b> Certificate", "issuer": "<i>UI</i>",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        saved = Certification.objects.get(pk=response.data["id"])
        self.assertEqual(saved.title, "OSA Certificate")
        self.assertEqual(saved.issuer, "UI")

    def test_computed_star_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "palsu", "starred_by": [self.user.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(Certification.objects.get(pk=response.data["id"]).starred_by.exists())

    # ----- Star -----

    def test_guest_cannot_star(self):
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.certification.starred_by.count(), 0)

    def test_logged_in_user_can_toggle_star_for_themselves_only(self):
        self.client.force_authenticate(user=self.user)
        # Mencoba memberi star atas nama owner diabaikan: akun selalu dari request.user
        response = self.client.post(self.star_url, {"user": self.owner.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(list(self.certification.starred_by.all()), [self.user])

        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(self.certification.starred_by.count(), 0)

    def test_missing_certification_star_returns_404(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("api:certification-star", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(url).status_code, status.HTTP_404_NOT_FOUND)

    # ----- CSRF dengan login sungguhan (bukan force_authenticate) -----

    def test_session_write_without_csrf_token_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Certification.objects.count(), 1)

        response = client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Certification.objects.filter(pk=self.certification.id).exists())

    def test_session_write_with_csrf_token_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        client.get(reverse("main:show_certification"))  # halaman menyetel cookie csrftoken
        token = client.cookies["csrftoken"].value
        response = client.post(self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)