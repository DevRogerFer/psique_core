# Generated migration to fix Gravacoes model fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultas', '0003_alter_pergunta_data_treinamento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gravacoes',
            name='data',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='gravacoes',
            name='transcricao',
            field=models.TextField(blank=True, default=''),
        ),
    ]
