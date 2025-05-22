from odoo import models
import re
import random
import string
import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _generate_serial_number(self):
        """
        Input: MA-100-1-22-0-02 → Output: 10012202ABC123
        """
        self.ensure_one()
        default_code = self.product_id.default_code or ''
        _logger.info("Generating serial from: %s", default_code)

        match = re.match(r"MA-(\d{3})-(\d{1})-(\d{2})-\d-(\d{2})", default_code)
        if not match:
            return None

        serie, hoehe, kopf, version = match.groups()
        base = f"{serie}{hoehe}{kopf}{version}"
        population = string.ascii_uppercase + string.digits

        for _ in range(5):  # Retry up to 5 times to avoid accidental duplicates
            random_part = ''.join(random.choices(population, k=6))
            serial = base + random_part

            # Ensure serial is not already used
            existing = self.env['stock.lot'].search([
                ('name', '=', serial),
                ('product_id', '=', self.product_id.id)
            ], limit=1)

            if not existing:
                return serial

        raise UserError(_("Could not generate a unique serial number after several attempts."))

    def _check_sn_uniqueness(self):
        _logger.warning("Bypassing _check_sn_uniqueness for production %s", self.name)
        return True  # Skip default check
    
    def action_start(self):
        res = super().action_start()

        for production in self:
            if production.state == 'progress' and not production.lot_producing_id:
                serial = production._generate_serial_number()
                if serial is None:
                    return
                _logger.info("Generated serial on start: %s", serial)

                for move in production.move_finished_ids:
                    # Check if the lot already exists
                    existing_lot = self.env['stock.lot'].search([
                        ('name', '=', serial),
                        ('product_id', '=', move.product_id.id),
                        ('company_id', '=', production.company_id.id),
                    ], limit=1)

                    # Check if this lot is used in another production
                    if existing_lot:
                        already_used = self.env['mrp.production'].search([
                            ('lot_producing_id', '=', existing_lot.id),
                            ('id', '!=', production.id)
                        ], limit=1)

                        if already_used:
                            raise UserError(
                                _("Serial '%s' for product '%s' is already used in production '%s'")
                                % (serial, move.product_id.display_name, already_used.name)
                            )

                    # Use existing or create
                    lot = existing_lot or self.env['stock.lot'].create({
                        'name': serial,
                        'product_id': move.product_id.id,
                        'company_id': production.company_id.id,
                    })

                    # Assign to move and lines
                    move.lot_ids = [(4, lot.id)]
                    for move_line in move.move_line_ids.filtered(lambda l: not l.lot_id):
                        move_line.lot_id = lot.id

                    production.lot_producing_id = lot.id

                    if serial not in production.name:
                        production.name = f"{production.name} - {serial}"
            else:
                _logger.info("Skipping serial generation for production %s; already has lot %s",
                            production.name, production.lot_producing_id.name if production.lot_producing_id else "None")

        return res


                        


