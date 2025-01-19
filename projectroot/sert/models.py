from datetime import datetime
import gettext
from django.contrib.admin.utils import label_for_field
_ = gettext.gettext
from django.db import models
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import get_object_or_404
from django.http import Http404

from sert.models_data import METHODS_LIST, ITEM_UNITS


class SertNumber(models.Model):
    id = models.CharField(primary_key=True, unique=True, blank=True, max_length=500, verbose_name='Идентификатор/Номер сертификата') # number-year
    number = models.PositiveIntegerField(blank=True, verbose_name='Номер по порядку')
    year = models.PositiveIntegerField(blank=True, verbose_name='Год')

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Номер сертификата'
        verbose_name_plural = 'Номера сертификатов'
        ordering = ['-year', '-number']


class Sert(models.Model):
    ## number_spg-sert_type-number_unique
    id = models.CharField(primary_key=True, unique=True, max_length=500, blank=True, verbose_name='Идентификатор')
    # для отбора на печать
    is_print = models.BooleanField(default=True, blank=True, null=True, verbose_name='На печать')
    # для управления Sert
    number_spg = models.ForeignKey('Kernel', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Номер СПГ')
    sert_type = models.CharField(choices=METHODS_LIST, default='НАСОС', max_length=500, verbose_name='Тип сертификата')
    number_unique = models.ForeignKey('SertNumber', on_delete=models.CASCADE, blank=True, verbose_name='Номер сертификата')
    date = models.DateField(default=datetime.now, verbose_name='Дата сертификата')
    galvan_date = models.DateField(default=datetime.now, verbose_name='Дата для гальваники')
    conclusion_type = models.ForeignKey('Conclusion', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Тип заключения')
    is_drag_met = models.BooleanField(default=False, blank=True, null=True, verbose_name='Есть драгоценные металлы')
    # guarantee_type = models.ForeignKey('Guarantee', on_delete=models.CASCADE, blank=True, null=True)
    # sign_type = models.ForeignKey('Signatories', on_delete=models.CASCADE, blank=True, null=True)
    guarantee_type = models.CharField(max_length=100, blank=True, null=True, verbose_name='Тип гарантии')
    sign_type = models.CharField(max_length=100, blank=True, null=True, verbose_name='Тип подписантов')
    # для редактирования при добавлении

    def __str__(self):
        return f'{self.id}'

    def get_absolute_url(self):
    #     # return reverse_lazy('view_news', kwargs={'news_id': self.pk})
        return reverse_lazy('sertupdate', kwargs={'pk': self.id}) # для ViewNews класса

    class Meta:
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'
        ordering = ['-date']


class Kernel(models.Model):
    number_spg = models.CharField(primary_key=True, unique=True, max_length=200, verbose_name='Номер СПГ')
    designation = models.TextField(verbose_name='Обозначение')
    denomination = models.TextField(null=True, blank=True, verbose_name='Наименование')
    quantity = models.PositiveIntegerField(default=1, blank=True, verbose_name='Количество')
    is_atom = models.BooleanField(default=False, blank=True, null=True, verbose_name='Атомка')
    atom_contract = models.TextField(null=True, blank=True, verbose_name='Атомный контракт')
    # для редактирования при добавлении

    def __str__(self):
        return f'{self.number_spg}'

    def get_absolute_url(self):
        # return reverse_lazy('view_news', kwargs={'news_id': self.pk})
        return reverse_lazy('kernelupdate', kwargs={'pk': self.number_spg}) # для ViewNews класса

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        # ordering = ['-created_at']


class Attachment(models.Model):
    # для управления отбором
    number_spg = models.ForeignKey('Kernel', on_delete=models.CASCADE, verbose_name='Номер СПГ')
    number_unique = models.ForeignKey('SertNumber', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Номер сертификата')
    sert_type = models.CharField(choices=METHODS_LIST, default='РЕМКОМПЛЕКТ', max_length=500, blank=True, verbose_name='Тип сертификата')

    designation = models.TextField(blank=True, verbose_name='Обозначение')
    denomination = models.TextField(null=True, blank=True, verbose_name='Наименование')
    quantity = models.DecimalField(default=1.0, max_digits=7, decimal_places=3, blank=True, verbose_name='Количество')
    item_units = models.CharField(choices=ITEM_UNITS, default='INT', max_length=100, blank=True, verbose_name='Единицы измерения')

    # для управления вложенностью и симметрией
    n_index = models.IntegerField(blank=True, null=True, verbose_name='n_index')
    a_index = models.CharField(max_length=500, blank=True, null=True, verbose_name='a_index')
    b_index = models.CharField(max_length=500, blank=True, null=True, verbose_name='b_index')
    a1_index = models.CharField(max_length=500, blank=True, null=True, verbose_name='a1_index')
    b1_index = models.CharField(max_length=500, blank=True, null=True, verbose_name='b1_index')
    a2_index = models.CharField(max_length=500, blank=True, null=True, verbose_name='a2_index')
    b2_index = models.CharField(max_length=500, blank=True, null=True, verbose_name='b2_index')
    is_one = models.BooleanField(default=False, verbose_name='is_one')
    is_two = models.BooleanField(default=False, verbose_name='is_two')
    is_three = models.BooleanField(default=False, verbose_name='is_three')
    is_four = models.BooleanField(default=False, verbose_name='is_four')

    # melt_id для отбора плавки
    melt_number = models.CharField(max_length=300, blank=True, null=True, verbose_name='Номер плавки')
    material_id = models.CharField(max_length=300, blank=True, null=True, verbose_name='ID материала')
    melt_year = models.CharField(max_length=300, blank=True, null=True, verbose_name='Год плавки')
    melt_passport = models.CharField(max_length=300, blank=True, null=True, verbose_name='Номер паспорта плавки')
    is_cast = models.BooleanField(null=True, blank=True, default=False, verbose_name='Это отливка')

    # дополнительные данные
    is_by_gost_material_number = models.BooleanField(default=True, blank=True, null=True, verbose_name='Мех.св-ва по ГОСТ')
    galvan_material = models.CharField(max_length=300, blank=True, null=True, verbose_name='Материал для гальваники')
    galvan_units = models.CharField(max_length=300, blank=True, null=True, verbose_name='Ед.изм. для гальваники')

    def __str__(self):
        return f'{self.id}-{self.number_spg}-{self.sert_type}'

    def get_absolute_url(self):
        # return reverse_lazy('view_news', kwargs={'news_id': self.pk})
        return reverse_lazy('attachmentupdate', kwargs={'pk': self.id}) # для ViewNews класса

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
        # ordering = ['-created_at']


class Melt(models.Model):
    ## melt_number-material_id-melt_year-melt_passport
    melt_id = models.CharField(primary_key=True, unique=True, max_length=600, blank=True, verbose_name='Идентификатор')
    melt_number = models.CharField(max_length=300, verbose_name='Номер плавки')
    material_id = models.CharField(max_length=300, verbose_name='ID материала')
    melt_year = models.CharField(max_length=300, verbose_name='Год плавки')
    melt_passport = models.CharField(max_length=300, verbose_name='Номер паспорта плавки')
    by_gost_number = models.PositiveIntegerField(blank=True, verbose_name='Номер по ГОСТ')

    carboneum = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='C (углерод)')  # C (углерод)
    manganum = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='Mn (марганец)')  # Mn (марганец)
    silicium = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='Si (кремний)')  # Si (кремний)
    sulfur = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='S (сера)')  # S (сера)
    phosphorus = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='P (фосфор)')  # P (фосфор)
    chromium = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='Cr (хром)')  # Cr (хром)
    molybdaenum = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='Mo (молибден)')  # Mo (молибден)
    niccolum = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='Ni (никель)')  # Ni (никель)
    niobium = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='Nb (ниобий)')  # Nb (ниобий)
    titanium = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='Ti (титан)')  # Ti (титан)
    cuprum = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='Cu (медь)')   # Cu (медь)
    magnesium = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='Mg (магний)')  # Mg (магний)
    ferrum = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True, verbose_name='Fe (железо)')  # Fe (железо)

    tensile_strength = models.PositiveIntegerField(blank=True, null=True, verbose_name='Предел прочности')  # Предел прочности
    yield_strength = models.PositiveIntegerField(blank=True, null=True, verbose_name='Предел текучести')  # Предел текучести
    relative_extension = models.PositiveIntegerField(blank=True, null=True, verbose_name='Относительное удлинение')  # Относительное удлинение
    relative_narrowing = models.PositiveIntegerField(blank=True, null=True, verbose_name='Относительное сужение')  # Относительное сужение
    impact_strength = models.CharField(max_length=300, blank=True, null=True, verbose_name='Ударная вязкость')  # Ударная вязкость
    impact_strength_60KCU = models.CharField(max_length=300, blank=True, null=True, verbose_name='Ударная вязкость КСU-60')  # Ударная вязкость КСU-60
    impact_strength_60KCV = models.CharField(max_length=300, blank=True, null=True, verbose_name='Ударная вязкость КСV-60')  # Ударная вязкость КСV-60
    hardness = models.CharField(max_length=300, blank=True, null=True, verbose_name='Твердость')  # Твердость
    mkk = models.CharField(max_length=300, blank=True, null=True, verbose_name='МКК')  # МКК

    def __str__(self):
        return f'{self.melt_id}'

    def get_absolute_url(self):
        # return reverse_lazy('view_news', kwargs={'news_id': self.pk})
        return reverse_lazy('meltupdate', kwargs={'pk': self.melt_id}) # для ViewNews класса

    class Meta:
        verbose_name = 'Плавка'
        verbose_name_plural = 'Плавки'
        ordering = ['-melt_year']


