# from odoo import api, fields, models, tools, _

# import logging

# _logger = logging.getLogger(__name__)

# class SmsProvider(models.Model):
#     _name = 'sms.provider'
#     _description = 'SMS Provider'

#     name = fields.Char("Provider Name", required=True)
#     api_key = fields.Char("API Key")
#     api_url = fields.Char("API URL")
    

#     def send_sms(self, to_number, message, provider_number):
#         """
#         Implement the logic to send an SMS through the provider's API
#         """
#         if self.name == 'Provider A':
#             # Send via Provider A API
#             response = self._send_via_provider_a(to_number, message, provider_number)
#         elif self.name == 'Provider B':
#             # Send via Provider B API
#             response = self._send_via_provider_b(to_number, message, provider_number)
#         # Add more providers as needed
        
#         return response

#     def _send_via_provider_a(self, to_number, message, provider_number):
#         # Example logic to call Provider A's API
#         data = {
#             'to': to_number,
#             'message': message,
#             'from': provider_number.number,  # Assuming provider_number is an object with a 'number' field
#             'api_key': self.api_key,
#         }
#         # Here, we would use the requests module to send an HTTP request to the provider API
#         # response = requests.post(self.api_url, json=data)
#         response = {}  # Simulated response
#         return response

#     def _send_via_provider_b(self, to_number, message, provider_number):
#         # Logic to send via Provider B API
#         pass
from odoo import api, fields, models, tools, _
from abc import ABC, abstractmethod
import logging

_logger = logging.getLogger(__name__)

class SmsProvider(models.Model):
    _name = 'sms.provider'
    _description = 'SMS Provider'
    

    name = fields.Char(string='Provider Name', required=True)
    api_url = fields.Char(string='API URL')
    api_key = fields.Char(string='API Key', required=True)
    phone_numbers = fields.One2many('sms.provider.number', 'provider_id', string='Phone Numbers')
    support_contact = fields.Char(string='Support Contact', help="Optional support contact information.")

   
   
    #@abstractmethod
    #def __init__(self, env):

        #pass
    @abstractmethod 
    def send(self, messages ):
        pass

    @abstractmethod
    def _send_sms_batch(self, messages, delivery_reports_url=False):
       pass

