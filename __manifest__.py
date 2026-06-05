{
    "name": "Yagüven — POS Cuenta Corriente Autorizada",
    "version": "19.0.1.0.1",
    "category": "Point of Sale",
    "summary": "Solo clientes autorizados (límite de crédito) pueden cerrar tickets a "
               "cuenta corriente en el POS; el resto debe cobrarse antes de emitir.",
    "description": """
Control de cuenta corriente en el Punto de Venta
================================================
- El método de pago "Cuenta de cliente" (pay_later) solo se habilita si el cliente
  tiene crédito autorizado (`use_partner_credit_limit`) y no supera su `credit_limit`.
- Quien no está autorizado debe cobrarse (efectivo/tarjeta/MP) antes de cerrar el ticket
  — consecuencia del comportamiento nativo del POS (cerrar exige tender completo).
- La autorización de crédito la maneja solo el grupo "Autoriza crédito Cta Cte"; el cajero
  ve los campos pero no los edita. Campos de crédito auditados (tracking).
- Guard de backend en `pos.order` (defensa en profundidad, no se saltea por API).
""",
    "author": "Yagüven C.G.",
    "website": "https://yaguven.com",
    "license": "LGPL-3",
    "depends": [
        "point_of_sale",
        "account",
    ],
    "data": [
        "security/pos_cta_cte_groups.xml",
        "views/res_partner_views.xml",
        "data/account_credit_limit.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "yaguven_pos_cta_cte/static/src/js/payment_screen_cta_cte.js",
        ],
    },
    "installable": True,
    "application": False,
}
