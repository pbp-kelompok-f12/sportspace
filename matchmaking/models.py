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
    temp_teammate = models.CharField(max_length=100, blank=True, null=True)
    is_full = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def player_count(self):
        """Menghitung jumlah pemain saat ini"""
        return self.players.count() + (1 if self.mode == '2v2' and self.temp_teammate else 0)

    def max_players(self):
        """Mengembalikan maksimal pemain berdasarkan mode"""
        if self.mode == '1v1':
            return 2
        elif self.mode == '2v2':
            return 4
        else:
            return 0  

    def can_join(self):
        """Cek apakah match masih bisa diikuti"""
        if self.is_full:
            return False
        return self.player_count() < self.max_players()

    def __str__(self):
        return f"{self.mode} oleh {self.created_by.username}"

    class Meta:
        verbose_name_plural = "Matches"
        ordering = ['-created_at']