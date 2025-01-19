from collections import namedtuple
from decimal import Decimal, InvalidOperation
from django import forms
from datetime import datetime
import random


from sert.models import (
    SertNumber,
    Sert,
    Kernel,
    Conclusion,
    Guarantee,
    Signatories,
    Attachment,
    Melt,
)
from sert.models_data import (
    METHODS_LIST,
    CONCLUSIONS_NAMES,
    ITEM_UNITS,
)
from sert.models_inspector import Inspector
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class BaseForm(forms.Form):
    file = forms.FileField()


class SertNumberForm(forms.ModelForm):

    def clean_number(self):
        number = self.cleaned_data['number']

        def get_numder():
            last = SertNumber.objects.order_by("-year").order_by("-number")[0]
            number = last.number + 1
            return number

        if not number:
            number = get_numder()
        else:
            r_number, is_good = Inspector.try_integeralization(number)
            if not is_good:
                error_text = f'{number} - Недопустимое значение'
                self.add_error('number', ValidationError(error_text))
                number = get_numder()
            else:
                number = r_number
        return number

    def clean_year(self):
        year = self.cleaned_data['year']

        def get_year():
            last = SertNumber.objects.order_by("-year").order_by("-number")[0]
            year = last.year
            return year

        if not year:
            year = get_year()
        else:
            r_year, is_good = Inspector.try_integeralization(year)
            if not is_good:
                error_text = f'{year} - Недопустимое значение'
                self.add_error('year', ValidationError(error_text))
                year = get_year()
            else:
                year = r_year
        return year

    def clean(self):
        if self.errors:
            raise ValidationError('Ошибка в данных')

        id = self.cleaned_data['id']

        number = self.cleaned_data['number']
        year = self.cleaned_data['year']

        def inspection_id(id):
            is_exist = Inspector.is_unique_exist_in_model(id, self._meta.model)
            if is_exist:
                error_text = f'{id} - Такой номер сертификата уже существует'
                raise ValidationError(error_text)

        if not id:
            id = f'{number}-{year}'
            inspection_id(id)
        else:
            if id != f'{number}-{year}':
                inspection_id(id)

        self.cleaned_data['id'] = id
        super().clean()

    class Meta:
        model = SertNumber
        fields = [
            'id',
            'number',
            'year',
        ]


class MyDateField(forms.DateField):

    def to_python (self, value):
        if value:
            if not isinstance(value, type(datetime.now().date())):
                try:
                    r_value = datetime.strptime(value, '%d.%m.%Y').date()
                except ValueError:
                    try:
                        r_value = datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        r_value = datetime.now().date()
            else:
                r_value = value
        else:
            r_value = datetime.now().date()
        return r_value


