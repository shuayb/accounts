from django.conf import settings
from django.db.models import Sum
from django.urls import reverse_lazy

from accountancy.forms import BaseVoidTransactionForm
from accountancy.views import (BaseViewTransaction, BaseVoidTransaction,
                               CreateCashBookTransaction,
                               DeleteCashBookTransMixin,
                               EditCashBookTransaction, CashBookAndNominalTransList,
                               NominalViewTransactionMixin)
from cashbook.forms import CashBookTransactionSearchForm
from nominals.forms import NominalForm
from nominals.models import Nominal, NominalTransaction
from vat.forms import VatForm

from .forms import CashBookHeaderForm, CashBookLineForm, enter_lines
from .models import CashBookHeader, CashBookLine, CashBookTransaction


class CreateTransaction(CreateCashBookTransaction):
    header = {
        "model": CashBookHeader,
        "form": CashBookHeaderForm,
        "prefix": "header",
        "initial": {"total": 0},
    }
    line = {
        "model": CashBookLine,
        "formset": enter_lines,
        "prefix": "line",
    }
    create_on_the_fly = {
        "nominal_form": NominalForm(action=reverse_lazy("nominals:nominal_create"), prefix="nominal"),
        "vat_form": VatForm(action=reverse_lazy("vat:vat_create"), prefix="vat"),
    }
    template_name = "cashbook/create.html"
    success_url = reverse_lazy("cashbook:transaction_enquiry")
    nominal_model = Nominal
    nominal_transaction_model = NominalTransaction
    cash_book_transaction_model = CashBookTransaction
    module = "CB"
    default_type = "cp"


class EditTransaction(EditCashBookTransaction):
    header = {
        "model": CashBookHeader,
        "form": CashBookHeaderForm,
        "prefix": "header",
        "initial": {"total": 0},
    }
    line = {
        "model": CashBookLine,
        "formset": enter_lines,
        "prefix": "line",
    }
    create_on_the_fly = {
        "nominal_form": NominalForm(action=reverse_lazy("nominals:nominal_create"), prefix="nominal"),
        "vat_form": VatForm(action=reverse_lazy("vat:vat_create"), prefix="vat"),
    }
    template_name = "cashbook/edit.html"
    success_url = reverse_lazy("cashbook:transaction_enquiry")
    nominal_model = Nominal
    nominal_transaction_model = NominalTransaction
    cash_book_transaction_model = CashBookTransaction
    module = "CB"


class ViewTransaction(NominalViewTransactionMixin, BaseViewTransaction):
    model = CashBookHeader
    line_model = CashBookLine
    nominal_transaction_model = NominalTransaction
    module = 'CB'
    void_form_action = reverse_lazy("cashbook:void")
    void_form = BaseVoidTransactionForm
    template_name = "cashbook/view.html"
    edit_view_name = "cashbook:edit"


class VoidTransaction(DeleteCashBookTransMixin, BaseVoidTransaction):
    header_model = CashBookHeader
    nominal_transaction_model = NominalTransaction
    form_prefix = "void"
    form = BaseVoidTransactionForm
    success_url = reverse_lazy("cashbook:transaction_enquiry")
    module = 'CB'
    cash_book_transaction_model = CashBookTransaction


class TransactionEnquiry(CashBookAndNominalTransList):
    model = CashBookHeader
    fields = [
        ("module", "Module"),
        ("header", "Internal Ref"),
        ("ref", "Ref"),
        ("cash_book__name", "Cash Book"),
        ("period", "Period"),
        ("date", "Date"),
        ("total", "Total"),
    ]
    form_field_to_searchable_model_field = {
        "reference": "ref"
    }
    datetime_fields = ["created", ]
    datetime_format = '%d %b %Y'
    advanced_search_form_class = CashBookTransactionSearchForm
    template_name = "cashbook/transactions.html"
    row_identifier = "header"

    def get_transaction_url(self, **kwargs):
        row = kwargs.pop("row")
        module = row.get("module")
        header = row.get("header")
        modules = settings.ACCOUNTANCY_MODULES
        module_name = modules[module]
        return reverse_lazy(module_name + ":view", kwargs={"pk": header})

    def apply_advanced_search(self, cleaned_data):
        queryset = super().apply_advanced_search(cleaned_data)
        if cashbook := cleaned_data.get("cashbook"):
            queryset = queryset.filter(cashbook=cashbook)
        return queryset

    def get_queryset(self):
        return (
            CashBookTransaction.objects
            .select_related('cash_book__name')
            .all()
            .values(
                *[field[0] for field in self.fields[:-1]]
            )
            .annotate(total=Sum("value"))
            .order_by(*self.order_by())
        )
