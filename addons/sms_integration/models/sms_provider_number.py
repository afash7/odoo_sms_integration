from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)

class SmsProviderNumber(models.Model):
    _name = "sms.provider.number"
    _description = 'SMS Provider Number'
    _rec_name = 'number'

    number = fields.Char(string='Phone Number', required=True, size=255)
    provider_id = fields.Many2one('sms.provider', string='Provider', ondelete='cascade', required=True)
    