class SertForm(forms.ModelForm):

    def clean_is_print(self):
        is_print = self.cleaned_data['is_print']
        if isinstance(is_print, type(None)):
            is_print = True
        return is_print

    def clean_number_spg(self):
        KernelObj  = self.cleaned_data['number_spg']
        if not KernelObj:
            error_text = 'Номер СПГ не указан'
            self.add_error('number_spg', ValidationError(error_text))
        else:
            is_exist = Inspector.is_exist_in_model(KernelObj.number_spg, Kernel, 'number_spg')
            if not is_exist:
                error_text = f'{KernelObj.number_spg} - Записи с таким номером СПГ нет в Kernel'
                self.add_error('number_spg', ValidationError(error_text))
        return KernelObj

    def clean_sert_type(self):
        sert_type = self.cleaned_data['sert_type']
        if not sert_type:
            sert_type = METHODS_LIST['НАСОС']
        else:
            is_exist = Inspector.is_exist_in_dict(sert_type, METHODS_LIST)
            if not is_exist:
                error_text = f'{sert_type} - Такой тип сертификата не предусмотрен'
                self.add_error('sert_type', ValidationError(error_text))
        return sert_type

    def clean_date(self):
        date = self.cleaned_data['date']
        if date:
            date = date
        else:
            date = datetime.now().date()
        return date

    def clean_galvan_date(self):
        galvan_date = self.cleaned_data['galvan_date']
        if galvan_date:
            galvan_date = galvan_date
        else:
            galvan_date = datetime.now().date()
        return galvan_date

    def clean_conclusion_type(self):
        ConclusionObj = self.cleaned_data['conclusion_type']
        if not ConclusionObj:
            pass
        else:
            is_exist = Inspector.is_exist_in_model(ConclusionObj.conclusion_type, Conclusion, 'conclusion_type')
            if not is_exist:
                error_text = f'{ConclusionObj.conclusion_type} - Такого типа заключения не существует'
                self.add_error('conclusion_type', ValidationError(error_text))
        return ConclusionObj

    def clean_is_drag_met(self):
        is_drag_met = self.cleaned_data['is_drag_met']
        if isinstance(is_drag_met, type(None)):
            is_drag_met = False
        return is_drag_met

    def clean_guarantee_type(self):
        guarantee_type = self.cleaned_data['guarantee_type']
        if not guarantee_type:
            pass
        else:
            is_exist = Inspector.is_exist_in_model(guarantee_type, Guarantee, 'guarantee_type')
            if not is_exist:
                error_text = f'{guarantee_type} - Такого типа гарантии не существует'
                self.add_error('guarantee_type', ValidationError(error_text))

        return guarantee_type

    def clean_sign_type(self):
        sign_type = self.cleaned_data['sign_type']
        if not sign_type:
            pass
        else:
            is_exist = Inspector.is_exist_in_model(sign_type, Signatories, 'sign_type')
            if not is_exist:
                error_text = f'{sign_type} - Такого типа подписантов не существует'
                self.add_error('sign_type', ValidationError(error_text))
        return sign_type

    def get_number_unique(self):
        SertNumberObj = self.cleaned_data['number_unique']
        if not SertNumberObj:
            new_number = SertNumberForm({'id': '', 'number': '', 'year': '',})
            new_number.save()
            SertNumberObj = SertNumber.objects.get(pk=new_number.cleaned_data['id'])
        else:
            is_exist = Inspector.is_unique_exist_in_model(SertNumberObj.id, SertNumber)
            if not is_exist:
                new_number = SertNumberForm({'id': '', 'number': '', 'year': '',})
                new_number.save()
                SertNumberObj = SertNumber.objects.get(pk=new_number.cleaned_data['id'])
        self.cleaned_data['number_unique'] = SertNumberObj

    def clean(self):
        if self.errors:
            raise ValidationError('Ошибка в данных')

        id = self.cleaned_data['id']
        KernelObj = self.cleaned_data['number_spg']
        sert_type = self.cleaned_data['sert_type']

        def inspection_id(id):
            is_exist = Inspector.is_unique_exist_in_model(id, self._meta.model)
            if is_exist:
                error_text = f'{id} - Такой сертификат уже существует'
                raise ValidationError(error_text)

        if not id:
            id = f'{KernelObj.number_spg}-{sert_type}'
            inspection_id(id)
        else:
            if id != f'{KernelObj.number_spg}-{sert_type}':
                inspection_id(id)

        self.cleaned_data['id'] = id

        if not self.errors:
            self.get_number_unique()
        super().clean()

    class Meta:
        model = Sert
        fields = [
            'id',
            'is_print',
            'number_spg',
            'sert_type',
            'number_unique',
            'date',
            'galvan_date',
            'conclusion_type',
            'is_drag_met',
            'guarantee_type',
            'sign_type',
        ]
        field_classes = {
            'date': MyDateField,
            'galvan_date': MyDateField,
        }


class SertFormUpdate(SertForm):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    class Meta:
        model = Sert
        fields = [
            'id',
            'number_spg',
            'sert_type',
            'is_print',
            'number_unique',
            'date',
            'galvan_date',
            'conclusion_type',
            'is_drag_met',
            'guarantee_type',
            'sign_type',
        ]
        widgets = {
            'id': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'number_spg': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'sert_type': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'is_print': forms.CheckboxInput(attrs={
                'class': 'form-control',
            }),
            'is_drag_met': forms.CheckboxInput(attrs={
                'class': 'form-control',
            }),
        }


class KernelForm(forms.ModelForm):

    def clean_is_atom(self):
        is_atom = self.cleaned_data['is_atom']
        if isinstance(is_atom, type(None)):
            is_atom = False
        return is_atom

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if not quantity:
            quantity = 1
        else:
            pass
        return quantity
        
    class Meta:
        model = Kernel
        fields = [
            'number_spg',
            'designation',
            'denomination',
            'quantity',
            'is_atom',
            'atom_contract',
        ]


