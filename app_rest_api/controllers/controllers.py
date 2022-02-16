# -*- coding: utf-8 -*-
from crypt import methods
from datetime import date
from werkzeug import exceptions
from odoo import http

from .base import api_view, get_select_options


class AppRestApi(http.Controller):

    @http.route('/api/authenticate', type='json', auth="none", cors="*")
    def authenticate(self, db, login, password):
        http.request.session.authenticate(db, login, password)
        return http.request.env['ir.http'].session_info()

    @http.route(['/api/contact', '/api/contact/<int:id>'], auth="user", type="json", cors="*")
    def contact(self, **kwargs):
        return api_view(
            "res.partner",
            fields=[
                "name",
                "phone",
                "mobile",
                "contact_address",
                "x_studio_driver_license",
                "x_studio_date_of_birth_1",
                "bank_ids",  # model: res.partner.bank
                # "bank_account_count",
                "street",
                "street2",
                "city",
                "zip",
                "country_id",  # model: res.country
                "company_type",
                "property_account_receivable_id",  # model: account.account
                "property_account_payable_id",  # model: account.account
            ],
            optional_fields=[
                "title",
                "email",
                "website",
                "image_medium",
                # "image_128",
                # "image_256",
                # "image_512",
                # "image_1024",
                # "image_1920",
                "child_ids",
                "type",
                "property_payment_term_id",  # model: account.payment.term
                "vat",
            ],
            filters={"name": "ilike", "type": "="},
            kwargs=kwargs
        )

    @http.route(['/api/bank', '/api/bank/<int:id>'], auth="user", type="json", cors="*")
    def bank(self, **kwargs):
        return api_view(
            "res.partner.bank",
            fields=[
                "active",
                "acc_type",
                "acc_number",
                "sanitized_acc_number",
                "acc_holder_name",
                "partner_id",
                "bank_id",
                "bank_name",
                "bank_bic",
                "currency_id"
                "company_id"
            ],
            filters={
                "acc_number": "ilike",
                "partner_id": "=",
            },
            kwargs=kwargs
        )

    @http.route(['/api/country', '/api/country/<int:id>'], auth="user", type="json", methods=["GET"], cors="*")
    def country(self, **kwargs):
        return api_view(
            "res.country",
            fields=["name", "code"],
            optional_fields=[
                "currency_id",
                "image_url",
                "phone_code"
            ],
            filters={
                "name": "ilike",
                "code": "="
            },
            kwargs=kwargs
        )

    @http.route(['/api/account', '/api/account/<int:id>'], auth="user", type="json", cors="*")
    def account(self, **kwargs):
        return api_view(
            "account.account",
            filters={
                "name": "ilike",
                "company_id": "="
            },
            kwargs=kwargs
        )

    @http.route(['/api/payment_term', '/api/payment_term/<int:id>'], auth="user", type="json", methods=["GET"], cors="*")
    def payment_term(self, **kwargs):
        return api_view(
            "account.payment.term",
            fields=["name", "note"],
            optional_fields=["line_ids"],
            filters={"name": "ilike"},
            kwargs=kwargs
        )

    @http.route(['/api/invoice', '/api/invoice/<int:id>'], auth="user", type="json", cors="*")
    def invoice(self, **kwargs):
        return api_view(
            "account.move",
            fields=[
                "name",
                "partner_id",
                "payment_reference",
                "invoice_date",
                "invoice_payment_term_id",  # model: account.payment.term
                "journal_id",  # model: account.journal
                "currency_id",  # model: res.currency
                "line_ids",  # model: account.move.line
            ],
            defaults={"invoice_date": date.today},
            filters={"name": "ilike", "partner_id": "="},
            kwargs=kwargs
        )

    @http.route(['/api/journal', '/api/journal/<int:id>'], auth="user", type="json", methods=["GET"], cors="*")
    def journal(self, **kwargs):
        return api_view(
            "account.journal",
            filters={"display_name": "ilike"},
            kwargs=kwargs
        )

    @http.route(['/api/currency', '/api/currency/<int:id>'], auth="user", type="json", methods=["GET"], cors="*")
    def currency(self, **kwargs):
        return api_view(
            "res.currency",
            filters={"full_name": "ilike", "symbol": "="},
            kwargs=kwargs
        )

    @http.route(['/api/invoice/line', '/api/invoice/line/<int:id>'], auth="user", type="json", cors="*")
    def invoice_line(self, **kwargs):
        return api_view(
            "account.move.line",
            fields=[
                "name",
                "product_id",  # model: product.product
                "quantity",
                "price_unit",
                "tax_ids",  # model: account.tax
            ],
            filters={"name": "ilike", "product_id": "="},
            kwargs=kwargs
        )

    @http.route(['/api/product', '/api/product/<int:id>'], auth="user", type="json", methods=["GET"], cors="*")
    def product(self, **kwargs):
        return api_view(
            "product.product",
            filters={
                "display_name": "ilike",
                "code": "=",
                "description": "ilike"
            },
            kwargs=kwargs
        )

    @http.route(['/api/tax', '/api/tax/<int:id>'], auth="user", type="json", methods=["GET"], cors="*")
    def tax(self, **kwargs):
        return api_view(
            "account.tax",
            filters={"display_name": "ilike", "description": "ilike"},
            kwargs=kwargs
        )

    @http.route(['/api/signature', '/api/signature/<int:id>'], auth="user", type="json", methods=["GET", "PUT", "PATCH"], cors="*")
    def signature(self, **kwargs):
        return api_view(
            "sign.request",
            filters={
                "display_name": "ilike",
                "state": "=",
                "subject": "ilike"
            },
            kwargs=kwargs
        )

    @http.route(['/api/signature/send', '/api/signature/send/<int:id>'], auth="user", type="json", methods=["GET", "POST"], cors="*")
    def signature_send(self, **kwargs):
        return api_view(
            "sign.send.request",
            fields=[
                "signer_ids",
                "follower_ids",
                "subject",
                "filename",
                "template_id"
            ],
            filters={"display_name": "ilike", "filename": "ilike"},
            defaults={"signers_count": lambda: None},
            actions={"POST": [("create_request", ["id"])]},
            kwargs=kwargs
        )

    @http.route(['/api/signature/template', '/api/signature/template/<int:id>'], auth="user", type="json", methods=["GET"], cors="*")
    def signature_template(self, **kwargs):
        return api_view(
            "sign.template",
            filters={"display_name": "ilike"},
            kwargs=kwargs
        )
