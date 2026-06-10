from markupsafe import Markup
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import html_escape


class ResPartner(models.Model):
    _inherit = "res.partner"

    # NO redefinir use_partner_credit_limit / credit_limit: son campos nativos
    # (credit_limit es company_dependent; redefinirlos rompe el compute nativo).
    # La auditoría de quién autoriza se hace con el override de write() de abajo.

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

    def _es_consumidor_final_generico(self):
        """True si el partner es el consumidor final genérico/anónimo: el nativo de
        l10n_ar (par_cfa) o duplicados de migración (mismo nombre, sin CUIT). Estos
        partners nunca pueden operar a cuenta corriente: representan ventas sin
        cliente identificado, no una persona con la que exista relación de crédito."""
        self.ensure_one()
        cfa = self.env.ref("l10n_ar.par_cfa", raise_if_not_found=False)
        if cfa and self.id == cfa.id:
            return True
        return "consumidor final" in (self.name or "").strip().lower() and not self.vat

    def write(self, vals):
        """Auditoría: si cambia la autorización de crédito, dejar constancia en el
        chatter (quién y a qué valor). Reemplaza el tracking, que no se puede usar
        sobre estos campos nativos sin romperlos."""
        if vals.get("use_partner_credit_limit"):
            for partner in self:
                if partner._es_consumidor_final_generico():
                    raise ValidationError(_(
                        "No se puede autorizar cuenta corriente a «%s»: es el "
                        "consumidor final genérico (ventas sin cliente identificado). "
                        "Para vender a cuenta corriente, usar un cliente real con "
                        "identificación.", partner.display_name))
        auditar = {"use_partner_credit_limit", "credit_limit"} & set(vals)
        res = super().write(vals)
        if auditar:
            usuario = html_escape(self.env.user.name)
            detalle = ", ".join(f"{html_escape(k)} = {html_escape(str(vals[k]))}" for k in sorted(auditar))
            body = Markup("<p><strong>Autorización de crédito modificada</strong> por %s</p><p>%s</p>") % (
                Markup(usuario), Markup(detalle))
            for partner in self:
                partner.message_post(body=body, message_type="comment", subtype_xmlid="mail.mt_note")
        return res
