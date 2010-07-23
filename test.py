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
        models = {
            'res.partner': 'ResPartner',
            'res.partner.address': 'ResPartnerAddress'
        }
        for key, value in models.items():
            self.assertEquals(OOOP.normalize_model_name(key), value)


if __name__ == '__main__':
    unittest.main()
