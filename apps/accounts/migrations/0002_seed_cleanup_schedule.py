from django.db import migrations


def create_cleanup_schedule(apps, schema_editor):
    Schedule = apps.get_model('django_q', 'Schedule')
    Schedule.objects.get_or_create(
        name='Cleanup unverified accounts',
        defaults={
            'func': 'apps.accounts.tasks.cleanup_unverified_accounts',
            'schedule_type': 'D',
            'repeats': -1,
        }
    )


def remove_cleanup_schedule(apps, schema_editor):
    Schedule = apps.get_model('django_q', 'Schedule')
    Schedule.objects.filter(name='Cleanup unverified accounts').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('django_q', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_cleanup_schedule,
            reverse_code=remove_cleanup_schedule,
        ),
    ]