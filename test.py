import unittest
import fudge
import xmlrpclib
from ooop import OOOP

RESPONSE_IRMODEL = [
    {'info': False, 
     'access_ids': [60, 61], 
     'name': 'Partner', 
     'field_id': [420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 746, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1217, 1218, 1250, 1331, 1332], 
     'state': 'base', 
     'model': 'res.partner', 
     'id': 58},
    {'info': False, 
     'access_ids': [62, 63], 
     'name': 'Partner Addresses', 
     'field_id': [442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458], 
     'state': 'base', 
     'model': 'res.partner.address', 
     'id': 59}
]

class TestOOOP(unittest.TestCase):
    """ OOOP testing """
    def setUp(self):
        fudge.clear_expectations() # from previous tests
        fake_setup = fudge.Fake('xmlrpclib.ServerProxy', expect_call=True)
        fake_api = (
            fake_setup.returns_fake()
            .expects('login').with_arg_count(3)
            .provides('execute').returns(RESPONSE_IRMODEL)
        )
        self.patched = fudge.patch_object(xmlrpclib, 'ServerProxy', fake_setup)

    def tearDown(self):
        self.patched.restore()

    def test_adapting_models_name_to_ooor_compat(self):
        """ 
            Adapting the models name from res.partner
            to ResPartner being more close to ooor 
            implementation
        """
        models = {
            'res.partner': 'ResPartner',
            'res.partner.address': 'ResPartnerAddress'
        }
        for key, value in models.items():
            self.assertEquals(OOOP.normalize_model_name(key), value)
    
    @fudge.with_fakes
    def test_ooop_instance(self):
        n = OOOP(dbname='test')
        self.assertEquals(n.__dict__.has_key('ResPartner'), True)
        self.assertEquals(n.__dict__.has_key('ResPartnerAddress'), True)

            
class TestManager(unittest.TestCase):
    """ Manager testing """
    def setUp(self):
        pass

    def tearDown(self):
        fudge.clear_expectations()

if __name__ == '__main__':
    unittest.main()
