from datetime import date, datetime, timedelta

from accountancy.helpers import sort_multiple
from accountancy.testing.helpers import *
from cashbook.models import CashBook, CashBookTransaction
from controls.models import FinancialYear, Period
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import RequestFactory, TestCase
from django.utils import timezone
from nominals.models import Nominal, NominalTransaction
from vat.models import Vat

from ..helpers import (create_credit_note_with_lines,
                       create_credit_note_with_nom_entries,
                       create_invoice_with_lines,
                       create_invoice_with_nom_entries, create_invoices,
                       create_lines, create_payment_with_nom_entries,
                       create_payments, create_refund_with_nom_entries)
from ..models import PurchaseHeader, PurchaseLine, PurchaseMatching, Supplier

HEADER_FORM_PREFIX = "header"
LINE_FORM_PREFIX = "line"
match_form_prefix = "match"
PL_MODULE = "PL"
DATE_INPUT_FORMAT = '%d-%m-%Y'
MODEL_DATE_INPUT_FORMAT = '%Y-%m-%d'

class ViewInvoice(TestCase):

    """
    Based on same tests as CreateInvoiceNominalEntries
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username="dummy", password="dummy")
        cls.factory = RequestFactory()
        cls.supplier = Supplier.objects.create(name="test_supplier")
        cls.ref = "test matching"
        cls.date = datetime.now().strftime(DATE_INPUT_FORMAT)
        cls.due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(DATE_INPUT_FORMAT)
        cls.model_date = datetime.now().strftime(MODEL_DATE_INPUT_FORMAT)
        cls.model_due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(MODEL_DATE_INPUT_FORMAT)
        fy = FinancialYear.objects.create(financial_year=2020)
        cls.period = Period.objects.create(fy=fy, period="01", fy_and_period="202001", month_start=date(2020,1,31))

        cls.description = "a line description"

        # ASSETS
        assets = Nominal.objects.create(name="Assets")
        current_assets = Nominal.objects.create(
            parent=assets, name="Current Assets")
        cls.nominal = Nominal.objects.create(
            parent=current_assets, name="Bank Account")

        # LIABILITIES
        liabilities = Nominal.objects.create(name="Liabilities")
        current_liabilities = Nominal.objects.create(
            parent=liabilities, name="Current Liabilities")
        cls.purchase_control = Nominal.objects.create(
            parent=current_liabilities, name="Purchase Ledger Control")
        cls.vat_nominal = Nominal.objects.create(
            parent=current_liabilities, name="Vat")

        cls.vat_code = Vat.objects.create(
            code="1", name="standard rate", rate=20)

        cls.url = reverse("purchases:create")

    def test(self):
        self.client.force_login(self.user)

        header = create_invoice_with_nom_entries(
            {
                "type": "pi",
                "supplier": self.supplier,
				"period": self.period,
                "ref": self.ref,
                "date": self.model_date,
                "due_date": self.model_due_date,
                "total": 2400,
                "paid": 0,
                "due": 2400
            },
            [
                {
                    'description': self.description,
                    'goods': 100,
                    'nominal': self.nominal,
                    'vat_code': self.vat_code,
                    'vat': 20
                }
            ] * 20,
            self.vat_nominal,
            self.purchase_control
        )

        headers = PurchaseHeader.objects.all()
        header = headers[0]

        response = self.client.get(
            reverse("purchases:view", kwargs={"pk": header.pk}))
        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["header"],
            header
        )


class ViewBroughtForwardInvoice(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username="dummy", password="dummy")
        cls.factory = RequestFactory()
        cls.supplier = Supplier.objects.create(name="test_supplier")
        cls.ref = "test matching"
        cls.date = datetime.now().strftime(DATE_INPUT_FORMAT)
        cls.due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(DATE_INPUT_FORMAT)
        cls.model_date = datetime.now().strftime(MODEL_DATE_INPUT_FORMAT)
        cls.model_due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(MODEL_DATE_INPUT_FORMAT)
        fy = FinancialYear.objects.create(financial_year=2020)
        cls.period = Period.objects.create(fy=fy, period="01", fy_and_period="202001", month_start=date(2020,1,31))

        
        cls.description = "a line description"

        cls.vat_code = Vat.objects.create(code="1", name="standard rate", rate=20)

    def test(self):
        self.client.force_login(self.user)

        header, lines = create_invoice_with_lines(
            {
                "type": "pbi",
                "supplier": self.supplier,
				"period": self.period,
                "ref": self.ref,
                "date": self.model_date,
                "due_date": self.model_due_date,
                "total": 2400,
                "paid": 0,
                "due": 2400
            },
            [
                {
                    
                    'description': self.description,
                    'goods': 100,
                    'vat': 20
                }
            ] * 20,
        )


        headers = PurchaseHeader.objects.all()
        header = headers[0]

        response = self.client.get(
            reverse("purchases:view", kwargs={"pk": header.pk}))
        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["header"],
            header
        )


class ViewCreditNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username="dummy", password="dummy")
        cls.factory = RequestFactory()
        cls.supplier = Supplier.objects.create(name="test_supplier")
        cls.ref = "test matching"
        cls.date = datetime.now().strftime(DATE_INPUT_FORMAT)
        cls.due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(DATE_INPUT_FORMAT)
        cls.model_date = datetime.now().strftime(MODEL_DATE_INPUT_FORMAT)
        cls.model_due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(MODEL_DATE_INPUT_FORMAT)
        fy = FinancialYear.objects.create(financial_year=2020)
        cls.period = Period.objects.create(fy=fy, period="01", fy_and_period="202001", month_start=date(2020,1,31))

        
        cls.description = "a line description"

        # ASSETS
        assets = Nominal.objects.create(name="Assets")
        current_assets = Nominal.objects.create(parent=assets, name="Current Assets")
        cls.nominal = Nominal.objects.create(parent=current_assets, name="Bank Account")

        # LIABILITIES
        liabilities = Nominal.objects.create(name="Liabilities")
        current_liabilities = Nominal.objects.create(parent=liabilities, name="Current Liabilities")
        cls.purchase_control = Nominal.objects.create(parent=current_liabilities, name="Purchase Ledger Control")
        cls.vat_nominal = Nominal.objects.create(parent=current_liabilities, name="Vat")


        cls.vat_code = Vat.objects.create(code="1", name="standard rate", rate=20)

        cls.url = reverse("purchases:create")

    def test(self):
        self.client.force_login(self.user)

        create_credit_note_with_nom_entries(
            {
                "type": "pc",
                "supplier": self.supplier,
				"period": self.period,
                "ref": self.ref,
                "date": self.model_date,
                "due_date": self.model_due_date,
                "total": 2400,
                "paid": 0,
                "due": 2400,
                "goods": 2000,
                "vat": 400
            },
            [
                {
                    
                    'description': self.description,
                    'goods': 100,
                    'nominal': self.nominal,
                    'vat_code': self.vat_code,
                    'vat': 20
                }
            ] * 20,
            self.vat_nominal,
            self.purchase_control
        )

        headers = PurchaseHeader.objects.all()
        header = headers[0]

        response = self.client.get(
            reverse("purchases:view", kwargs={"pk": header.pk}))
        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["header"],
            header
        )


class ViewBroughtForwardCreditNote(TestCase):

    """
    Based on same tests as EditCreditNoteNominalTransactions 
    except of course we always expect no nominal output
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username="dummy", password="dummy")
        cls.factory = RequestFactory()
        cls.supplier = Supplier.objects.create(name="test_supplier")
        cls.ref = "test matching"
        cls.date = datetime.now().strftime(DATE_INPUT_FORMAT)
        cls.due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(DATE_INPUT_FORMAT)
        cls.model_date = datetime.now().strftime(MODEL_DATE_INPUT_FORMAT)
        cls.model_due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(MODEL_DATE_INPUT_FORMAT)
        fy = FinancialYear.objects.create(financial_year=2020)
        cls.period = Period.objects.create(fy=fy, period="01", fy_and_period="202001", month_start=date(2020,1,31))

        
        cls.description = "a line description"

        cls.vat_code = Vat.objects.create(code="1", name="standard rate", rate=20)

    def test(self):
        self.client.force_login(self.user)

        # function will still work for credit notes
        header, lines = create_credit_note_with_lines(
            {
                "type": "pbc",
                "supplier": self.supplier,
				"period": self.period,
                "ref": self.ref,
                "date": self.model_date,
                "due_date": self.model_due_date,
                "total": 2400,
                "paid": 0,
                "due": 2400
            },
            [
                {
                    
                    'description': self.description,
                    'goods': 100,
                    'vat': 20
                }
            ] * 20,
        )


        headers = PurchaseHeader.objects.all()
        header = headers[0]

        response = self.client.get(
            reverse("purchases:view", kwargs={"pk": header.pk}))
        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["header"],
            header
        )


