{
'name': 'Public References',
    'category': 'Website',
    'summary': 'Publish Your Public References',
    'version': '1.0',
    'description': """
OpenERP Blog
============

        """,
    'author': 'OpenERP SA',
    'depends': ['website', 'project'],
    'data': [
        'views/website_contract.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
