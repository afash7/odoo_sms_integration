from odoo import models, fields
import requests
import logging
import http
import json
import logging


_logger = logging.getLogger(__name__)

class FarazProvider(models.Model):
    _name = 'sms.faraz.provider'
    _inherit = 'sms.provider'
    _description = ' Faraz SMS  Provider'
    

    #def __init__(self, env):
        #pass 



    def send(self, messages):
        provider_number = self.env['sms.provider.number'].browse(messages[0]['send_number'])
        send_number = provider_number.number
        _logger.info('Provider number: %s', send_number)

        # FarazSMS API URL
        url = "https://api2.ippanel.com/api/v1/sms/send/webservice/single"

        headers = {
            'accept': 'application/json',
            'apikey': '-o7JcnNYQ0dkLlQma0S89SG1SqTfomMPcoVQWjH3sFw=',
            'Content-Type': 'application/json'
            }
        payload = json.dumps({
            "sender": send_number,  # Replace with your line number
            "recipient": [sms['number'] for sms in messages[0]['numbers']],  # The list of phone numbers
            "message": messages[0]['content'],  # Assuming all messages have the same content
        })

        # Send the request to the SMS API
        response = requests.request("POST", url, headers=headers, data=payload)
        return response
    
        
    def _send_sms_batch(self, messages, delivery_reports_url=False):
        # Faraz-specific API call logic
       pass
    
    