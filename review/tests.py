from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from home.models import LapanganPadel
from .models import Review


class ReviewViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tasya", password="12345")
        self.lapangan = LapanganPadel.objects.create(
            place_id="test123",
            nama="Padel Test Court",
            alamat="Jl. Test No.1",
            rating=4.0,
            total_review=10,
        )

    def login(self):
        self.client.login(username="tasya", password="12345")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("review:my_reviews"))
        self.assertEqual(response.status_code, 302)
        # Sesuaikan ke LOGIN_URL di project ini
        self.assertIn("/login/", response.url)

    def test_my_reviews_page_loads(self):
        self.login()
        response = self.client.get(reverse("review:my_reviews"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "my_reviews.html")

    def test_all_reviews_page(self):
        self.login()
        Review.objects.create(user=self.user, lapangan=self.lapangan, comment="Nice")
        response = self.client.get(reverse("review:all_reviews", args=[self.lapangan.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "all_reviews.html")

    def test_add_review(self):
        self.login()
        response = self.client.post(
            reverse("review:my_reviews"),
            {"lapangan": self.lapangan.id, "comment": "Tempat bagus"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 1)

    def test_add_duplicate_review_fails(self):
        self.login()
        # bikin review pertama
        Review.objects.create(user=self.user, lapangan=self.lapangan, comment="ok")
        
        # coba bikin review duplikat
        response = self.client.post(
            reverse("review:my_reviews"),
            {"lapangan": self.lapangan.id, "comment": "duplikat"},
            follow=True,
        )
        self.assertEqual(Review.objects.count(), 1)
        # pastikan halaman my_reviews tetap kebuka
        self.assertEqual(response.status_code, 200)


    def test_edit_review_ajax(self):
        self.login()
        review = Review.objects.create(user=self.user, lapangan=self.lapangan, comment="awal")
        response = self.client.post(
            reverse("review:edit_review", args=[review.id]),
            data={"comment": "edit", "anonymous": False},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        review.refresh_from_db()
        self.assertEqual(review.comment, "edit")

    def test_delete_review_ajax(self):
        self.login()
        review = Review.objects.create(user=self.user, lapangan=self.lapangan, comment="hapus")
        response = self.client.post(reverse("review:delete_review", args=[review.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 0)

    def test_add_new_review_success(self):
        self.login()
        lapangan2 = LapanganPadel.objects.create(
            place_id="test456",
            nama="Lapangan Baru",
            alamat="Jl. Baru No.2",
            rating=5.0,
            total_review=0,
        )
        response = self.client.post(
            reverse("review:my_reviews"),
            {"lapangan": lapangan2.id, "comment": "Review baru"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 1)