class ViewPayment(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username="dummy", password="dummy")
        cls.factory = RequestFactory()
        cls.supplier = Supplier.objects.create(name="test_supplier")
        cls.ref = "test matching"
        cls.date = datetime.now().strftime(DATE_INPUT_FORMAT)
        cls.due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(DATE_INPUT_FORMAT)
        cls.model_date = datetime.now().strftime(MODEL_DATE_INPUT_FORMAT)
        cls.model_due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(MODEL_DATE_INPUT_FORMAT)
        fy = FinancialYear.objects.create(financial_year=2020)
        cls.period = Period.objects.create(fy=fy, period="01", fy_and_period="202001", month_start=date(2020,1,31))

        
        cls.description = "a line description"

        # ASSETS
        assets = Nominal.objects.create(name="Assets")
        current_assets = Nominal.objects.create(parent=assets, name="Current Assets")
        cls.nominal = Nominal.objects.create(parent=current_assets, name="Bank Account")

        # LIABILITIES
        liabilities = Nominal.objects.create(name="Liabilities")
        current_liabilities = Nominal.objects.create(parent=liabilities, name="Current Liabilities")
        cls.purchase_control = Nominal.objects.create(parent=current_liabilities, name="Purchase Ledger Control")
        cls.vat_nominal = Nominal.objects.create(parent=current_liabilities, name="Vat")

        cls.cash_book = CashBook.objects.create(name="Cash Book", nominal=cls.nominal) # Bank Nominal

        cls.vat_code = Vat.objects.create(code="1", name="standard rate", rate=20)


    def test(self):
        self.client.force_login(self.user)

        create_payment_with_nom_entries(
            {
                "cash_book": self.cash_book,
                "type": "pp",
                "supplier": self.supplier,
				"period": self.period,
                "ref": self.ref,
                "date": self.model_date,
                "due_date": self.model_due_date,
                "total": 120,
                "due": 120,
                "paid": 0,
            },
            self.purchase_control,
            self.nominal
        )

        headers = PurchaseHeader.objects.all()
        header = headers[0]

        response = self.client.get(
            reverse("purchases:view", kwargs={"pk": header.pk}))
        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["header"],
            header
        )