class KernelFormUpdate(KernelForm):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    class Meta:
        model = Kernel
        fields = [
            'number_spg',
            'designation',
            'denomination',
            'quantity',
            'is_atom',
            'atom_contract',
        ]
        widgets = {
            'number_spg': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'designation': forms.Textarea(attrs={
                'style': 'height:100px; resize:vertical;',
            }),
            'denomination': forms.Textarea(attrs={
                'style': 'height:100px; resize:vertical;',
            }),
            'is_atom': forms.CheckboxInput(attrs={
                'class': 'form-control',
            }),
            'atom_contract': forms.Textarea(attrs={
                'style': 'height:100px; resize:vertical;',
            }),
        }


class MyCharField(forms.ChoiceField):
    def to_python(self, value):
        if isinstance(value, type('')):
            value = ITEM_UNITS['INT']
        print('=====', value)
        if value in self.empty_values:
            return ITEM_UNITS['INT']
        return str(value)


class MyDecimalField(forms.DecimalField):
    def to_python(self, value):
        if isinstance(value, type(None)):
            value = Decimal(1.0)
        else:
            try:
                value = Decimal(value)
            except InvalidOperation:
                value = Decimal(1.0)
        return value


class AttachmentForm(forms.ModelForm):

    def clean_number_spg(self):
        KernelObj  = self.cleaned_data['number_spg']
        if not KernelObj:
            error_text = 'Номер СПГ не указан'
            self.add_error('number_spg', ValidationError(error_text))
        else:
            is_exist = Inspector.is_exist_in_model(KernelObj.number_spg, Kernel, 'number_spg')
            if not is_exist:
                error_text = f'{KernelObj.number_spg} - Записи с таким номером СПГ нет в Kernel'
                self.add_error('number_spg', ValidationError(error_text))
        return KernelObj

    def clean_number_unique(self): # не такой
        SertNumberObj = self.cleaned_data['number_unique']
        if not SertNumberObj:
            pass
        else:
            is_exist = Inspector.is_exist_in_model(SertNumberObj.id, SertNumber, 'id')
            if not is_exist:
                error_text = f'{SertNumberObj.id} - Записи с таким номером сертификата нет в SertNumber'
                self.add_error('number_unique', ValidationError(error_text))
        return SertNumberObj

    def clean_sert_type(self):
        sert_type = self.cleaned_data['sert_type']
        if not sert_type:
            sert_type = METHODS_LIST['РЕМКОМПЛЕКТ']
        else:
            is_exist = Inspector.is_exist_in_dict(sert_type, METHODS_LIST)
            if not is_exist:
                error_text = f'{sert_type} - Такой тип сертификата не предусмотрен'
                self.add_error('sert_type', ValidationError(error_text))
        return sert_type

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if not quantity:
            quantity = Decimal(1.0)
        else:
            r_quantity, is_good = Inspector.try_decimalization(quantity)
            if not is_good:
                error_text = f'{quantity} - Недопустимое значение'
                self.add_error('quantity', ValidationError(error_text))
                quantity = Decimal(1)
            else:
                quantity = r_quantity
        return quantity

    def clean_item_units(self):
        item_units = self.cleaned_data['item_units']
        if not item_units:
            item_units = ITEM_UNITS['INT']
        else:
            is_exist = Inspector.is_exist_in_dict(item_units, ITEM_UNITS)
            if not is_exist:
                error_text = f'{item_units} - Такой тип единиц измерения не предусмотрен'
                self.add_error('item_units', ValidationError(error_text))
        return item_units

    def clean_n_index(self):
        n_index = self.cleaned_data['n_index']
        if not n_index:
            pass
        else:
            r_n_index, is_good = Inspector.try_integeralization(n_index)
            if not is_good:
                error_text = f'{n_index} - Недопустимое значение'
                self.add_error('n_index', ValidationError(error_text))
                n_index = 0
            else:
                n_index = r_n_index
        return n_index

    # 'a_index', 'b_index',
    # 'a1_index', 'b1_index',
    # 'a2_index', 'b2_index',
    # 'is_one', 'is_two', 'is_three', 'is_four',
    #
    # 'melt_number', 'material_id', 'melt_year', 'melt_passport',

    def clean_is_cast(self):
        is_cast = self.cleaned_data['is_cast']
        melt_number = self.cleaned_data['melt_number']
        material_id = self.cleaned_data['material_id']
        melt_year = self.cleaned_data['melt_year']
        melt_passport = self.cleaned_data['melt_passport']
        if melt_number or material_id or melt_year or melt_passport:
            is_cast = True
        else:
            is_cast = False
        return is_cast

    def clean_is_by_gost_material_number(self):
        is_by_gost_material_number = self.cleaned_data['is_by_gost_material_number']
        if isinstance(is_by_gost_material_number, type(None)):
            is_by_gost_material_number = True
        return is_by_gost_material_number

    # 'galvan_material', 'galvan_units',

    def clean(self):
        if self.errors:
            raise ValidationError('Ошибка в данных')

        # is_cast = self.cleaned_data['is_cast']
        melt_number = self.cleaned_data['melt_number']
        material_id = self.cleaned_data['material_id']
        melt_year = self.cleaned_data['melt_year']
        melt_passport = self.cleaned_data['melt_passport']
        if melt_number or material_id or melt_year or melt_passport:
            is_cast = True
        else:
            is_cast = False
        self.cleaned_data['is_cast'] = is_cast

        # is_cast = self.cleaned_data['is_cast']
        if is_cast:
            melt_number = self.cleaned_data['melt_number']
            material_id = self.cleaned_data['material_id']
            melt_year = self.cleaned_data['melt_year']
            melt_passport = self.cleaned_data['melt_passport']
            melt_id = f'{melt_number}-{material_id}-{melt_year}-{melt_passport}'
            is_exist = Inspector.is_exist_in_model(melt_id, Melt, 'melt_id')
            if not is_exist:
                error_text = f'{melt_id} - Такой плавки не зарегистрировано'
                raise ValidationError(error_text)

            designation = self.cleaned_data['designation']
            if not designation:
                self.cleaned_data['designation'] = 'плавка'

        # автозаполнение 'is_one', 'is_two', 'is_three', 'is_four',
        number_spg = self.cleaned_data['number_spg']
        a_index = self.cleaned_data['a_index']
        b_index = self.cleaned_data['b_index']
        a1_index = self.cleaned_data['a1_index']
        b1_index = self.cleaned_data['b1_index']
        a2_index = self.cleaned_data['a2_index']
        b2_index = self.cleaned_data['b2_index']

        # is_one
        first1 = bool(
            (not b_index) and (
                not a1_index) and (
                not b1_index) and (
                not a2_index) and (
                not b2_index))
        second1 = bool(number_spg or (number_spg and a_index))
        if not (first1 and second1):
            is_one = False
        else:
            is_one = True

        # is_two
        first2 = bool(
            (not a_index) and (
                not b1_index) and (
                not a2_index) and (
                not b2_index))
        second2 = bool(b_index or (b_index and a1_index))
        if not (first2 and second2):
            is_two = False
        else:
            is_two = True

        # is_three
        first3 = bool(
            (not a_index) and (
                not b_index) and (
                not a1_index) and (
                not b2_index))
        second3 = bool(b1_index or (b1_index and a2_index))
        if not (first3 and second3):
            is_three = False
        else:
            is_three = True

        # is_four
        first4 = bool(
            (not a_index) and (
                not b_index) and (
                not a1_index) and (
                not b1_index) and (
                not a2_index))
        second4 = bool(b2_index)
        if not (first4 and second4):
            is_four = False
        else:
            is_four = True

        self.cleaned_data['is_one'] = is_one
        self.cleaned_data['is_two'] = is_two
        self.cleaned_data['is_three'] = is_three
        self.cleaned_data['is_four'] = is_four
        super().clean()

    class Meta:
        model = Attachment
        fields = [
            'id',
            'number_spg',
            'number_unique',
            'sert_type',

            'designation',
            'denomination',
            'quantity',
            'item_units',

            'n_index',
            'a_index',
            'b_index',
            'a1_index',
            'b1_index',
            'a2_index',
            'b2_index',
            'is_one',
            'is_two',
            'is_three',
            'is_four',

            'melt_number',
            'material_id',
            'melt_year',
            'melt_passport',
            'is_cast',

            'is_by_gost_material_number',
            'galvan_material',
            'galvan_units',
        ]
        # field_classes = {
        #     'item_units': MyDecimalField,
        #     'quantity': MyDecimalField,
        # }


