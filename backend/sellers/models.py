from django.db import models

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('verified', 'Verified'),
    ('rejected', 'Rejected'),
]


class Seller(models.Model):
    user_id = models.IntegerField(unique=True, db_index=True)  # linked Django auth_user.id
    business_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, blank=True)
    category_focus = models.CharField(max_length=100, blank=True)
    registration_id = models.CharField(max_length=100, blank=True)
    business_description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.business_name
