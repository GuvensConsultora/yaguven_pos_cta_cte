def migrate(cr, version):
    """El install inicial (buggy) redefinió credit_limit sin company_dependent, dejando
    la columna res_partner.credit_limit como `numeric`. Debe ser `jsonb` (company_dependent
    nativo). Postgres no castea numeric->jsonb, así que se dropea la columna corrupta y Odoo
    la recrea con el tipo correcto al cargar el registry en este mismo upgrade.
    Los valores previos eran 0/sin uso (no había límites de crédito cargados aún)."""
    cr.execute("ALTER TABLE res_partner DROP COLUMN IF EXISTS credit_limit")
