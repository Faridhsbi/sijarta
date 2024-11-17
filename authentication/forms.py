from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['nama', 'username', 'jenis_kelamin', 'no_hp', 'tgl_lahir', 'alamat', 'password1', 'password2']
        widgets = {
            'jenis_kelamin': forms.Select(choices=[
                ('', 'Pilih Jenis Kelamin'),  # Placeholder
                ('L', 'Laki-laki'),
                ('P', 'Perempuan')
            ]),
            'password': forms.PasswordInput(),
            'tgl_lahir': forms.DateInput(attrs={'type': 'date'}),
        }

class WorkerRegisterForm(forms.ModelForm):
    class Meta:
        model = Pekerja
        fields = ['nama_bank', 'nomor_rekening', 'npwp', 'link_foto']

    nama_bank_choices = [
        ('GoPay', 'GoPay'),
        ('OVO', 'OVO'),
        ('VA_BCA', 'Virtual Account BCA'),
        ('VA_BNI', 'Virtual Account BNI'),
        ('VA_Mandiri', 'Virtual Account Mandiri')
    ]
    
    nama_bank = forms.ChoiceField(choices=nama_bank_choices)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['link_foto'].widget = forms.URLInput()
        self.fields['link_foto'].label = 'URL Foto'
    
    def clean_no_hp(self):
        no_hp = self.cleaned_data.get('no_hp')
        if User.objects.filter(no_hp=no_hp).exists():
            raise forms.ValidationError("Nomor HP sudah terdaftar. Silakan login.")
        return no_hp

    def clean_npwp(self):
        npwp = self.cleaned_data.get('npwp')
        if Pekerja.objects.filter(npwp=npwp).exists():
            raise forms.ValidationError("NPWP sudah terdaftar.")
        return npwp


