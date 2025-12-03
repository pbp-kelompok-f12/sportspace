from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile


class AccountsViewsTests(TestCase):
    """Unit test untuk semua view di app accounts"""

    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('accounts:signup')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.profile_url = reverse('accounts:profile')
        self.profile_json_url = reverse('accounts:profile_json')

        # Buat user untuk login test
        self.user = User.objects.create_user(username='tester', password='Cukurukuk123!')

        # Data untuk signup baru
        self.new_user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'Cukurukuk123!',
            'password2': 'Cukurukuk123!',
            'role': 'customer'
        }

    # ----------------------------------------------------------------------
    # SIGNUP TESTS
    # ----------------------------------------------------------------------
    def test_signup_page_loads(self):
        """Halaman signup bisa diakses"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_user_can_signup_successfully(self):
        """User bisa signup dan diarahkan ke /home/"""
        response = self.client.post(self.signup_url, self.new_user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_invalid_password_mismatch(self):
        """Signup gagal jika password tidak sama"""
        data = self.new_user_data.copy()
        data['password2'] = 'TidakSama123!'
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn’t match.")

    # ----------------------------------------------------------------------
    # LOGIN TESTS
    # ----------------------------------------------------------------------
    def test_login_page_loads(self):
        """Halaman login bisa diakses"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_user_can_login(self):
        """User bisa login dengan kredensial valid"""
        login_success = self.client.login(username='tester', password='Cukurukuk123!')
        self.assertTrue(login_success)

    def test_login_invalid_credentials(self):
        """Login gagal dengan kredensial salah"""
        response = self.client.post(self.login_url, {'username': 'salah', 'password': 'tidakada'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct", status_code=200)

    # ----------------------------------------------------------------------
    # LOGOUT TESTS
    # ----------------------------------------------------------------------
    def test_logout_redirects_to_login(self):
        """Logout berhasil dan redirect ke halaman login"""
        self.client.login(username='tester', password='Cukurukuk123!')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    # ----------------------------------------------------------------------
    # PROFILE VIEW TESTS
    # ----------------------------------------------------------------------
    def test_profile_view_requires_login(self):
        """Profile view butuh login"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)  # redirect ke login

    def test_profile_view_loads_for_logged_user(self):
        """Profile view dapat diakses oleh user login"""
        self.client.login(username='tester', password='Cukurukuk123!')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_profile_view_post_updates_data(self):
        """POST ke profile view memperbarui profil"""
        self.client.login(username='tester', password='Cukurukuk123!')
        data = {'email': 'baru@example.com', 'phone': '081234', 'address': 'Jakarta', 'photo_url': ''}
        response = self.client.post(self.profile_url, data)
        self.assertEqual(response.status_code, 200)
        # photo_url dikembalikan sebagai None jika kosong
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'success': True,
                'message': 'Profil berhasil diperbarui!',
                'email': 'baru@example.com',
                'phone': '081234',
                'address': 'Jakarta',
                'photo_url': None,
                'bio': ''
            }
        )

    # ----------------------------------------------------------------------
    # PROFILE JSON TEST
    # ----------------------------------------------------------------------
    def test_profile_json_returns_data(self):
        """Profile JSON mengembalikan data user"""
        self.client.login(username='tester', password='Cukurukuk123!')
        response = self.client.get(self.profile_json_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['username'], 'tester')
        self.assertEqual(data['role'], 'customer')

# TEST ADMIN.py
from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from accounts.models import Profile
from accounts.admin import ProfileAdmin


class DummyRequest:
    """Request palsu untuk pengujian permission di admin."""
    pass


class ProfileAdminPermissionTests(TestCase):
    """Test untuk memastikan semua operasi CRUD di admin dinonaktifkan."""

    def setUp(self):
        # Inisialisasi AdminSite dan ProfileAdmin secara manual
        self.site = AdminSite()
        self.admin = ProfileAdmin(Profile, self.site)
        self.request = DummyRequest()

        # Buat user & profile agar bisa digunakan sebagai contoh objek
        self.user = User.objects.create_user(username='tester', password='Cukurukuk123!')
        self.profile = self.user.profile  # otomatis dibuat oleh sinyal

    def test_has_add_permission_returns_false(self):
        """Admin tidak boleh menambah data"""
        self.assertFalse(self.admin.has_add_permission(self.request))

    def test_has_change_permission_returns_false(self):
        """Admin tidak boleh mengubah data"""
        self.assertFalse(self.admin.has_change_permission(self.request, self.profile))

    def test_has_delete_permission_returns_false(self):
        """Admin tidak boleh menghapus data"""
        self.assertFalse(self.admin.has_delete_permission(self.request, self.profile))

class ProfileModelTests(TestCase):
    """Test untuk model Profile."""

    def test_str_method_returns_username_and_role(self):
        """__str__ harus mengembalikan 'username (role)'"""
        user = User.objects.create_user(username='taka', password='Cukurukuk123!')
        profile = user.profile  # otomatis dibuat (OneToOne)
        profile.role = 'venue_owner'
        profile.save()

        expected_str = "taka (venue_owner)"
        self.assertEqual(str(profile), expected_str)

class ProfileViewTests(TestCase):
    """Test untuk memastikan profile_view berfungsi saat GET."""

    def setUp(self):
        self.user = User.objects.create_user(username='taka', password='Cukurukuk123!')
        self.user.profile.role = 'customer'
        self.user.profile.save()
        self.url = reverse('accounts:profile')

    def test_profile_view_get_returns_html(self):
        """Jika method bukan POST, harus render profile.html dengan form dan profile di context"""
        self.client.login(username='taka', password='Cukurukuk123!')

        response = self.client.get(self.url)

        # Pastikan status code OK
        self.assertEqual(response.status_code, 200)

        # Pastikan menggunakan template yang benar
        self.assertTemplateUsed(response, 'profile.html')

        # Pastikan context mengandung objek profile dan form
        self.assertIn('profile', response.context)
        self.assertIn('form', response.context)

        # Pastikan response bukan JSON (artinya bukan JsonResponse)
        self.assertFalse(isinstance(response, dict), "Response tidak boleh berupa JsonResponse untuk GET request")

class LoginViewRoleTests(TestCase):
    """Test untuk memastikan redirect login berdasarkan role user."""

    def setUp(self):
        # Buat dua user dengan role berbeda
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpass123')
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

        self.customer_user = User.objects.create_user(username='customeruser', password='custpass123')
        self.customer_user.profile.role = 'customer'
        self.customer_user.profile.save()

        self.url = reverse('accounts:login')

    def test_login_redirects_admin_to_adminpanel(self):
        """Jika role = admin, redirect ke dashboard admin"""
        response = self.client.post(self.url, {
            'username': 'adminuser',
            'password': 'adminpass123'
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard-admin/', response.url)

    def test_login_redirects_non_admin_to_home(self):
        """Jika role ≠ admin, redirect ke /home/"""
        response = self.client.post(self.url, {
            'username': 'customeruser',
            'password': 'custpass123'
        })

        self.assertRedirects(response, '/home/')


from django.http import JsonResponse


class ProfileViewInvalidFormTests(TestCase):
    """Test cabang 'else' dalam POST jika form tidak valid."""

    def setUp(self):
        self.user = User.objects.create_user(username='taka', password='Cukurukuk123!')
        self.user.profile.role = 'customer'
        self.user.profile.save()
        self.client.login(username='taka', password='Cukurukuk123!')
        self.url = reverse('accounts:profile')

    def test_profile_view_post_invalid_form_returns_json_error(self):
        """Jika form tidak valid, harus return JsonResponse dengan success=False dan status 400"""
        invalid_data = {
            'email': '',          # valid karena optional
            'phone': '1234',
            'address': 'Jakarta',
            'photo_url': 'not-a-valid-url'  # invalid URL
        }

        response = self.client.post(self.url, invalid_data)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('errors', data)
        self.assertIn('photo_url', data['errors'])

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile, FriendRequest
from django.http import JsonResponse


class FriendSystemTests(TestCase):
    """Test untuk semua view friend system (send, handle, list, unfriend, count, suggestions)."""

    def setUp(self):
        self.client = Client()

        # Buat dua user
        self.user1 = User.objects.create_user(username="alice", password="12345")
        self.user2 = User.objects.create_user(username="bob", password="12345")

        # Login sebagai user1 (yang akan melakukan aksi)
        self.client.login(username="alice", password="12345")

        # URL view yang digunakan
        self.send_url = reverse("accounts:send_friend_request")
        self.handle_url = reverse("accounts:handle_friend_request")
        self.friends_json_url = reverse("accounts:friends_json")
        self.unfriend_url = reverse("accounts:unfriend")
        self.request_count_url = reverse("accounts:get_request_count")
        self.friend_count_url = reverse("accounts:get_friend_count")
        self.suggestions_url = reverse("accounts:get_friend_suggestions")

    # ------------------------------------------------------------------
    # SEND FRIEND REQUEST
    # ------------------------------------------------------------------
    def test_send_friend_request_success(self):
        """User dapat mengirim permintaan pertemanan."""
        response = self.client.post(self.send_url, {"username": "bob"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "pending")
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).exists())

    def test_send_friend_request_self_not_allowed(self):
        """Tidak bisa menambahkan diri sendiri."""
        response = self.client.post(self.send_url, {"username": "alice"})
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("Tidak bisa menambahkan diri sendiri", data["message"])

    def test_send_friend_request_user_not_found(self):
        """Gagal jika user target tidak ada."""
        response = self.client.post(self.send_url, {"username": "unknown_user"})
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("User tidak ditemukan", data["message"])

    # ------------------------------------------------------------------
    # HANDLE FRIEND REQUEST
    # ------------------------------------------------------------------
    def test_handle_friend_request_accept(self):
        """Menerima permintaan pertemanan berhasil."""
        FriendRequest.objects.create(from_user=self.user2, to_user=self.user1)
        friend_request = FriendRequest.objects.get(from_user=self.user2, to_user=self.user1)

        response = self.client.post(self.handle_url, {
            "action": "accept",
            "from_user_id": self.user2.id
        })

        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("berteman dengan", data["message"])
        self.assertIn(self.user2.profile, self.user1.profile.friends.all())

    def test_handle_friend_request_reject(self):
        """Menolak permintaan pertemanan berhasil."""
        FriendRequest.objects.create(from_user=self.user2, to_user=self.user1)

        response = self.client.post(self.handle_url, {
            "action": "reject",
            "from_user_id": self.user2.id
        })
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["new_friend"], None)
        self.assertFalse(FriendRequest.objects.filter(from_user=self.user2, to_user=self.user1).exists())

    def test_handle_friend_request_not_found(self):
        """Menangani kasus permintaan tidak ditemukan."""
        response = self.client.post(self.handle_url, {
            "action": "accept",
            "from_user_id": 9999
        })
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data["success"])

    # ------------------------------------------------------------------
    # FRIEND LIST JSON
    # ------------------------------------------------------------------
    def test_friends_json_returns_friend_list(self):
        """friends_json mengembalikan daftar teman."""
        # Jadikan berteman langsung
        self.user1.profile.friends.add(self.user2.profile)
        self.user2.profile.friends.add(self.user1.profile)

        response = self.client.get(self.friends_json_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("friends", data)
        self.assertEqual(data["friends"][0]["username"], "bob")

    # ------------------------------------------------------------------
    # UNFRIEND
    # ------------------------------------------------------------------
    def test_unfriend_removes_friend(self):
        """unfriend menghapus hubungan pertemanan dua arah."""
        self.user1.profile.friends.add(self.user2.profile)
        self.user2.profile.friends.add(self.user1.profile)

        response = self.client.post(self.unfriend_url, {"username": "bob"})
        data = response.json()
        self.assertTrue(data["success"])
        self.assertNotIn(self.user2.profile, self.user1.profile.friends.all())

    def test_unfriend_user_not_found(self):
        """Jika user target tidak ada, kembalikan 404."""
        response = self.client.post(self.unfriend_url, {"username": "ghost"})
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # COUNT TESTS
    # ------------------------------------------------------------------
    def test_get_request_count_returns_correct_number(self):
        """get_request_count mengembalikan jumlah pending request."""
        FriendRequest.objects.create(from_user=self.user2, to_user=self.user1)
        response = self.client.get(self.request_count_url)
        data = response.json()
        self.assertEqual(data["count"], 1)

    def test_get_friend_count_returns_correct_number(self):
        """get_friend_count mengembalikan jumlah teman."""
        self.user1.profile.friends.add(self.user2.profile)
        self.user2.profile.friends.add(self.user1.profile)

        response = self.client.get(self.friend_count_url)
        data = response.json()
        self.assertEqual(data["count"], 1)

    # ------------------------------------------------------------------
    # SUGGESTIONS TESTS
    # ------------------------------------------------------------------
    def test_get_friend_suggestions_excludes_self_and_friends(self):
        """Saran teman tidak boleh memunculkan diri sendiri atau teman yang sudah ada."""
        self.user1.profile.friends.add(self.user2.profile)
        self.user2.profile.friends.add(self.user1.profile)

        response = self.client.get(self.suggestions_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for s in data["suggestions"]:
            self.assertNotEqual(s["username"], "alice")
            self.assertNotEqual(s["username"], "bob")
