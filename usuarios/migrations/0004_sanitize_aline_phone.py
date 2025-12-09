from django.db import migrations

NAME = "Aline"

def forward(apps, schema_editor):
    Pacientes = apps.get_model("usuarios", "Pacientes")
    for p in Pacientes.objects.filter(nome=NAME).only("id", "telefone"):
        if p.telefone:
            p.telefone = p.telefone.replace(" ", "").strip()
            p.save(update_fields=["telefone"])

def backward(apps, schema_editor):
    # no-op (cannot restore spaces reliably)
    pass

class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0003_update_rogerio_phone"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
