from odoo import fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    DISPATCHED_SELECTION = [
        ("0", "No"),
        ("1", "Not Required"),
        ("2", "On Remote Dispatcher"),
        ("3", "On Local Dispatcher"),
        ("4", "On Local Reception"),
    ]

    PASSPORT_SELECTION = [
        ("1", "At Customer"),
        ("2", "At The Manufacturer"),
        ("3", "In A Service Company"),
        ("0", "Unknown"),
    ]

    is_lift = fields.Boolean("Is Lift", default=False)
    is_dispatched = fields.Selection(
        DISPATCHED_SELECTION, "Is Dispatched", default="0", tracking=True
    )
    capacity = fields.Char("Capacity", size=10, tracking=True)
    stops = fields.Char("Stops", size=3, tracking=True)
    passport = fields.Selection(
        PASSPORT_SELECTION, "Passport", default="0", tracking=True
    )
    require_inspection = fields.Boolean("Require Inspection", default=False)
    inspection_company_id = fields.Many2one(
        "res.partner", "Inspection Company", tracking=True
    )
    date_next_inspection = fields.Date("Next Inspection", tracking=True)
