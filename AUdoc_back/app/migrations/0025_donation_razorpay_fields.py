from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0024_alter_todaysappointment_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="donation",
            name="razorpay_order_id",
            field=models.CharField(blank=True, max_length=120, verbose_name="Razorpay Order ID"),
        ),
        migrations.AddField(
            model_name="donation",
            name="razorpay_payment_id",
            field=models.CharField(blank=True, max_length=120, verbose_name="Razorpay Payment ID"),
        ),
        migrations.AddField(
            model_name="donation",
            name="razorpay_signature",
            field=models.CharField(blank=True, max_length=255, verbose_name="Razorpay Signature"),
        ),
    ]
