from django.db import models
from django.contrib.auth.models import User

class Match(models.Model):
    MODE_CHOICES = [
        ('1v1', '1 vs 1'),
        ('2v2', '2 vs 2'),
    ]
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    players = models.ManyToManyField(User, related_name='matches')
    temp_teammate = models.CharField(max_length=100, blank=True, null=True)  # ⬅️ Tambahan
    is_full = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def player_count(self):
        # Untuk 2v2, hitung +1 karena ada teman non-user
        return self.players.count() + (1 if self.mode == '2v2' and self.temp_teammate else 0)

    def max_players(self):
        return 2 if self.mode == '1v1' else 4

    def can_join(self):
        return self.player_count() < self.max_players()

    def __str__(self):
        return f"{self.mode} oleh {self.created_by.username}"
