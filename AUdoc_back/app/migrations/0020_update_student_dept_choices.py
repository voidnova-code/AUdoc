from django.db import migrations, models


NEW_CHOICES = [
    ("LING",    "Linguistics"),
    ("BEN",     "Bengali"),
    ("HINDI",   "Hindi"),
    ("MANI",    "Manipuri"),
    ("SANS",    "Sanskrit"),
    ("ASM",     "Assamese"),
    ("ENG",     "English"),
    ("ARAB",    "Arabic"),
    ("FREN",    "French"),
    ("ECON",    "Economics"),
    ("COM",     "Commerce"),
    ("POLSCI",  "Political Science"),
    ("HIST",    "History"),
    ("SOCIO",   "Sociology"),
    ("SWRK",    "Social Work"),
    ("MASSCOM", "Mass Communication"),
    ("VISART",  "Visual Arts"),
    ("PERART",  "Performing Arts"),
    ("PHIL",    "Philosophy"),
    ("EDU",     "Education"),
    ("BBA",     "Business Administration"),
    ("LIS",     "Library & Information Science"),
    ("PHY",     "Physics"),
    ("CHEM",    "Chemistry"),
    ("MATH",    "Mathematics"),
    ("STAT",    "Statistics"),
    ("CSE",     "Computer Science"),
    ("LSBIO",   "Life Science & Bioinformatics"),
    ("MICRO",   "Microbiology"),
    ("BIOTECH", "Biotechnology"),
    ("IT",      "Information Technology"),
    ("ECE",     "Electronics & Telecommunication"),
    ("AGENG",   "Agricultural Engineering"),
    ("ECO",     "Ecology & Environmental Science"),
    ("EARTH",   "Earth Sciences"),
    ("LAW",     "Law"),
    ("PHARMA",  "Pharmaceutical Sciences"),
    ("OTHER",   "Other"),
]


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0019_remove_helpdesk_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studentregistration",
            name="department",
            field=models.CharField(choices=NEW_CHOICES, max_length=10),
        ),
        migrations.AlterField(
            model_name="studentprofile",
            name="department",
            field=models.CharField(choices=NEW_CHOICES, max_length=10),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="student_department",
            field=models.CharField(choices=NEW_CHOICES, max_length=10),
        ),
    ]
