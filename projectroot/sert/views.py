from collections import namedtuple

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from openpyxl.workbook import Workbook

from sert.forms import BaseForm
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from sert.createdocx import SertMaker
from sert.createdocx2 import GroupManager

from sert.importxlsx import ImportManager, Importer, Converter, Loader
from sert.models import Sert, Attachment, Melt, Kernel
from sert.forms import SertForm, SertFormUpdate, KernelFormUpdate, AttachmentFormUpdate, MeltFormUpdate


from datetime import datetime
from django.contrib import messages
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, FileResponse
from io import BytesIO
import zipfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class InstructionView(LoginRequiredMixin, TemplateView):
    template_name = "sert/instruction.html"


@login_required
def get_examples(request):
    with open("static/instruction/serts_examples.zip", 'rb') as file:
        response = HttpResponse(content=file,
                            content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="serts_examples.zip"'
    return response


class HomeSert(LoginRequiredMixin, ListView):
    model = Sert
    context_object_name = 'serts'
    template_name = 'sert/homesert_list.html'
    paginate_by = 14


class SearchHomeSert(LoginRequiredMixin, ListView):
    model = Sert
    context_object_name = 'serts'
    template_name = 'sert/search_homesert_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        searched = self.request.GET.get('searched')
        context['searched'] = searched
        return context

    def get_queryset(self):
        searched = self.request.GET.get('searched')
        lookup_data = (Q(number_spg=searched) |
                       Q(number_spg__number_spg__icontains=searched) |
                       Q(number_spg__designation__icontains=searched) |
                       Q(number_spg__denomination__icontains=searched) |
                       Q(number_spg__atom_contract__icontains=searched) |
                       Q(id__icontains=searched) |
                       Q(sert_type__icontains=searched) |
                       Q(number_unique=searched) |
                       Q(date__icontains=searched) |
                       Q(galvan_date__icontains=searched) |
                       Q(conclusion_type=searched) |
                       Q(conclusion_type__conclusion_text__icontains=searched) |
                       Q(guarantee_type__icontains=searched) |
                       Q(sign_type__icontains=searched)
                       )
        return Sert.objects.filter(lookup_data)


class OneSert(LoginRequiredMixin, DetailView):
    model = Sert
    context_object_name = 'sert'
    template_name = 'sert/onesert.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.request.resolver_match.kwargs['pk']
        sert = Sert.objects.get(pk=pk)
        test = Attachment.objects.filter(number_unique=sert.number_unique)
        if not test:
            pre_attachs = (Attachment.objects.filter(number_spg=sert.number_spg)
                    .filter(sert_type=sert.sert_type))
        else:
            pre_attachs = (Attachment.objects.filter(number_unique=sert.number_unique)
                    .filter(number_spg=sert.number_spg)
                    .filter(sert_type=sert.sert_type))
        attachs = []
        melts = []
        melts_id_list = []
        if pre_attachs:
            for a in pre_attachs:
                if not a.is_cast:
                    attachs.append(a)
                else:
                    melt_id = f'{a.melt_number}-{a.material_id}-{a.melt_year}-{a.melt_passport}'
                    if melt_id not in melts_id_list:
                        melts_id_list.append(melt_id)
        if melts_id_list:
            for m in melts_id_list:
                melt = list(Melt.objects.filter(melt_id=m))
                melts += melt
        context['attachs'] = pre_attachs
        context['melts'] = melts
        return context


class OneSertUpdateView(LoginRequiredMixin, UpdateView):
    model = Sert
    form_class = SertFormUpdate
    template_name = 'sert/updateform.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_title'] = 'СЕРТИФИКАТ'
        return context


class OneKernelUpdateView(LoginRequiredMixin, UpdateView):
    model = Kernel
    form_class = KernelFormUpdate
    template_name = 'sert/updateform.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_title'] = 'ПРОДУКТ'
        return context


class OneAttachmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Attachment
    form_class = AttachmentFormUpdate
    template_name = 'sert/updateform.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_title'] = 'ВЛОЖЕНИЕ'
        return context


