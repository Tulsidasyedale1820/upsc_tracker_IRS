from django.db import migrations

def clear_all_production_records(apps, schema_editor):
    # Dynamically look up the models from the active context
    User = apps.get_model('auth', 'User')
    Exam = apps.get_model('tracker', 'Exam')
    Subject = apps.get_model('tracker', 'Subject')
    Topic = apps.get_model('tracker', 'Topic')
    SubTopic = apps.get_model('tracker', 'SubTopic')

    # Execute full system purge across the cloud cluster tables
    SubTopic.objects.all().delete()
    Topic.objects.all().delete()
    Subject.objects.all().delete()
    Exam.objects.all().delete()
    User.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        # This tells Django to run right after your last migration update
        ('tracker', '0004_remove_subtopic_time_spent_mins_and_more'),
    ]

    operations = [
        migrations.RunPython(clear_all_production_records),
    ]