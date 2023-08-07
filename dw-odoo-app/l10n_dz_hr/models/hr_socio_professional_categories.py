from odoo import _, api, fields, models


class HrSocioProfessionalCategories(models.Model):
    _name = 'hr.socioprofessional.categories'

    def name_get(self):
        return [(record.id, "[%s] %s" % (record.code, record.name)) for record in self]

    name = fields.Char(
        "name"
    )
    code = fields.Char(
        "Code"
    )
    socio_professional_levels_ids = fields.One2many(
        'hr.socioprofessional.categories.levels',
        'socio_professional_category_id',
        'Levels'
    )
    description = fields.Text()


class HrSocioProfessionalCategorieslevels(models.Model):
    _name = 'hr.socioprofessional.categories.levels'

    name = fields.Char(
        "name"
    )
    socio_professional_category_id = fields.Many2one(
        'hr.socioprofessional.categories',
        'Level'
    )

    def name_get(self):
        return [(record.id, "[%s] %s" % (record.name, record.socio_professional_category_id.name)) for record in self]
