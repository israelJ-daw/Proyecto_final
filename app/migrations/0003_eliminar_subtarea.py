# Generated manually — eliminación del modelo Subtarea

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_crear_grupo_usuario'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Subtarea',
        ),
    ]
