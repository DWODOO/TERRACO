# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_investment = fields.Boolean('Is investment',
                                   help="L’investissement est une « immobilisation », un bien ou un droit dont l’entreprise est propriétaire :"
                                        "- Les immobilisations corporelles ce sont celles qu’on peut toucher (Terrain, Matériel de transport, Matériel informatique, Agencement etc…) ;"
                                        "- Elles augmentent la valeur du patrimoine de l’entreprise et est une source d’avantages économiques futurs ;"
                                        "- Les immobilisations ce sont des biens qui restent plus d’un an dans l’entreprise et dont la valeur unitaire est supérieure à 30.000,00 DA ;"
                                        "- En fin d’année la valeur des immobilisations diminue après la constatation comptable d’une « dotation aux amortissements » considérée comme « charge  non décaissable »."
                                        "La charge est une dépense d’une entreprise qui influe sur le résultat. La catégorie de charges variable fluctue avec l’activité de l’entreprise. Le matériel et outillage informatique et autres dont la valeur unitaire est égale ou inférieure à 30.000,00 DA peuvent être  considérés comme charges et non pas comme immobilisation, conformément à l’Article 141 du Code des Impôts Directes (C.I.D)."
                                        " L’article 141 alinéa 3 du C.I.D, stipule :                                                                     Les éléments de faible valeur dont le montant hors taxes n’excède pas 30 000,00 DA peuvent être constatés comme charge déductible de l’exercice de rattachement. "
                                        " Remarque : On utilise le terme « acquisition » d’immobilisation plutôt que « achat » réservé aux charges.")
