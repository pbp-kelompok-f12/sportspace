from django.db import models
from django.contrib.auth.models import User


class Match(models.Model):
    MODE_CHOICES = [
        ('1v1', '1 vs 1'),
        ('2v2', '2 vs 2'),
    ]

    mode = models.CharField(max_length=3, choices=MODE_CHOICES)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='matches_created'
    )
    players = models.ManyToManyField(
        User, related_name='matches_joined', blank=True
    )
    temp_teammate = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def mode_display(self):
        return self.get_mode_display()

    @property
    def player_count(self):
        count = self.players.count()
        if self.mode == '2v2' and self.temp_teammate:
            count += 1
        return count

    @property
    def max_players(self):
        if self.mode == '1v1':
            return 2
        if self.mode == '2v2':
            return 4
        return 0

    @property
    def is_full(self):
        return self.player_count >= self.max_players

    def can_join(self):
        if self.is_full:
            return False

        if self.mode == '1v1':
            return self.players.count() < 2

        if self.mode == '2v2':
            return self.players.count() < 2

        return False

    def __str__(self):
        return f"{self.mode} oleh {self.created_by.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Matches"
