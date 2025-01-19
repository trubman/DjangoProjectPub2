from django.urls import path
from django.views.decorators.cache import cache_page
from sert.views import (
    HomeSert, SearchHomeSert,
    is_print_switch,
    get_loadform,
    OneSert,
    PrintSert,
    FileLoadFormView,
    OneSertUpdateView,
    OneKernelUpdateView,
    OneAttachmentUpdateView,
    OneMeltUpdateView,
    InstructionView,
    get_examples,
    # MyView
)

urlpatterns = [
    path('', cache_page(3)(HomeSert.as_view()), name='homesert'),
    path('searchsert/', cache_page(30)(SearchHomeSert.as_view()), name='searchsert'),
    path('sert/<str:pk>/', cache_page(30)(OneSert.as_view()), name='onesert'),
    path('instruction/', cache_page(60)(InstructionView.as_view()), name='instruction'),
    path('instruction/getexamples/', get_examples, name='getexamples'),

    path('update/sert/<str:pk>/', OneSertUpdateView.as_view(), name='sertupdate'),
    path('update/kernel/<str:pk>/', OneKernelUpdateView.as_view(), name='kernelupdate'),
    path('update/attachment/<int:pk>/', OneAttachmentUpdateView.as_view(), name='attachmentupdate'),
    path('update/melt/<str:pk>/', OneMeltUpdateView.as_view(), name='meltupdate'),

    path('printstatus/<str:id>/', is_print_switch, name='is_print_switch'),
    path('print/', cache_page(5)(PrintSert.as_view()), name='printsert'),
    path('loadfile/', cache_page(5)(FileLoadFormView.as_view()), name='loadfile'),
    path('getform/', get_loadform, name='getform'),
]