class Signatories(models.Model):
    # id
    sign_type = models.CharField(max_length=300, verbose_name='Тип подписантов')
    sign_person = models.CharField(max_length=300, verbose_name='ФИО подписанта')
    sign_job_title = models.CharField(max_length=300, verbose_name='Должность подписанта')

    def __str__(self):
        return f'{self.sign_type}'

    class Meta:
        verbose_name = 'Подписанты'
        verbose_name_plural = 'Подписанты'
        ordering = ['-sign_type']


class Conclusion(models.Model):
    conclusion_type = models.CharField(primary_key=True, unique=True, max_length=300, verbose_name='Тип заключения')
    conclusion_text = models.TextField(verbose_name='Текст заключения')

    def __str__(self):
        return f'{self.conclusion_type}'

    class Meta:
        verbose_name = 'Заключение'
        verbose_name_plural = 'Заключения'
        ordering = ['-conclusion_type']


class Guarantee(models.Model):
    # id
    guarantee_type = models.CharField(max_length=300, verbose_name='Тип гарантии')
    guarantee_text = models.TextField(verbose_name='Текст гарантии')

    def __str__(self):
        return f'{self.guarantee_type}'

    class Meta:
        verbose_name = 'Гарантия'
        verbose_name_plural = 'Гарантии'
        ordering = ['-guarantee_type']

