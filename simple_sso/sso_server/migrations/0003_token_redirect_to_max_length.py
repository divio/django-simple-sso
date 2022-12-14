from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sso_server', '0002_consumer_name_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='redirect_to',
            field=models.CharField(max_length=1023),
        ),
    ]
