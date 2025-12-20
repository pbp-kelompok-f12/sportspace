from django.db import models
from django.contrib.auth.models import User
from home.models import LapanganPadel
import review
from django.core.validators import MaxLengthValidator

# Create your models here.
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lapangan = models.ForeignKey(LapanganPadel, on_delete=models.CASCADE, related_name="reviews")
    rating = models.FloatField(default=0.0)
    comment = models.TextField(validators=[MaxLengthValidator(150)])
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return f'Review by {self.user.username} - Rating: {self.rating}'
    
    class Meta:
        unique_together = ('user', 'lapangan')  # 1 user 1 review per lapangan