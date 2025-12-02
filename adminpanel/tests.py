from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile
from home.models import LapanganPadel
from booking.models import Booking, Venue
from django.utils import timezone
import uuid
import json


class AdminPanelTests(TestCase):
    def setUp(self):
        # Buat user admin dan login
        self.admin_user = User.objects.create_user(username='adminuser', password='testpass')
        self.admin_profile = self.admin_user.profile
        self.admin_profile.role = 'admin'
        self.admin_profile.save()
        self.client = Client()
        self.client.login(username='adminuser', password='testpass')

        # Buat user non-admin
        self.normal_user = User.objects.create_user(username='normaluser', password='testpass')
        self.normal_profile = self.normal_user.profile
        self.normal_profile.role = 'customer'
        self.normal_profile.save()

        # Buat venue dan booking contoh
        self.venue = Venue.objects.create(
            name="Padel Court",
            location="Jakarta Selatan",
            address="Jl. Kemang Raya No. 12"
        )
        self.booking = Booking.objects.create(
            user=self.normal_user,
            venue=self.venue,
            booking_date=timezone.now().date(),
            start_time=timezone.now().time(),
            end_time=(timezone.now() + timezone.timedelta(hours=1)).time(),
            customer_name="John Doe",
            customer_email="john@example.com",
            customer_phone="08123456789",
        )

        # Buat lapangan contoh
        self.lapangan = LapanganPadel.objects.create(
            place_id="test_place_id",
            nama="Lapangan 1",
            alamat="Jl. Contoh",
            rating=4.5,
            total_review=10
        )

    # ============================================================
    #                     ADMIN PAGE TESTS
    # ============================================================
    def test_dashboard_admin_page_loads(self):
        response = self.client.get(reverse('adminpanel:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_admin.html')

    def test_dashboard_redirect_for_non_admin(self):
        self.client.logout()
        self.client.login(username='normaluser', password='testpass')
        response = self.client.get(reverse('adminpanel:dashboard'))
        self.assertEqual(response.status_code, 302)  # redirect ke /home/

    # ============================================================
    #                     LAPANGAN TESTS
    # ============================================================
    def test_get_lapangan_json_returns_data(self):
        response = self.client.get(reverse('adminpanel:get_lapangan_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('lapangan', data)
        self.assertEqual(len(data['lapangan']), 1)

    def test_create_lapangan_ajax_success(self):
        payload = {
            "place_id": "id_baru",
            "nama": "Lapangan Baru",
            "alamat": "Jl. Baru",
            "rating": 4.0,
            "total_review": 20
        }
        response = self.client.post(
            reverse('adminpanel:create_lapangan_ajax'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_update_lapangan_ajax_success(self):
        payload = {
            "nama": "Lapangan Updated",
            "alamat": "Jl. Update",
            "place_id": "test_place_id",
            "rating": 5.0,
            "total_review": 30
        }
        response = self.client.post(
            reverse('adminpanel:update_lapangan_ajax', args=[self.lapangan.id]),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_delete_lapangan_ajax_success(self):
        response = self.client.delete(
            reverse('adminpanel:delete_lapangan_ajax', args=[self.lapangan.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    # ============================================================
    #                     USER MANAGEMENT TESTS
    # ============================================================
    def test_get_users_json_returns_users(self):
        response = self.client.get(reverse('adminpanel:get_users_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('users', data)
        self.assertGreaterEqual(len(data['users']), 2)

    def test_add_user_ajax_success(self):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "role": "customer"
        }
        response = self.client.post(
            reverse('adminpanel:add_user_ajax'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_update_user_ajax_success(self):
        payload = {
            "username": "updated_user",
            "email": "updated@example.com",
            "role": "customer"
        }
        response = self.client.post(
            reverse('adminpanel:update_user_ajax', args=[self.normal_user.id]),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_delete_user_ajax_success(self):
        response = self.client.delete(
            reverse('adminpanel:delete_user_ajax', args=[self.normal_user.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    # ============================================================
    #                     BOOKING TESTS
    # ============================================================
    def test_get_booking_json_returns_data(self):
        response = self.client.get(reverse('adminpanel:get_booking_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('bookings', data)
        self.assertGreaterEqual(len(data['bookings']), 1)

    def test_delete_booking_ajax_success(self):
        response = self.client.delete(
            reverse('adminpanel:delete_booking_ajax', args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

class AdminViewTests(TestCase):
    def setUp(self):
        # Buat admin user dan login
        self.admin_user = User.objects.create_user(username="adminuser", password="testpass")
        self.admin_user.profile.role = "admin"
        self.admin_user.profile.save()

        self.client = Client()
        self.client.login(username="adminuser", password="testpass")

        # Buat user biasa
        self.normal_user = User.objects.create_user(username="normaluser", password="testpass")
        self.normal_user.profile.role = "customer"
        self.normal_user.profile.save()

        # Buat data lapangan
        self.lapangan = LapanganPadel.objects.create(
            place_id="test123",
            nama="Lapangan Lama",
            alamat="Jl. Lama",
            rating=4.0,
            total_review=10
        )

    # ===============================================================
    # TEST: create_admin_user
    # ===============================================================
    def test_create_admin_user_get(self):
        """GET harus tampilkan halaman konfirmasi"""
        response = self.client.get(reverse("adminpanel:create_admin_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_admin.html")

    def test_create_admin_user_post_success(self):
        """POST tanpa admin existing akan berhasil membuat superuser"""
        response = self.client.post(reverse("adminpanel:create_admin_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_created_success.html")
        self.assertTrue(User.objects.filter(username="admin").exists())
        data = response.context
        self.assertTrue(data["success"])
        self.assertIn("berhasil", data["message"].lower())

    def test_create_admin_user_post_fail_if_exists(self):
        """Jika user admin sudah ada, maka pesan gagal"""
        User.objects.create_superuser(username="admin", password="cukurukuk", email="a@b.com")
        response = self.client.post(reverse("adminpanel:create_admin_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_created_success.html")
        data = response.context
        self.assertFalse(data["success"])
        self.assertIn("sudah ada", data["message"].lower())

    # ===============================================================
    # TEST: dashboard_lapangan_ajax
    # ===============================================================
    def test_dashboard_lapangan_ajax_admin(self):
        """Admin bisa akses dashboard lapangan"""
        response = self.client.get(reverse("adminpanel:dashboard_lapangan"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard_admin_lapangan.html")

    def test_dashboard_lapangan_ajax_non_admin_redirect(self):
        """Non-admin akan diarahkan ke /home/"""
        self.client.logout()
        self.client.login(username="normaluser", password="testpass")
        response = self.client.get(reverse("adminpanel:dashboard_lapangan"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/home/", response.url)

    # ===============================================================
    # TEST: create_lapangan_ajax
    # ===============================================================
    def test_create_lapangan_ajax_success(self):
        payload = {
            "place_id": "abc123",
            "nama": "Lapangan Baru",
            "alamat": "Jl. Baru",
            "rating": 4.5,
            "total_review": 15
        }
        response = self.client.post(
            reverse("adminpanel:create_lapangan_ajax"),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(LapanganPadel.objects.filter(nama="Lapangan Baru").exists())

    def test_create_lapangan_ajax_invalid_form(self):
        """Jika form tidak valid (missing field wajib)"""
        payload = {"nama": ""}  # invalid
        response = self.client.post(
            reverse("adminpanel:create_lapangan_ajax"),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("errors", data)

    def test_create_lapangan_ajax_invalid_json(self):
        """Jika body bukan JSON valid"""
        response = self.client.post(
            reverse("adminpanel:create_lapangan_ajax"),
            data="{invalid json",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    # ===============================================================
    # TEST: update_lapangan_ajax
    # ===============================================================
    def test_update_lapangan_ajax_success(self):
        payload = {
            "place_id": "test123",
            "nama": "Lapangan Update",
            "alamat": "Jl. Baru",
            "rating": 5.0,
            "total_review": 30
        }
        response = self.client.post(
            reverse("adminpanel:update_lapangan_ajax", args=[self.lapangan.id]),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.lapangan.refresh_from_db()
        self.assertEqual(self.lapangan.nama, "Lapangan Update")

    def test_update_lapangan_ajax_not_found(self):
        response = self.client.post(
            reverse("adminpanel:update_lapangan_ajax", args=[999]),
            data=json.dumps({"nama": "ABC"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    # ===============================================================
    # TEST: delete_lapangan_ajax
    # ===============================================================
    def test_delete_lapangan_ajax_success(self):
        response = self.client.delete(
            reverse("adminpanel:delete_lapangan_ajax", args=[self.lapangan.id])
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertFalse(LapanganPadel.objects.filter(id=self.lapangan.id).exists())

    def test_delete_lapangan_ajax_not_found(self):
        response = self.client.delete(
            reverse("adminpanel:delete_lapangan_ajax", args=[999])
        )
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    # ===============================================================
    # TEST: dashboard_user_admin
    # ===============================================================
    def test_dashboard_user_admin_accessible(self):
        response = self.client.get(reverse("adminpanel:dashboard_user_admin"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard_admin_users.html")

    def test_dashboard_user_admin_non_admin_redirect(self):
        self.client.logout()
        self.client.login(username="normaluser", password="testpass")
        response = self.client.get(reverse("adminpanel:dashboard_user_admin"))
        self.assertEqual(response.status_code, 302)

    # ===============================================================
    # TEST: get_users_json
    # ===============================================================
    def test_get_users_json_all(self):
        response = self.client.get(reverse("adminpanel:get_users_json"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("users", data)
        self.assertGreaterEqual(len(data["users"]), 2)

    def test_get_users_json_filtered(self):
        response = self.client.get(reverse("adminpanel:get_users_json") + "?role=customer")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("users", data)
        # Semua hasil harus punya role customer
        for u in data["users"]:
            self.assertEqual(u["role"], "customer")

