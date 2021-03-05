from unittest import TestCase
from unittest.mock import patch, MagicMock

from koiki.create_delivery import CreateDelivery


class CreateDeliveryTest(TestCase):

    def setUp(self):
        self.order = {
            'order_key': 'xxx',
            'customer_note': 'delivery testing',
            'shipping': {
                'first_name': 'James',
                'last_name': 'Bond',
                'address_1': 'Address 1',
                'address_2': 'address 2',
                'postcode': '08025',
                'city': 'Barcelona',
                'state': 'Barcelona',
                'country': 'ES'
            },
            'billing': {
                'email': 'email@example.com',
                'phone': '+34666554433'
            }
        }

    @patch('koiki.create_delivery.Sender', autospec=True)
    @patch('koiki.create_delivery.Recipient', autospec=True)
    @patch('koiki.create_delivery.Order', autospec=True)
    def test_body(self, MockOrder, MockRecipient, MockSender):
        mock_order = MagicMock()
        mock_order.to_dict.return_value = {'order key': 'dummy value'}
        MockOrder.return_value = mock_order

        mock_recipient = MagicMock()
        mock_recipient.to_dict.return_value = {'recipient key': 'dummy value'}
        MockRecipient.return_value = mock_recipient

        mock_sender = MagicMock()
        mock_sender.to_dict.return_value = {'recipient sender': 'dummy value'}
        MockSender.return_value = mock_sender

        body = CreateDelivery(self.order).body()
        self.assertEqual(body, {
            'formatoEtiqueta': 'PDF',
            'envios': [{
                'order key': 'dummy value',
                'recipient key': 'dummy value',
                'recipient sender': 'dummy value'
            }]
        })

    @patch('koiki.create_delivery.Sender')
    def test_body_calls_sender(self, MockSender):
        CreateDelivery(self.order).body()
        MockSender().to_dict.assert_called_once()

    @patch('koiki.create_delivery.Recipient')
    def test_body_calls_recipient(self, MockRecipient):
        CreateDelivery(self.order).body()
        MockRecipient().to_dict.assert_called_once()

    def test_url(self):
        self.assertEqual(CreateDelivery(self.order).url(), '/altaEnvios')
