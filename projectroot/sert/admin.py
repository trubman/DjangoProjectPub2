from django.contrib import admin
from sert.models import (
    SertNumber,
    Sert,
    Kernel,
    Attachment,
    Melt,
    Signatories,
    Conclusion,
    Guarantee,
)
from sert.forms import (
    SertNumberForm,
    SertForm,
    KernelForm,
    AttachmentForm,
    MeltForm,
)

class SertNumberAdmin(admin.ModelAdmin):
    form = SertNumberForm
    fields = (
        'id',
        'number',
        'year',
    )
    list_display = (
        'id',
        'number',
        'year',
    )

class SertAdmin(admin.ModelAdmin):
    form = SertForm
    fields = (
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
    )
    list_display = (
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
    )
    search_fields = (
        'id',
        'is_print',
        # 'number_spg',
        'sert_type',
        # 'number_unique',
        'date',
        'galvan_date',
        # 'conclusion_type',
        'is_drag_met',
        'guarantee_type',
        'sign_type',
    )
    list_filter = (
        'is_print',
        'sert_type',
        'is_drag_met',
    )
    list_editable = (
        'is_print',
        'is_drag_met',
    )
    # readonly_fields = ()


class KernelAdmin(admin.ModelAdmin):
    form = KernelForm
    fields = (
        'number_spg',
        'designation',
        'denomination',
        'quantity',
        'is_atom',
        'atom_contract',
    )
    list_display = (
        'number_spg',
        'designation',
        'denomination',
        'quantity',
        'is_atom',
        'atom_contract',
    )
    search_fields = (
        'number_spg',
        'designation',
        'denomination',
        'atom_contract',
    )
    list_filter = (
        'is_atom',
    )
    list_editable = (
        'is_atom',
    )
    # readonly_fields = ()


class AttachmentAdmin(admin.ModelAdmin):
    form = AttachmentForm
    fields = (
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
    )
    list_display = (
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
    )
    search_fields = (
        'id',
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

        'melt_number',
        'material_id',
        'melt_year',
        'melt_passport',

        'galvan_material',
        'galvan_units',
    )
    list_filter = (
        'sert_type',
        'is_cast',
        'is_by_gost_material_number',
    )
    list_editable = (
        'is_by_gost_material_number',
    )
    readonly_fields = (
        'id',
        # 'is_one',
        # 'is_two',
        # 'is_three',
        # 'is_four',
        # 'is_cast',
    )


class MeltAdmin(admin.ModelAdmin):
    form = MeltForm
    fields = (
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
    )
    list_display = (
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
    )
    search_fields = (
        'melt_id',
        'melt_number',
        'material_id',
        'melt_year',
        'melt_passport',
    )
    list_filter = (
        'material_id',
        'melt_year',
    )
    # list_editable = ()
    # readonly_fields = ()


class SignatoriesAdmin(admin.ModelAdmin):
    list_display = (
        'sign_type',
        'sign_person',
        'sign_job_title',
    )
    class Meta:
        model = Signatories
        fields = (
            'sign_type',
            'sign_person',
            'sign_job_title',
        )


class ConclusionAdmin(admin.ModelAdmin):
    list_display = (
        'conclusion_type',
        'conclusion_text',
    )
    class Meta:
        model = Conclusion
        fields = (
            'conclusion_type',
            'conclusion_text',
        )


class GuaranteeAdmin(admin.ModelAdmin):
    list_display = (
        'guarantee_type',
        'guarantee_text',
    )
    class Meta:
        model = Guarantee
        fields = (
            'guarantee_type',
            'guarantee_text',
        )

admin.site.register(SertNumber, SertNumberAdmin)
admin.site.register(Sert, SertAdmin)
admin.site.register(Kernel, KernelAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Melt, MeltAdmin)
admin.site.register(Signatories, SignatoriesAdmin)
admin.site.register(Conclusion, ConclusionAdmin)
admin.site.register(Guarantee, GuaranteeAdmin)

admin.site.site_title = 'Страница администратора'
admin.site.site_header = 'Страница администратора'