class AttachmentFormForAdmin(AttachmentForm):
    # def __init__(self, *args, **kargs):
    #     super().__init__(*args, **kargs)

    class Meta:
        model = Attachment
        fields = [
            'id',
            'number_spg',
            'number_unique',
            'sert_type',

            'designation',
            'denomination',
            'quantity',
            'item_units',

            'n_index',
            'a_index',
            'b_index',
            'a1_index',
            'b1_index',
            'a2_index',
            'b2_index',
            'is_one',
            'is_two',
            'is_three',
            'is_four',

            'melt_number',
            'material_id',
            'melt_year',
            'melt_passport',
            'is_cast',

            'is_by_gost_material_number',
            'galvan_material',
            'galvan_units',
        ]


class AttachmentFormUpdate(AttachmentForm):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    class Meta:
        model = Attachment
        fields = [
            'number_spg',
            'number_unique',
            'sert_type',

            'designation',
            'denomination',
            'quantity',
            'item_units',

            'n_index',
            'a_index',
            'b_index',
            'a1_index',
            'b1_index',
            'a2_index',
            'b2_index',
            'is_one',
            'is_two',
            'is_three',
            'is_four',

            'melt_number',
            'material_id',
            'melt_year',
            'melt_passport',
            'is_cast',

            'is_by_gost_material_number',
            'galvan_material',
            'galvan_units',
        ]
        widgets = {
            'number_spg': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'number_unique': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'sert_type': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'designation': forms.Textarea(attrs={
                'style': 'height:100px; resize:vertical;',
            }),
            'denomination': forms.Textarea(attrs={
                'style': 'height:100px; resize:vertical;',
            }),
            'is_one': forms.CheckboxInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'is_two': forms.CheckboxInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'is_three': forms.CheckboxInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'is_four': forms.CheckboxInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'is_cast': forms.CheckboxInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'is_by_gost_material_number': forms.CheckboxInput(attrs={
                'class': 'form-control',
            }),
        }



