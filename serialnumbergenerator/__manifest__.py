{
    "name": "Custom Serial Number For CR3D",
    "version": "18.0.1.1",
    "depends": ["mrp", "stock"],
    "author": "Stefan Weiß",
    "category": "Manufacturing",
    "summary": "Automatically generates custom serial numbers on production order completion",
    "description": "Generates serial numbers in the format [Serie][Höhe][Custom][Version][RandomPart] based on product internal reference.",
    "installable": True,
    "application": False,
    "auto_install": False,
    'data': [
    'views/stock_lot_passwords.xml',
],
}