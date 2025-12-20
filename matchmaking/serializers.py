from rest_framework import serializers
from .models import Match


class MatchSerializer(serializers.ModelSerializer):
    mode_display = serializers.CharField(read_only=True)
    player_count = serializers.IntegerField(read_only=True)
    max_players = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True
    )

    player_usernames = serializers.SerializerMethodField()
    is_user_registered = serializers.SerializerMethodField()
    is_user_creator = serializers.SerializerMethodField()
    can_user_join = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            'id',
            'mode_display',
            'created_by_username',
            'player_count',
            'max_players',
            'player_usernames',
            'is_full',
            'is_user_registered',
            'is_user_creator',
            'can_user_join',
            'temp_teammate',
        ]

    def get_player_usernames(self, obj):
        return list(obj.players.values_list('username', flat=True))

    def _get_user(self):
        request = self.context.get('request')
        return request.user if request else None

    def get_is_user_registered(self, obj):
        user = self._get_user()
        return user.is_authenticated and obj.players.filter(pk=user.pk).exists()

    def get_is_user_creator(self, obj):
        user = self._get_user()
        return user.is_authenticated and obj.created_by == user

    def get_can_user_join(self, obj):
        user = self._get_user()
        if not user or not user.is_authenticated:
            return False
        return (
            obj.can_join()
            and not self.get_is_user_registered(obj)
            and not self.get_is_user_creator(obj)
        )