class MeltForm(forms.ModelForm):

    def clean_by_gost_number(self):
        by_gost_number = self.cleaned_data['by_gost_number']
        if not by_gost_number:
            by_gost_number = random.randint(1, 20)
        return by_gost_number

    def clean(self):
        if self.errors:
            raise ValidationError('Ошибка в данных')

        melt_id = self.cleaned_data['melt_id']

        def get_melt_id():
            melt_number = self.cleaned_data['melt_number']
            material_id = self.cleaned_data['material_id']
            melt_year = self.cleaned_data['melt_year']
            melt_passport = self.cleaned_data['melt_passport']
            melt_id = f'{melt_number}-{material_id}-{melt_year}-{melt_passport}'
            return melt_id

        def inspection_id(id):
            is_exist = Inspector.is_unique_exist_in_model(id, self._meta.model)
            if is_exist:
                error_text = f'{id} - Такая отливка уже существует'
                raise ValidationError(error_text)

        if not melt_id:
            melt_id = get_melt_id()
            inspection_id(melt_id)
        else:
            if melt_id != get_melt_id():
                inspection_id(melt_id)

        self.cleaned_data['melt_id'] = melt_id
        # print('===после===', self.cleaned_data)
        super().clean()

    class Meta:
        model = Melt
        fields = [
            'melt_id',
            'melt_number',
            'material_id',
            'melt_year',
            'melt_passport',
            'by_gost_number',

            'carboneum',
            'manganum',
            'silicium',
            'sulfur',
            'phosphorus',
            'chromium',
            'molybdaenum',
            'niccolum',
            'niobium',
            'titanium',
            'cuprum',
            'magnesium',
            'ferrum',

            'tensile_strength',
            'yield_strength',
            'relative_extension',
            'relative_narrowing',
            'impact_strength',
            'impact_strength_60KCU',
            'impact_strength_60KCV',
            'hardness',
            'mkk',
        ]
        # field_classes = {
        #     'by_gost_number': MyIntegerField,
        # }


class MeltFormUpdate(MeltForm):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    class Meta:
        model = Melt
        fields = [
            'melt_id',
            'melt_number',
            'material_id',
            'melt_year',
            'melt_passport',
            'by_gost_number',

            'carboneum',
            'manganum',
            'silicium',
            'sulfur',
            'phosphorus',
            'chromium',
            'molybdaenum',
            'niccolum',
            'niobium',
            'titanium',
            'cuprum',
            'magnesium',
            'ferrum',

            'tensile_strength',
            'yield_strength',
            'relative_extension',
            'relative_narrowing',
            'impact_strength',
            'impact_strength_60KCU',
            'impact_strength_60KCV',
            'hardness',
            'mkk',
        ]
        widgets = {
            'melt_id': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'melt_number': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'material_id': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'melt_year': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
            'melt_passport': forms.TextInput(attrs={
                'readonly': 'readonly',
                'style': 'color: #696969; background-color: #A9A9A9;',
            }),
        }
