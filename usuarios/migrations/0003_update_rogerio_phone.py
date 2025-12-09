from django.db import migrations

PHONE = "5511992550655"
NAME = "Rogério"


def forward(apps, schema_editor):
    Pacientes = apps.get_model("usuarios", "Pacientes")
    try:
        obj = Pacientes.objects.get(nome=NAME)
        obj.telefone = PHONE
        obj.save()
    except Pacientes.DoesNotExist:
        pass


def backward(apps, schema_editor):
    Pacientes = apps.get_model("usuarios", "Pacientes")
    try:
        obj = Pacientes.objects.get(nome=NAME)
        obj.telefone = ""
        obj.save()
    except Pacientes.DoesNotExist:
        pass

class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0002_alter_pacientes_telefone"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
