import openerp.tests

inject = [
    "./../../../website/static/src/js/website.tour.test.js",
    "./../../../website_event_sale/static/src/js/website.tour.event_sale.js",
]

@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUi(openerp.tests.HttpCase):
    def test_admin(self):
        self.phantom_js("/", "openerp.website.Tour.run('event_buy_tickets', 'test')", "openerp.website.Tour.tours.event_buy_tickets", inject=inject)

    def test_demo(self):
        self.phantom_js("/", "openerp.website.Tour.run('event_buy_tickets', 'test')", "openerp.website.Tour.tours.event_buy_tickets", login="demo", password="demo", inject=inject);

    def test_public(self):
        self.phantom_js("/", "openerp.website.Tour.run('event_buy_tickets', 'test')", "openerp.website.Tour.tours.event_buy_tickets", login=None, inject=inject);

