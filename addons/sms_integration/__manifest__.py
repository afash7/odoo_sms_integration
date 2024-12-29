{
    "name": "SMS Integration",
    "summary": "Module to manage SMS providers and phone numbers for sending messages",
    "description": """    
    to manage all your library transactions
    """,
    "author": "OdooPro",
    "website": "https://google.com",
    "category": "Tools",
    "sequence": 95,
    "version": '1.0.0',
    "depends": [
        "base",
        "sms"
    ],
    "data": [
        'security/ir.model.access.csv',
        "views/sms_provider_view.xml",
        "views/sms_provider_number_view.xml",
        "views/inherited_sms_composer_view.xml"
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}