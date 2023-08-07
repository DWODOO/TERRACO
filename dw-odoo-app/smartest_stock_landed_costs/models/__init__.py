# -*- coding: utf-8 -*-
from odoo.addons.stock_landed_costs.models.stock_landed_cost import SPLIT_METHOD
SPLIT_METHOD.append(('hs_code', 'HS code'))
from . import stock_landed_cost
from . import hs_code
from . import product_template
from . import  product_category
from . import  stock_move
# from . import  import_folder
# from . import  purchase_order
# from . import  comex_file

