from odoo import _, api, models
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.constrains("payment_ids", "partner_id")
    def _check_cta_cte_autorizada(self):
        """Guard de backend (defensa en profundidad): una orden con pago a 'Cuenta de
        cliente' (pay_later) solo se permite si el cliente tiene crédito autorizado
        (`use_partner_credit_limit`) y no supera su límite. No se saltea por API/UI."""
        for order in self:
            paylater = order.payment_ids.filtered(
                lambda p: p.payment_method_id.type == "pay_later" and p.amount > 0
            )
            if not paylater:
                continue
            partner = order.partner_id
            if not partner:
                raise ValidationError(_(
                    "No se puede cerrar a cuenta corriente sin cliente identificado."))
            if not partner.use_partner_credit_limit:
                raise ValidationError(_(
                    "El cliente «%s» no está autorizado para cuenta corriente. "
                    "Debe cobrarse el ticket (efectivo/tarjeta) antes de cerrarlo.",
                    partner.display_name))
            a_cta = sum(paylater.mapped("amount"))
            if partner.credit_limit and (partner.credit + a_cta) > partner.credit_limit:
                raise ValidationError(_(
                    "El cliente «%(p)s» supera su límite de crédito "
                    "(límite %(lim).2f; deuda actual %(deu).2f + este ticket %(tic).2f).",
                    p=partner.display_name, lim=partner.credit_limit,
                    deu=partner.credit, tic=a_cta))
