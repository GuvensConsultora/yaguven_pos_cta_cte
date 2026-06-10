/**
 * UX: bloquea elegir "Cuenta de cliente" (pay_later) en el POS si el cliente NO está
 * autorizado a cuenta corriente (use_partner_credit_limit) o supera su límite.
 *
 * IMPORTANTE: esto es solo experiencia de usuario (frenar temprano con un mensaje claro).
 * La garantía real es el guard de backend en pos.order (_check_cta_cte_autorizada),
 * que NO se saltea aunque este JS falle o quede desactualizado.
 *
 * Nombres de API del POS O19 (addNewPaymentLine, currentOrder, get_partner,
 * get_total_with_tax, paymentMethod.type) son volátiles entre versiones: validar
 * corriendo el POS y reapuntar si cambió alguno.
 */
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

/** O19 renombró la API del order a camelCase (getPartner, getTotalWithTax);
 *  resolver con fallback para tolerar ambas variantes. */
function partnerDe(order) {
    if (!order) return null;
    if (typeof order.getPartner === "function") return order.getPartner();
    if (typeof order.get_partner === "function") return order.get_partner();
    return order.partner_id || null;
}
function totalDe(order) {
    if (!order) return 0;
    if (typeof order.getTotalWithTax === "function") return order.getTotalWithTax();
    if (typeof order.get_total_with_tax === "function") return order.get_total_with_tax();
    return 0;
}

patch(PaymentScreen.prototype, {
    async addNewPaymentLine(paymentMethod) {
        if (paymentMethod && paymentMethod.type === "pay_later") {
            const order = this.currentOrder;
            const motivo = this._ctaCteBloqueada(partnerDe(order));
            if (motivo) {
                this.dialog.add(AlertDialog, {
                    title: _t("Cuenta corriente no autorizada"),
                    body: motivo,
                });
                return false;
            }
        }
        return super.addNewPaymentLine(...arguments);
    },

    /** Devuelve el mensaje de bloqueo, o false si está habilitado. */
    _ctaCteBloqueada(partner) {
        if (!partner) {
            return _t("Seleccioná un cliente para cobrar a cuenta corriente.");
        }
        if (!partner.use_partner_credit_limit) {
            return _t(
                "El cliente «%s» no está autorizado para cuenta corriente. " +
                "Cobrá el ticket (efectivo/tarjeta) antes de cerrarlo.",
                partner.name
            );
        }
        const limite = partner.credit_limit || 0;
        const deuda = partner.credit || 0;
        const total = totalDe(this.currentOrder);
        if (limite && deuda + total > limite) {
            return _t(
                "El cliente «%s» supera su límite de crédito autorizado.",
                partner.name
            );
        }
        return false;
    },
});
