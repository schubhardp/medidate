from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Paciente


@receiver(post_save, sender=User)
def ensure_paciente_profile(sender, instance: User, created, **kwargs):
    if created:
        Paciente.objects.get_or_create(user=instance)
