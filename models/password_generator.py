from odoo import models, fields, api
import string
import random

class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    password_pi = fields.Char(string="Password Pi", readonly=True)
    password_admin = fields.Char(string="Password Admin", readonly=True)
    password_maintainer = fields.Char(string="Password Maintainer", readonly=True)
    password_user = fields.Char(string="Password User", default="12345678", readonly=True)
    password_touch_maintainer = fields.Char(string="Password Touch Maintainer", default="Maintain3r", readonly=True)
    password_useradmin = fields.Char(string="Password UserAdmin", default="SysAdm1n", readonly=True)

    def _generate_unique_passwords(self, count=3, length=8):
        excluded_chars = {'0', 'O', 'l', 'I'}
        allowed_chars = [c for c in string.ascii_letters + string.digits if c not in excluded_chars]
        passwords = []

        while len(passwords) < count:
            pw = ''.join(random.choices(allowed_chars, k=length))
            if pw not in passwords:  # prevent duplicates in one batch
                passwords.append(pw)

        return passwords
    
    @api.model
    def create(self, vals):
        lot = super().create(vals)

        # Only generate if not already set (so manual creation works too)
        if not lot.password_pi and not lot.password_admin and not lot.password_maintainer:
            passwords = lot._generate_unique_passwords(3)
            lot.write({
                'password_pi': passwords[0],
                'password_admin': passwords[1],
                'password_maintainer': passwords[2],
            })

        return lot
