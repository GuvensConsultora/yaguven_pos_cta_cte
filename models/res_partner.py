from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Auditoría: dejar registrado en el chatter quién cambió la autorización/límite.
    use_partner_credit_limit = fields.Boolean(tracking=True)
    credit_limit = fields.Monetary(tracking=True)

    # Helper de UI: True si el usuario actual puede autorizar crédito (grupo dedicado).
    # Se usa en la vista para dejar los campos de crédito readonly a quien NO lo tiene.
    puede_autorizar_credito = fields.Boolean(
        compute="_compute_puede_autorizar_credito",
        help="Técnico: el usuario pertenece al grupo 'Autoriza crédito Cta Cte'.")

    def _compute_puede_autorizar_credito(self):
        can = self.env.user.has_group("yaguven_pos_cta_cte.group_autoriza_credito")
        for partner in self:
            partner.puede_autorizar_credito = can

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Sumar los campos de crédito a los datos del partner que carga el POS,
        para poder decidir en pantalla si se habilita 'Cuenta de cliente'."""
        fields_list = super()._load_pos_data_fields(config_id)
        for f in ("use_partner_credit_limit", "credit_limit", "credit"):
            if f not in fields_list:
                fields_list.append(f)
        return fields_list
