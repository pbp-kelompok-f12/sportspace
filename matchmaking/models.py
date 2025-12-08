from django.db import models
from django.contrib.auth.models import User


class Match(models.Model):
    MODE_CHOICES = [
        ('1v1', '1 vs 1'),
        ('2v2', '2 vs 2'),
    ]
    
    # max_length diubah menjadi 3 (cukup untuk '1v1' atau '2v2')
    mode = models.CharField(max_length=3, choices=MODE_CHOICES) 
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_created')
    # Related name diubah agar lebih spesifik
    players = models.ManyToManyField(User, related_name='matches_joined', blank=True) 
    temp_teammate = models.CharField(max_length=100, blank=True, null=True)
    
    # is_full dihilangkan karena akan dihitung sebagai @property
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def mode_display(self):
        return self.get_mode_display()
        
    @property
    def player_count(self):
        """
        Menghitung jumlah slot yang terisi.
        - 1v1: Hanya menghitung jumlah user di M2M field 'players'.
        - 2v2: Menghitung jumlah user di 'players' + 1 (slot untuk temp_teammate) jika temp_teammate ada.
        """
        count = self.players.count()
        
        # Jika mode 2v2 dan temp_teammate (teman non-user) ada, hitung slotnya
        if self.mode == '2v2' and self.temp_teammate:
            # Karena creator (user) sudah masuk players, kita hanya perlu cek apakah slot teman terisi.
            # Slot pemain di 2v2 = 4. 2 User + 2 Teman.
            # Jika temp_teammate ada, itu mengisi satu slot.
            
            # Logika yang lebih aman: Hitung semua User terdaftar.
            # Jika mode 2v2 dan temp_teammate ada, tambahkan 1 slot terisi.
            if self.mode == '2v2':
                if self.temp_teammate:
                    count += 1
                # Batas jumlah user di players (2v2) = 2.
                # Batas jumlah slot terisi = 4.
            
            # Revisi: Karena player_count adalah jumlah slot yang terisi.
            # 1v1 (Max 2): players.count() (Max 2)
            # 2v2 (Max 4): players.count() (Max 2) + 1 (temp_teammate, jika ada) + 1 (player non-temp, jika ada)
            
            # Logika yang benar:
            # Player Count = Jumlah User terdaftar + (1 jika mode 2v2 dan temp_teammate ada)
            
            # Jika mode 2v2, slot temp_teammate (teman creator) mengisi satu slot.
            if self.mode == '2v2' and self.temp_teammate:
                # Slot yang terisi = (User 1 + User 2) + (Teman 1 + Teman 2)
                # Players.count() = Jumlah user (Max 2)
                # Jika temp_teammate ada, itu mengisi satu slot non-user.
                count = self.players.count()
                
                # Jika temp_teammate ada, itu mengisi slot pemain non-user.
                # Jika jumlah players.count() = 1 (Creator), temp_teammate mengisi slot kedua tim A. Total terisi = 2.
                # Jika ada user kedua (join), total players.count() = 2.
                
                # Logika paling sederhana: Hitung User + (1 jika 2v2 dan temp_teammate ada)
                return self.players.count() + (1 if self.temp_teammate else 0)
        
        return self.players.count()


    @property
    def max_players(self):
        """Mengembalikan maksimal slot pemain berdasarkan mode"""
        if self.mode == '1v1':
            return 2
        elif self.mode == '2v2':
            return 4
        return 0  

    @property
    def is_full(self):
        """Cek apakah match sudah penuh"""
        # Menggunakan properti yang sudah diperbaiki
        return self.player_count >= self.max_players

    def can_join(self, user=None):
        """Cek apakah match masih bisa diikuti oleh user tertentu"""
        if self.is_full:
            return False
        
        # Jika Match 2v2 dan temp_teammate belum ada, slot untuk user kedua (lawan) masih terbuka.
        
        # Di sini logika harus mengacu pada sisa slot user yang bisa join.
        # Maksimal user yang bisa join adalah max_players - (jumlah slot non-user).
        
        # Jika mode 1v1, max players user = 2.
        if self.mode == '1v1':
            return self.players.count() < 2
        
        # Jika mode 2v2:
        # Maksimal user yang bisa join = 2 (1 creator, 1 user lain).
        if self.mode == '2v2':
            # Jika ada temp_teammate, slot user tersisa 2 (creator + lawan user).
            # Jika pemain user sudah 2, user tidak bisa join.
            return self.players.count() < 2
            
        return False

    def __str__(self):
        return f"{self.mode} oleh {self.created_by.username}"

    class Meta:
        verbose_name_plural = "Matches"
        ordering = ['-created_at']