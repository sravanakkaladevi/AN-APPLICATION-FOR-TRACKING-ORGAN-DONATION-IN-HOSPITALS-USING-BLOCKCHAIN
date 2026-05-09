from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_hospitalprofile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='hospitalprofile',
            name='background_image',
            field=models.ImageField(blank=True, null=True, upload_to='hospital_backgrounds/'),
        ),
    ]
