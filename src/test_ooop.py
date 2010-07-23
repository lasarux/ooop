import unittest
from ooop import OOOP

class TestOOOP(unittest.TestCase):
    """OOOP testing"""
    def test_adapting_models_name_to_ooor_compat(self):
        """ 
            Adapting the models name from res.partner
            to ResPartner being more close to ooor 
            implementation
        """
        self.assertEquals(OOOP.normalize_model_name('res.partner'), 'ResPartner')


    def test_adapting_models_name_to_ooor_compat(self):
        """ 
            Adapting the models name from res.partner
            to ResPartner being more close to ooor 
            implementation
        """
        self.assertEquals(OOOP.normalize_model_name('res.partner.address'), 'ResPartnerAddress')
        
        
