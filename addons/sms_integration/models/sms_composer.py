import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)

class SmsComposer(models.TransientModel):
    _inherit = 'sms.composer'

    provider_id = fields.Many2one('sms.provider', string="SMS Provider")
    provider_number_id = fields.Many2one('sms.provider.number', string="Provider Number")




    @api.onchange('provider_id')
    def _onchange_provider(self):
        if self.provider_id:
            return {'domain': {'provider_number_id': [('provider_id', '=', self.provider_id.id)]}}
        else:
            return {'domain': {'provider_number_id': []}}  



    def _action_send_sms_comment(self, records=None):
        records = records if records is not None else self._get_records()
        _logger.info('_action_send_sms_comment records= %s ', records)
        subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')

        

        vals = {'body': self.body, 'partner_ids': [(6, 0, [self.res_id])], 'author_id': self.env.user.partner_id.id,
            'model': self.res_model, 'res_id': self.res_id, 'subtype_id': subtype_id, 'message_type': 'sms',
            'record_company_id': self.env.company.id}
        mail_message = self.env['mail.message'].create(vals)
        mail_message_id = mail_message.id

        sms_values = [{'mail_message_id': mail_message_id, 'partner_id': self.res_id, 'body':self.body, 
             'number': self.recipient_single_number, 'provider_id': self.provider_id.id, 'provider_number_id': self.provider_number_id.id}]
        return self.env['sms.sms'].sudo().create(sms_values).send() 
