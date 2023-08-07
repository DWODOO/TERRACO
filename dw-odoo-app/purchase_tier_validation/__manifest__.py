# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Tier Validation",
    "summary": "Extends the functionality of Purchase Orders to "
    "support a tier validation process.",
    "version": "15.",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase","base_tier_validation"],
    "data": [
        'security/purchase_product_request_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/sequence.xml',
        'views/purchase_product_request_view.xml',
        'views/purchase_product_request_line_view.xml',
        'views/purchase_order_view.xml',
        'views/menus.xml',
        'reports/report_purchase_request.xml',
    ],
}
