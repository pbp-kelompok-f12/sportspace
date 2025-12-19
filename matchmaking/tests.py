from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from .models import Match


class MatchModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="12345")

    def test_str_representation(self):
        match = Match.objects.create(mode="1v1", created_by=self.user)
        self.assertEqual(str(match), "1v1 oleh tester")

    def test_player_count_and_max_players(self):
        match1 = Match.objects.create(mode="1v1", created_by=self.user)
        match1.players.add(self.user)
        self.assertEqual(match1.player_count(), 1)
        self.assertEqual(match1.max_players(), 2)

        match2 = Match.objects.create(mode="2v2", created_by=self.user, temp_teammate="Adit")
        match2.players.add(self.user)
        self.assertEqual(match2.player_count(), 2)
        self.assertEqual(match2.max_players(), 4)

    def test_can_join_behavior(self):
        match = Match.objects.create(mode="1v1", created_by=self.user)
        match.players.add(self.user)
        self.assertTrue(match.can_join())

        # Tambahkan user kedua, match sudah penuh
        match.players.add(User.objects.create_user(username="u2"))
        self.assertFalse(match.can_join())

    def test_unknown_mode_defaults(self):
        """Pastikan method tidak error pada mode aneh"""
        match = Match.objects.create(mode="custom", created_by=self.user)
        self.assertEqual(match.max_players(), 0)
        self.assertFalse(match.can_join())


class MatchmakingViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="pass")
        self.user2 = User.objects.create_user(username="user2", password="pass")

    def login(self):
        self.client.login(username="user1", password="pass")

    def test_redirect_if_not_logged_in(self):
        urls = [
            reverse('matchmaking:home'),
            reverse('matchmaking:one_vs_one'),
            reverse('matchmaking:two_vs_two'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/accounts/login/", response.url)

    def test_home_view(self):
        self.login()
        response = self.client.get(reverse('matchmaking:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'matchmaking/matchmaking.html')

    def test_create_one_vs_one_match(self):
        self.login()
        response_get = self.client.get(reverse('matchmaking:one_vs_one'))
        self.assertEqual(response_get.status_code, 200)
        response_post = self.client.post(reverse('matchmaking:one_vs_one'))
        self.assertEqual(response_post.status_code, 302)
        self.assertEqual(Match.objects.count(), 1)
        match = Match.objects.first()
        self.assertEqual(match.mode, '1v1')
        self.assertIn(self.user, match.players.all())

    def test_create_two_vs_two_match(self):
        self.login()
        response_get = self.client.get(reverse('matchmaking:two_vs_two'))
        self.assertEqual(response_get.status_code, 200)
        response_post = self.client.post(reverse('matchmaking:two_vs_two'), {'teammate': 'Budi'})
        self.assertEqual(response_post.status_code, 302)
        match = Match.objects.first()
        self.assertEqual(match.temp_teammate, 'Budi')
        self.assertIn(self.user, match.players.all())

    def test_create_two_vs_two_match_no_teammate(self):
        self.login()
        response_post = self.client.post(reverse('matchmaking:two_vs_two'))
        self.assertEqual(response_post.status_code, 302)
        match = Match.objects.first()
        self.assertEqual(match.temp_teammate, '')

    def test_match_detail_view(self):
        self.login()
        match = Match.objects.create(mode='1v1', created_by=self.user)
        response = self.client.get(reverse('matchmaking:match_detail', args=[match.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'matchmaking/match_detail.html')

    def test_join_match_success(self):
        self.login()
        match = Match.objects.create(mode='1v1', created_by=self.user2)
        response = self.client.post(reverse('matchmaking:join_match', args=[match.id]))
        match.refresh_from_db()
        self.assertIn(self.user, match.players.all())
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("Berhasil bergabung" in msg for msg in messages))

    def test_join_match_already_in(self):
        self.login()
        match = Match.objects.create(mode='1v1', created_by=self.user)
        match.players.add(self.user)
        response = self.client.post(reverse('matchmaking:join_match', args=[match.id]))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("sudah terdaftar" in msg for msg in messages))

    def test_join_match_full(self):
        self.login()
        match = Match.objects.create(mode='1v1', created_by=self.user2)
        user3 = User.objects.create_user(username="u3", password="p")
        match.players.add(self.user2, user3)
        match.is_full = True
        match.save()
        response = self.client.post(reverse('matchmaking:join_match', args=[match.id]))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("penuh" in msg for msg in messages))

    def test_join_match_not_found(self):
        self.login()
        response = self.client.post(reverse('matchmaking:join_match', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_match_by_creator(self):
        self.login()
        match = Match.objects.create(mode='1v1', created_by=self.user)
        response = self.client.post(reverse('matchmaking:delete_match', args=[match.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Match.objects.count(), 0)

    def test_delete_match_by_non_creator(self):
        self.login()
        match = Match.objects.create(mode='1v1', created_by=self.user2)
        response = self.client.post(reverse('matchmaking:delete_match', args=[match.id]))
        match.refresh_from_db()
        self.assertEqual(Match.objects.count(), 1)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("tidak memiliki izin" in msg for msg in messages))

    def test_delete_nonexistent_match(self):
        self.login()
        response = self.client.post(reverse('matchmaking:delete_match', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_join_match_cannot_join(self):
        """Tes ketika match sudah penuh atau tidak bisa diikuti."""
        self.login()
        match = Match.objects.create(mode='1v1', created_by=self.user2, is_full=True)
        response = self.client.post(reverse('matchmaking:join_match', args=[match.id]))
        self.assertRedirects(response, reverse('matchmaking:home'))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("tidak dapat diikuti" in msg or "penuh" in msg for msg in messages))

    def test_delete_match_redirects_non_creator(self):
        """Tes memastikan non-creator diarahkan ulang setelah gagal menghapus."""
        self.login()
        match = Match.objects.create(mode='1v1', created_by=self.user2)
        response = self.client.post(reverse('matchmaking:delete_match', args=[match.id]))
        self.assertRedirects(response, reverse('matchmaking:home'))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("tidak memiliki izin" in msg for msg in messages))
