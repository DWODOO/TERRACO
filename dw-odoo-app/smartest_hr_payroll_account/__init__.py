# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA
from . import models
from . import wizard

# Import Python libs
import logging

# Import Odoo libs
from odoo import _, api, SUPERUSER_ID

# Global Variables
_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    # Initialize variables
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Check if the 'hr_payroll_account' module is installed
    hr_payroll_account_module = env['ir.module.module'].search([
        ('name', '=', 'hr_payroll_account'),
        ('state', '=', 'installed')
    ])

    # If 'hr_payroll_account' is installed then uninstall it
    if hr_payroll_account_module:
        # Log the operation for debugging purpose
        _logger.debug(
            _("'hr_payroll_account' module is installed. We will uninstall this module to use SMARTEST module instead")
        )

        # Uninstall the module
        hr_payroll_account_module.module_uninstall()
