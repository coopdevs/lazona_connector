from unittest import TestCase
import pycountry
from koiki.woocommerce.state import State, InvalidState


class StateTest(TestCase):

    def test_with_code(self):
        barcelona = State("B")
        self.assertEquals(barcelona.value, pycountry.subdivisions.get(code="ES-B"))

        girona = State("GI")
        self.assertEquals(girona.value, pycountry.subdivisions.get(code="ES-GI"))

        tarragona = State("T")
        self.assertEquals(tarragona.value, pycountry.subdivisions.get(code="ES-T"))

        lleida = State("L")
        self.assertEquals(lleida.value, pycountry.subdivisions.get(code="ES-L"))

    def test_with_invalid_code(self):
        with self.assertRaises(InvalidState):
            State("invalid")

    def test_with_name(self):
        barcelona = State("Barcelona")
        self.assertEquals(barcelona.value, pycountry.subdivisions.get(code="ES-B"))

        girona = State("Girona")
        self.assertEquals(girona.value, pycountry.subdivisions.get(code="ES-GI"))

        tarragona = State("Tarragona")
        self.assertEquals(tarragona.value, pycountry.subdivisions.get(code="ES-T"))

        lleida = State("Lleida")
        self.assertEquals(lleida.value, pycountry.subdivisions.get(code="ES-L"))

    def test_foreign_state(self):
        with self.assertRaises(InvalidState):
            State("DE-BY")
