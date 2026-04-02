from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0021_alter_appointment_student_department_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctor",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="doctors/", verbose_name="Profile Photo"),
        ),
    ]
