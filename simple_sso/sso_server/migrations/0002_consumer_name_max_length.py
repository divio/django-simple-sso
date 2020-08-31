from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sso_server', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='name',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
