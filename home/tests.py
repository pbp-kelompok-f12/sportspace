from django.test import TestCase

# Create your tests here.
import json
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch # Penting untuk mem-mock API
from .models import LapanganPadel

class ViewTests(TestCase):
    
    def setUp(self):
        """
        Setup data yang akan digunakan berulang kali di semua tes.
        Berjalan sebelum SETIAP method tes.
        """
        # Buat beberapa user untuk tes permissions
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.admin_user = User.objects.create_superuser(username='admin', password='password123', email='admin@test.com')
        
        # Buat objek LapanganPadel yang dimiliki oleh user1
        self.lapangan1 = LapanganPadel.objects.create(
            place_id="place_abc_123",
            nama="Lapangan Milik User 1",
            alamat="Jl. Tes No. 1",
            rating=4.5,
            total_review=10,
            added_by=self.user1 
        )
        
        # Inisialisasi client
        self.client = Client()

        # URL yang sering digunakan
        self.home_url = reverse('home:home')
        self.landing_url = reverse('home:landing')
        self.get_json_url = reverse('home:get_lapangan_json')
        self.create_ajax_url = reverse('home:create_lapangan_ajax')
        self.refresh_api_url = reverse('home:refresh_from_api')
        self.get_by_id_url = reverse('home:get_lapangan_by_id', args=[self.lapangan1.id])
        self.update_ajax_url = reverse('home:update_lapangan_ajax', args=[self.lapangan1.id])
        self.delete_ajax_url = reverse('home:delete_lapangan_ajax', args=[self.lapangan1.id])
        self.modal_edit_url = reverse('home:get_lapangan_modal', args=[self.lapangan1.id])
        self.modal_add_url = reverse('home:get_lapangan_modal_add') # Asumsi Anda punya URL terpisah untuk add
        
        # Jika URL modal add tidak terpisah (menggunakan 'id=None'):
        # Kita akan panggil 'get_lapangan_modal' tanpa argumen
        self.modal_add_url_fallback = reverse('home:get_lapangan_modal')


    # --- Tes View Sederhana (Landing & Home) ---

    def test_landing_view_anonymous_user(self):
        """Tes pengguna anonim bisa mengakses landing page."""
        response = self.client.get(self.landing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_landing_view_authenticated_user_redirects(self):
        """Tes pengguna yang login di-redirect dari landing ke home."""
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.landing_url)
        # Harusnya redirect (302) ke halaman 'home'
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url)

    def test_home_view_authenticated(self):
        """Tes pengguna yang login bisa mengakses home."""
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')

    def test_home_view_unauthenticated_redirects(self):
        """Tes pengguna anonim di-redirect dari home ke login."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)
        # Cek apakah redirect ke URL login
        self.assertTrue(response.url.startswith('/accounts/login/'))


    # --- Tes View GET (Modal & JSON) ---

    def test_get_lapangan_modal_add(self):
        """Tes mendapatkan modal untuk 'Add'."""
        self.client.login(username='user1', password='password123')
        # Menggunakan URL tanpa ID
        response = self.client.get(self.modal_add_url_fallback) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/modal.html')
        self.assertContains(response, 'Add New Lapangan') # Cek title
        self.assertContains(response, 'Add Lapangan') # Cek submit text

    def test_get_lapangan_modal_edit(self):
        """Tes mendapatkan modal untuk 'Edit'."""
        self.client.login(username='user1', password='password123')
        # Menggunakan URL dengan ID lapangan1
        response = self.client.get(self.modal_edit_url) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/modal.html')
        self.assertContains(response, 'Edit Lapangan') # Cek title
        self.assertContains(response, 'Update') # Cek submit text
        self.assertContains(response, self.lapangan1.nama) # Cek form terisi

    def test_get_lapangan_json_authenticated(self):
        """Tes mendapatkan semua data lapangan via JSON."""
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.get_json_url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['fields']['nama'], self.lapangan1.nama)
        self.assertEqual(data[0]['fields']['added_by'], self.user1.id)

    def test_get_lapangan_by_id_success(self):
        """Tes mendapatkan satu lapangan via JSON by ID."""
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.get_by_id_url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['nama'], self.lapangan1.nama)
        self.assertEqual(data['id'], self.lapangan1.id)

    def test_get_lapangan_by_id_not_found(self):
        """Tes mendapatkan JSON untuk ID yang tidak ada (404)."""
        self.client.login(username='user1', password='password123')
        # Buat URL untuk ID yang tidak ada
        bad_url = reverse('home:get_lapangan_by_id', args=[9999])
        response = self.client.get(bad_url)
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Lapangan not found')


    # --- Tes View AJAX (Create, Update, Delete) ---

    def test_create_lapangan_ajax_success(self):
        """Tes berhasil membuat lapangan baru via AJAX POST."""
        self.client.login(username='user1', password='password123')
        payload = {
            'nama': 'Lapangan Baru Tes',
            'alamat': 'Jl. Baru No. 123',
            'rating': 5.0,
            'notes': 'Catatan tes'
        }
        
        # Kirim sebagai JSON
        response = self.client.post(
            self.create_ajax_url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201) # 201 Created
        self.assertEqual(LapanganPadel.objects.count(), 2) # Sekarang ada 2 lapangan
        
        # Cek data baru di database
        new_lapangan = LapanganPadel.objects.get(nama='Lapangan Baru Tes')
        self.assertEqual(new_lapangan.alamat, 'Jl. Baru No. 123')
        self.assertEqual(new_lapangan.added_by, self.user1) # Cek pemilik
        self.assertTrue(new_lapangan.place_id.startswith('internal_')) # Cek place_id
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Lapangan berhasil ditambahkan!')

    def test_create_lapangan_ajax_invalid_data(self):
        """Tes gagal membuat lapangan karena data tidak valid (nama kosong)."""
        self.client.login(username='user1', password='password123')
        payload = {'nama': '', 'alamat': 'Alamat ada'} # Nama wajib diisi
        
        response = self.client.post(
            self.create_ajax_url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400) # Bad Request
        self.assertEqual(LapanganPadel.objects.count(), 1) # Data tidak bertambah
        
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Nama dan Alamat wajib diisi.')

    def test_create_lapangan_wrong_method(self):
        """Tes view create_lapangan menolak method GET."""
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.create_ajax_url)
        self.assertEqual(response.status_code, 405) # Method Not Allowed

    def test_update_lapangan_ajax_success_owner(self):
        """Tes pemilik (user1) berhasil mengupdate lapangannya."""
        self.client.login(username='user1', password='password123')
        payload = {'nama': 'Nama Sudah Diupdate', 'notes': 'Catatan baru'}
        
        response = self.client.post(
            self.update_ajax_url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Refresh data dari DB untuk cek
        self.lapangan1.refresh_from_db()
        self.assertEqual(self.lapangan1.nama, 'Nama Sudah Diupdate')
        self.assertEqual(self.lapangan1.notes, 'Catatan baru')
        
        data = response.json()
        self.assertEqual(data['status'], 'success')

    def test_update_lapangan_ajax_permission_denied(self):
        """Tes user2 GAGAL mengupdate lapangan milik user1."""
        self.client.login(username='user2', password='password123') # Login sebagai user2
        payload = {'nama': 'Coba Diretas'}
        
        response = self.client.post(
            self.update_ajax_url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403) # Forbidden
        
        # Cek nama di DB tidak berubah
        self.lapangan1.refresh_from_db()
        self.assertEqual(self.lapangan1.nama, 'Lapangan Milik User 1') 
        
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'You do not have permission to edit this.')

    def test_update_lapangan_ajax_success_admin(self):
        """Tes admin BERHASIL mengupdate lapangan milik user1."""
        self.client.login(username='admin', password='password123') # Login sebagai admin
        payload = {'nama': 'Diupdate oleh Admin'}
        
        response = self.client.post(
            self.update_ajax_url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.lapangan1.refresh_from_db()
        self.assertEqual(self.lapangan1.nama, 'Diupdate oleh Admin')

    def test_delete_lapangan_ajax_success_owner(self):
        """Tes pemilik (user1) berhasil menghapus lapangannya."""
        self.client.login(username='user1', password='password123')
        response = self.client.delete(self.delete_ajax_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LapanganPadel.objects.count(), 0) # Data terhapus
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        # Cek apakah objek benar-benar tidak ada
        with self.assertRaises(LapanganPadel.DoesNotExist):
            LapanganPadel.objects.get(id=self.lapangan1.id)

    def test_delete_lapangan_ajax_permission_denied(self):
        """Tes user2 GAGAL menghapus lapangan milik user1."""
        self.client.login(username='user2', password='password123') # Login sebagai user2
        response = self.client.delete(self.delete_ajax_url)
        
        self.assertEqual(response.status_code, 403) # Forbidden
        self.assertEqual(LapanganPadel.objects.count(), 1) # Data masih ada
        
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'You do not have permission to delete this.')

    def test_delete_lapangan_ajax_success_admin(self):
        """Tes admin BERHASIL menghapus lapangan milik user1."""
        self.client.login(username='admin', password='password123')
        response = self.client.delete(self.delete_ajax_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LapanganPadel.objects.count(), 0)


    # --- Tes View dengan External API (Mocking) ---

    # @patch menimpa fungsi 'get_google_maps_data' di dalam file 'home.views'
    @patch('home.views.get_google_maps_data') 
    @override_settings(GOOGLE_MAPS_API_KEY='dummy_key') # Pastikan setting API key ada
    def test_refresh_from_api_success(self, mock_get_data):
        """Tes refresh API berhasil (membuat data baru & update data lama)."""
        self.client.login(username='user1', password='password123')
        
        # 1. Definisikan data palsu yang akan dikembalikan oleh mock
        mock_api_results = [
            {
                'place_id': 'place_abc_123', # ID ini sama dengan self.lapangan1
                'nama': 'Nama Lapangan Diupdate', # Nama baru
                'alamat': 'Alamat Baru',
                'rating': 5.0,
                'total_review': 20,
                'thumbnail_url': 'http://new.url/image.png'
            },
            {
                'place_id': 'place_xyz_789', # ID baru
                'nama': 'Lapangan Baru dari API',
                'alamat': 'Jl. API',
                'rating': 4.0,
                'total_review': 5,
                'thumbnail_url': 'http://api.url/image.png'
            }
        ]
        
        # Atur mock untuk mengembalikan data palsu ini
        mock_get_data.return_value = mock_api_results
        
        # Panggil view
        response = self.client.get(self.refresh_api_url)
        
        # Cek respons
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], '1 new venues added, 1 venues updated.')
        
        # Cek database
        self.assertEqual(LapanganPadel.objects.count(), 2) # Sekarang ada 2 lapangan
        
        # Cek lapangan yang diupdate (self.lapangan1)
        self.lapangan1.refresh_from_db()
        self.assertEqual(self.lapangan1.nama, 'Nama Lapangan Diupdate')
        self.assertEqual(self.lapangan1.rating, 5.0)
        
        # Cek lapangan yang baru dibuat
        new_lapangan_api = LapanganPadel.objects.get(place_id='place_xyz_789')
        self.assertEqual(new_lapangan_api.nama, 'Lapangan Baru dari API')

    @patch('home.views.get_google_maps_data')
    @override_settings(GOOGLE_MAPS_API_KEY='dummy_key')
    def test_refresh_from_api_empty_response(self, mock_get_data):
        """Tes refresh API gagal karena API mengembalikan data kosong."""
        self.client.login(username='user1', password='password123')
        
        # Atur mock untuk mengembalikan list kosong
        mock_get_data.return_value = []
        
        response = self.client.get(self.refresh_api_url)
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('No data received from Google Maps API', data['message'])

    @override_settings(GOOGLE_MAPS_API_KEY=None) # Set API key jadi None
    def test_refresh_from_api_no_key(self):
        """Tes refresh API gagal karena API key tidak ada di settings."""
        self.client.login(username='user1', password='password123')
        
        response = self.client.get(self.refresh_api_url)
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('Google Maps API key not configured', data['message'])