class ViewBroughtForwardPayment(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username="dummy", password="dummy")
        cls.factory = RequestFactory()
        cls.supplier = Supplier.objects.create(name="test_supplier")
        cls.ref = "test matching"
        cls.date = datetime.now().strftime(DATE_INPUT_FORMAT)
        cls.due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(DATE_INPUT_FORMAT)
        cls.model_date = datetime.now().strftime(MODEL_DATE_INPUT_FORMAT)
        cls.model_due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(MODEL_DATE_INPUT_FORMAT)
        fy = FinancialYear.objects.create(financial_year=2020)
        cls.period = Period.objects.create(fy=fy, period="01", fy_and_period="202001", month_start=date(2020,1,31))

        
        cls.description = "a line description"

        # ASSETS
        assets = Nominal.objects.create(name="Assets")
        current_assets = Nominal.objects.create(parent=assets, name="Current Assets")
        cls.nominal = Nominal.objects.create(parent=current_assets, name="Bank Account")

        # LIABILITIES
        liabilities = Nominal.objects.create(name="Liabilities")
        current_liabilities = Nominal.objects.create(parent=liabilities, name="Current Liabilities")
        cls.purchase_control = Nominal.objects.create(parent=current_liabilities, name="Purchase Ledger Control")
        cls.vat_nominal = Nominal.objects.create(parent=current_liabilities, name="Vat")

        cls.vat_code = Vat.objects.create(code="1", name="standard rate", rate=20)

    def test(self):
        self.client.force_login(self.user)

        PurchaseHeader.objects.create(**{
            "type": "pbp",
            "supplier": self.supplier,
			"period": self.period,
            "ref": self.ref,
            "date": self.model_date,
            "due_date": self.model_due_date,
            "total": -120,
            "due": -120,
            "paid": 0,
            "goods": 0,
            "vat": 0,          
        })

        headers = PurchaseHeader.objects.all()
        header = headers[0]

        response = self.client.get(
            reverse("purchases:view", kwargs={"pk": header.pk}))
        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["header"],
            header
        )


