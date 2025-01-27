from odoo import models, fields
import requests
import logging
import http
import json
import logging

_logger = logging.getLogger(__name__)

class SmsIrProvider(models.Model):
    _name = 'sms.ir.provider'
    _inherit = 'sms.provider'
    _description = 'SMS IR Provider'
    


    #def __init__(self, env):
        #pass 



    def send(self, messages):
        provider_number = self.env['sms.provider.number'].browse(messages[0]['send_number'])
        send_number = provider_number.number
        _logger.info('provider_number %s', send_number)
        

        url = ""
        headers = {
            'X-API-KEY': '',
            'Content-Type': 'application/json',
        }
        payload = json.dumps({
            "lineNumber": send_number,  # Replace with your line number
            "messageText": messages[0]['content'],  # Assuming all messages have the same content
            "mobiles": [sms['number'] for sms in messages[0]['numbers']],  # The list of phone numbers
            "sendDateTime": None  # If you're sending immediately, otherwise set the datetime
        })

        # Send the request to the SMS API
        response = requests.request("POST", url, headers=headers, data=payload)
        return response
      
    def _send_sms_batch(self, messages, delivery_reports_url=False):
        # sms.ir-specific API call logic
       pass