class OneMeltUpdateView(LoginRequiredMixin, UpdateView):
    model = Melt
    form_class = MeltFormUpdate
    template_name = 'sert/updateform.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_title'] = 'ПЛАВКУ'
        return context


class PrintSert(LoginRequiredMixin, ListView):
    model = Sert
    context_object_name = 'serts'
    template_name = 'sert/forprint_list.html'

    def get_queryset(self):
        return Sert.objects.filter(is_print=True)

    def post(self, request, *args, **kwargs):
        GM = GroupManager()
        docx_list = GM.get_docx_list()
        if not docx_list:
            errors = GM.get_error()
            for level, text in errors:
                messages.add_message(self.request, level, text,)
            return render(request, self.template_name, )
        FM = FileMaker(docx_list)
        export_file = FM.get_file()
        response = HttpResponse(content=export_file.content, content_type=export_file.content_type)
        response['Content-Disposition'] = f'attachment; filename="{export_file.filename}"'
        return response


@login_required
def is_print_switch(request, id):
    try:
        sert = Sert.objects.get(id=id)
        if sert.is_print:
            sert.is_print = False
        else:
            sert.is_print = True
        sert.save()
    except ObjectDoesNotExist:
        pass
    return redirect('homesert')


@login_required
def get_loadform(request):
    with open("static/loadform/blankloader.xlsx", 'rb') as file:
        response = HttpResponse(content=file,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="blankloader.xlsx"'
    return response


class FileMaker:
    def __init__(self, input_docx_list):
        self.input_docx_list = input_docx_list
        self.result_file_nt = namedtuple('result_file', [
            'content', 'content_type', 'filename',
        ])
        self.result_file = None

        self.check_quantity()

    def get_file(self):
        return self.result_file

    def check_quantity(self):
        if len(self.input_docx_list) == 0:
            pass
        elif len(self.input_docx_list) == 1:
            self.set_lonly_file()
        elif len(self.input_docx_list) >= 2:
            self.set_group_file()

    @staticmethod
    def get_file_content(docx_nt):
        with BytesIO() as buffer:
            document = docx_nt.content
            document.save(buffer)
            content = buffer.getvalue()
            return content

    def set_lonly_file(self):
        docx_nt = self.input_docx_list[0]
        content = self.get_file_content(docx_nt)
        self.result_file = self.result_file_nt(
            content=content,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=f'{docx_nt.name}.{docx_nt.format}'
        )

    @staticmethod
    def get_file_read_content(docx_nt_content):
        with BytesIO() as buffer:
            docx_nt_content.save(buffer)
            buffer.seek(0)
            content = buffer.read()
            return content

    def set_group_file(self):
        with BytesIO() as mem_zip:
            docx_tuples_list = []
            nt = namedtuple('docx_tuple', ['filename', 'content', ])
            for docx_nt in self.input_docx_list:
                docx_tuples_list.append(nt(
                    filename=f'{docx_nt.name}.{docx_nt.format}',
                    content=self.get_file_read_content(docx_nt.content),
                ))

            with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                for docx_tuple in docx_tuples_list:  # итерирует кортеж
                    zf.writestr(docx_tuple.filename, docx_tuple.content)
            content = mem_zip.getvalue()

            pre_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.result_file = self.result_file_nt(
                content=content,
                content_type='application/zip',
                filename=f'{pre_name}_serts.zip'
            )


class FileLoadFormView(LoginRequiredMixin, FormView):
    template_name = 'sert/forloadfile.html'
    form_class = BaseForm
    success_url = reverse_lazy('loadfile')

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        file = self.request.FILES['file']
        IM = ImportManager()
        IM.set_file(file)
        for_messages_list = IM.get_errors() # (level, text,)
        if not for_messages_list:
            pass
        else:
            for level, text in for_messages_list:
                messages.add_message(self.request, level, text,)
        return super().form_valid(form)

