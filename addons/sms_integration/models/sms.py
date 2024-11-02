import json
import requests
import logging
from odoo import fields , models, tools, _
from odoo.addons.sms.tools.sms_api import SmsApi

_logger = logging.getLogger(__name__)

class SmsSms(models.Model):
    
    _inherit = 'sms.sms'
    IAP_TO_SMS_STATE_SUCCESS = {
        'processing': 'process',
        'success': 'sent',
        # These below are not returned in responses from IAP API in _send but are received via webhook events.
        'sent': 'pending',
        'delivered': 'sent',
    }
    IAP_TO_SMS_FAILURE_TYPE = {
        'insufficient_credit': 'sms_credit',
        'wrong_number_format': 'sms_number_format',
        'country_not_supported': 'sms_country_not_supported',
        'server_error': 'sms_server',
        'unregistered': 'sms_acc'
    }

    BOUNCE_DELIVERY_ERRORS = {'sms_invalid_destination', 'sms_not_allowed', 'sms_rejected'}
    DELIVERY_ERRORS = {'sms_expired', 'sms_not_delivered', *BOUNCE_DELIVERY_ERRORS}

    provider_id = fields.Many2one('sms.provider', string="SMS Provider", required=True)
    provider_number_id = fields.Many2one('sms.provider.number', string='Provider Number', required=True)

    
    def _send(self, unlink_failed=False, unlink_sent=True, raise_exception=False):
        
        """Send SMS after checking the number (presence and formatting)."""
       
        grouped_sms = {}
        for sms in self:
             key = (sms.body, sms.provider_id.id)  # Grouping by both body and provider_id
             if key not in grouped_sms:
                grouped_sms[key] = []
             grouped_sms[key].append(sms)
             
        """Send SMS after checking the number (presence and formatting)."""
        messages = [{
            'content': body,
            'numbers': [{'number': sms.number, 'uuid': sms.uuid} for sms in sms_records],
            'provider': provider_id,
            'send_number':sms_records[0].provider_number_id.id,
        } for (body, provider_id), sms_records in grouped_sms.items()]
        

        _logger.info('Messages %s', messages)

        provider = self.env['sms.provider'].browse(messages[0]['provider'])

        if provider.name == 'sms.ir':

            provider_model = self.env['sms.ir.provider']
            provider_model.send(messages)
            _logger.info('Messagessssss%s', messages)
            
        else:
            _logger.info('>>>>>>>>>%s', provider.name)
            provider_model = self.env['sms.faraz.provider']
            response_data = provider_model.send(messages)
            _logger.info('Messagessssss%s', messages)  
            
        try:
            # Send the request to the SMS API
            response = provider_model.send(messages)
            _logger.info('response//////////// %s', response)
            response_data = response.json()
            if provider.name == 'sms.ir':
                message_ids = response_data.get('data', {}).get('messageIds')
                status = response_data.get('status')

                if status == 1:
                    delivery_reports_url = f"https://api.sms.ir/v1/send/{message_ids}"
                    _logger.info(f"Delivery reports URL: {delivery_reports_url}")
                    results = [{'uuid': sms['uuid'], 'state': 'success'} for sms in messages[0]['numbers']]
                else:
                    results = [{'uuid': sms['uuid'], 'state': 'server_error'} for sms in messages[0]['numbers']]
                    _logger.error(f"Failed to get messageId. Response: {response_data}")

            elif provider.name == 'faraz':
                message_id = response_data.get('data', {}).get('message_id')
                status = response_data.get('status')  
                _logger.info('status......... %s', status)

                if status == 'OK':  
                    delivery_reports_url = f"https://api.farazsms.com/v1/send/{message_id}"  
                    _logger.info(f"Delivery reports URL: {delivery_reports_url}")
                    results = [{'uuid': sms['uuid'], 'state': 'success'} for sms in messages[0]['numbers']]
                else:
                    results = [{'uuid': sms['uuid'], 'state': 'server_error'} for sms in messages[0]['numbers']]
                    _logger.error(f"Failed to get message_id. Response: {response_data}")

            else:
                _logger.error(f"Unknown provider: {provider.name}")
                results = [{'uuid': sms['uuid'], 'state': 'unknown_provider'} for sms in messages[0]['numbers']]

        except Exception as e:
            _logger.info('Sent batch %s SMS: %s: failed with exception %s', len(self.ids), self.ids, e)
            if raise_exception:
                raise
            results = [{'uuid': sms['uuid'], 'state': 'server_error'} for sms in messages[0]['numbers']]

        _logger.info('Send batch %s SMS: %s: gave %s', len(self.ids), self.ids, results)

        results_uuids = [result['uuid'] for result in results]
        all_sms_sudo = self.env['sms.sms'].sudo().search([('uuid', 'in', results_uuids)]).with_context(sms_skip_msg_notification=True)

        # Update SMS records based on the results
        for iap_state, results_group in tools.groupby(results, key=lambda result: result['state']):
            sms_sudo = all_sms_sudo.filtered(lambda s: s.uuid in {result['uuid'] for result in results_group})
            if success_state := self.IAP_TO_SMS_STATE_SUCCESS.get(iap_state):
                sms_sudo.sms_tracker_id._action_update_from_sms_state(success_state)
                to_delete = {'to_delete': True} if unlink_sent else {}
                sms_sudo.write({'state': success_state, 'failure_type': False, **to_delete})
            else:
                failure_type = self.IAP_TO_SMS_FAILURE_TYPE.get(iap_state, 'unknown')
                if failure_type != 'unknown':
                    sms_sudo.sms_tracker_id._action_update_from_sms_state('error', failure_type=failure_type)
                else:
                    sms_sudo.sms_tracker_id._action_update_from_provider_error(iap_state)
                to_delete = {'to_delete': True} if unlink_failed else {}
                sms_sudo.write({'state': 'error', 'failure_type': failure_type, **to_delete})

        all_sms_sudo.mail_message_id._notify_message_notification_update()
    
