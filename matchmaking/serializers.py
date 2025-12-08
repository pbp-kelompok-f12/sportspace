from rest_framework import serializers
from .models import Match
from django.db.models import Exists, OuterRef, Q 

class MatchSerializer(serializers.ModelSerializer):
    # Akses properti yang sudah ada di model:
    mode_display = serializers.CharField(source='mode_display', read_only=True) # Mengakses @property mode_display
    player_count = serializers.IntegerField(read_only=True) # Mengakses @property player_count
    max_players = serializers.IntegerField(read_only=True)   # Mengakses @property max_players
    is_full = serializers.BooleanField(read_only=True)       # Mengakses @property is_full
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    # Field Status User-specific untuk Flutter (Tetap pakai SerializerMethodField)
    player_usernames = serializers.SerializerMethodField()
    is_user_registered = serializers.SerializerMethodField()
    is_user_creator = serializers.SerializerMethodField()
    can_user_join = serializers.SerializerMethodField()
    

    class Meta:
        model = Match
        fields = (
            'id', 'mode_display', 'created_by_username', 
            'player_count', 'max_players', 'player_usernames',
            'is_full', 'is_user_registered', 'is_user_creator',
            'can_user_join', 'temp_teammate', 
        )

    # --- Implementasi Method Fields ---

    def get_player_usernames(self, obj):
        # Mengambil username dari ManyToMany field 'players'
        return list(obj.players.values_list('username', flat=True))

    def get_user(self):
        # Mengambil user dari context request
        # Menggunakan .get() lebih aman
        return self.context.get('request').user

    def get_is_user_registered(self, obj):
        user = self.get_user()
        if not user or not user.is_authenticated: return False
        # Cek apakah user sudah ada di players M2M field
        return obj.players.filter(pk=user.pk).exists()
    
    def get_is_user_creator(self, obj):
        user = self.get_user()
        if not user or not user.is_authenticated: return False
        return obj.created_by == user

    def get_can_user_join(self, obj):
        user = self.get_user()
        if not user or not user.is_authenticated: return False
        
        is_registered = self.get_is_user_registered(obj)
        is_creator = self.get_is_user_creator(obj)
        is_full = obj.is_full # Mengakses properti model
        
        # Logika: Bisa join jika belum terdaftar, bukan creator, dan masih ada slot user
        # Menggunakan metode can_join() dari model yang sudah diperbaiki
        return obj.can_join() and not is_registered and not is_creator