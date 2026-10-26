from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nota", "0009_alter_nota_berat"),
    ]

    operations = [
        migrations.AlterField(
            model_name="itempakaian",
            name="jenis",
            field=models.CharField(
                choices=[('Kaos L. Pendek', 'Kaos Lengan Pendek'), ('Kaos L. Panjang', 'Kaos Lengan Panjang'), ('Kemeja L. Pendek', 'Kemeja Lengan Pendek'), ('Kemeja L. Panjang', 'Kemeja Lengan Panjang'), ('Celana Panjang', 'Celana Panjang'), ('Celana Pendek', 'Celana Pendek'), ('Celana Dalam', 'Celana Dalam'), ('Kerudung', 'Kerudung'), ('Jaket', 'Jaket'), ('Sprei', 'Sprei'), ('Selimut', 'Selimut'), ('Sarung Bantal', 'Sarung Bantal'), ('Daster', 'Daster'), ('Sarung', 'Sarung'), ('Polo Osin', 'Polo Osin'), ('Kemeja Osin', 'Kemeja Osin'), ('Sajadah', 'Sajadah'), ('Training Osin', 'Training Osin'), ('Batik Osin', 'Batik Osin'), ('Koko Osin', 'Koko Osin'), ('Kupluk', 'Kupluk'), ('Dasi', 'Dasi'), ('Jas', 'Jas'), ('Kaos Osin', 'Kaos Osin'), ('Baju Koko', 'Baju Koko'), ('Gamis', 'Gamis'), ('Baju Tidur', 'Baju Tidur'), ('Baju Sma', 'Baju SMA'), ('Batik Sma', 'Batik SMA'), ('Olahraga Sekolah', 'Olahraga Sekolah'), ('Baju Sekolah', 'Baju Sekolah'), ('Bra', 'Bra'), ('Singlet', 'Singlet'), ('Kaos Kaki', 'Kaos Kaki'), ('Handuk', 'Handuk'), ('Ciput', 'Ciput'), ('Hoodie', 'Hoodie'), ('Lekton', 'Lekton'), ('Batik L. Panjang', 'Batik Lengan Panjang')],
                max_length=100,
            ),
        ),
    ]
