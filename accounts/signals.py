from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import User,UserProfile
@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        print('user profile is created')
    else:
        try:
            profile=UserProfile.objects.get(user=instance)
            print('user is updated')
        except:
            UserProfile.objects.create(user=instance)
            print('profile did not exist so created one')
        print('User updated')

@receiver(pre_save,sender=User)
def pre_save_profile_receiver(sender,instance,**kwargs):
    print(instance.username,'this user is saved')
