# from django.db import models
# import uuid
# from django.contrib.auth.models import AbstractUser
# from datetime import date

# class User(AbstractUser):
#     # Menggunakan UUID sebagai primary key
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     # username = models.CharField(max_length=255 , unique=True)
#     nama = models.CharField(max_length=255)
#     jenis_kelamin = models.CharField(max_length=1, choices=[('L', 'Laki-laki'), ('P', 'Perempuan')], default='L')
#     no_hp = models.CharField(max_length=15, unique=True)
#     # password = models.CharField(max_length=255) 
#     tgl_lahir = models.DateField(default=date.today)
#     alamat = models.CharField(max_length=255)
#     saldo_my_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     role = models.CharField(max_length=10, choices=[('pengguna', 'Pengguna'), ('pekerja', 'Pekerja')])

#     USERNAME_FIELD = 'no_hp'  # Harus ada
#     def __str__(self):
#         return self.nama


# class Pengguna(models.Model):
#     id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
#     level = models.CharField(max_length=50)  # Anda bisa menyesuaikan max_length sesuai kebutuhan

#     def __str__(self):
#         return f"Pelanggan: {self.id.nama} - Level: {self.level}"


# class Pekerja(models.Model):
#     # Menggunakan UUID sebagai primary key dan sebagai foreign key ke Pengguna
#     id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
#     nama_bank = models.CharField(max_length=100)
#     nomor_rekening = models.CharField(max_length=16)
#     npwp = models.CharField(max_length=16, unique=True)
#     link_foto = models.URLField(max_length=200)
#     rating = models.FloatField(default=1.0)
#     jml_pesanan_selesai = models.IntegerField(default=0)

#     def __str__(self):
#         return f"Pekerja: {self.id.nama} - Rating: {self.rating}"