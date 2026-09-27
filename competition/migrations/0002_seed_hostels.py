from django.db import migrations

HOSTELS = [
    "Gandhi Bhawan", "Krishna Bhawan", "Vyas Bhawan", "Ram Bhawan",
    "Budh Bhawan", "Bhagirath Bhawan", "Shankar Bhawan", "Meera Bhawan",
    "Malviya Bhawan", "Srinivasa Ramanujan Bhawan", "CVR Bhawan",
    "Vishwakarma Bhawan", "MSA Bhawan", "Rana Pratap Bhawan", "Ashok Bhawan",
]


def seed_hostels(apps, schema_editor):
    Hostel = apps.get_model('competition', 'Hostel')
    for name in HOSTELS:
        Hostel.objects.get_or_create(name=name)


def remove_hostels(apps, schema_editor):
    Hostel = apps.get_model('competition', 'Hostel')
    Hostel.objects.filter(name__in=HOSTELS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0001_initial'),  # check this matches your actual previous migration filename
    ]

    operations = [
        migrations.RunPython(seed_hostels, remove_hostels),
    ]