class ViewRefund(TestCase):

    """
    Same tests as EditPaymentNominalEntries
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username="dummy", password="dummy")
        cls.factory = RequestFactory()
        cls.supplier = Supplier.objects.create(name="test_supplier")
        cls.ref = "test matching"
        cls.date = datetime.now().strftime(DATE_INPUT_FORMAT)
        cls.due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(DATE_INPUT_FORMAT)
        cls.model_date = datetime.now().strftime(MODEL_DATE_INPUT_FORMAT)
        cls.model_due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(MODEL_DATE_INPUT_FORMAT)
        fy = FinancialYear.objects.create(financial_year=2020)
        cls.period = Period.objects.create(fy=fy, period="01", fy_and_period="202001", month_start=date(2020,1,31))

        
        cls.description = "a line description"

        # ASSETS
        assets = Nominal.objects.create(name="Assets")
        current_assets = Nominal.objects.create(parent=assets, name="Current Assets")
        cls.nominal = Nominal.objects.create(parent=current_assets, name="Bank Account")

        # LIABILITIES
        liabilities = Nominal.objects.create(name="Liabilities")
        current_liabilities = Nominal.objects.create(parent=liabilities, name="Current Liabilities")
        cls.purchase_control = Nominal.objects.create(parent=current_liabilities, name="Purchase Ledger Control")
        cls.vat_nominal = Nominal.objects.create(parent=current_liabilities, name="Vat")

        cls.cash_book = CashBook.objects.create(name="Cash Book", nominal=cls.nominal) # Bank Nominal

        cls.vat_code = Vat.objects.create(code="1", name="standard rate", rate=20)

    def test(self):
        self.client.force_login(self.user)

        create_refund_with_nom_entries(
            {
                "cash_book": self.cash_book,
                "type": "pr",
                "supplier": self.supplier,
				"period": self.period,
                "ref": self.ref,
                "date": self.model_date,
                "due_date": self.model_due_date,
                "total": 120,
                "due": 120,
                "paid": 0,
            },
            self.purchase_control,
            self.nominal
        )

        headers = PurchaseHeader.objects.all()
        header = headers[0]

        response = self.client.get(
            reverse("purchases:view", kwargs={"pk": header.pk}))
        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["header"],
            header
        )


class ViewBroughtForwardRefund(TestCase):

    """
    Tests same as EditRefundNominalEntries.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username="dummy", password="dummy")
        cls.factory = RequestFactory()
        cls.supplier = Supplier.objects.create(name="test_supplier")
        cls.ref = "test matching"
        cls.date = datetime.now().strftime(DATE_INPUT_FORMAT)
        cls.due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(DATE_INPUT_FORMAT)
        cls.model_date = datetime.now().strftime(MODEL_DATE_INPUT_FORMAT)
        cls.model_due_date = (datetime.now() + timedelta(days=31)
                        ).strftime(MODEL_DATE_INPUT_FORMAT)
        fy = FinancialYear.objects.create(financial_year=2020)
        cls.period = Period.objects.create(fy=fy, period="01", fy_and_period="202001", month_start=date(2020,1,31))

        
        cls.description = "a line description"

        # ASSETS
        assets = Nominal.objects.create(name="Assets")
        current_assets = Nominal.objects.create(parent=assets, name="Current Assets")
        cls.nominal = Nominal.objects.create(parent=current_assets, name="Bank Account")

        # LIABILITIES
        liabilities = Nominal.objects.create(name="Liabilities")
        current_liabilities = Nominal.objects.create(parent=liabilities, name="Current Liabilities")
        cls.purchase_control = Nominal.objects.create(parent=current_liabilities, name="Purchase Ledger Control")
        cls.vat_nominal = Nominal.objects.create(parent=current_liabilities, name="Vat")

        cls.vat_code = Vat.objects.create(code="1", name="standard rate", rate=20)

        cls.url = reverse("purchases:create")

    def test(self):
        self.client.force_login(self.user)

        PurchaseHeader.objects.create(**{
            "type": "pbr",
            "supplier": self.supplier,
			"period": self.period,
            "ref": self.ref,
            "date": self.model_date,
            "due_date": self.model_due_date,
            "total": 120,
            "due": 120,
            "paid": 0,
            "goods": 0,
            "vat": 0,          
        })

        headers = PurchaseHeader.objects.all()
        header = headers[0]

        response = self.client.get(
            reverse("purchases:view", kwargs={"pk": header.pk}))
        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.context["header"],
            header
        )
