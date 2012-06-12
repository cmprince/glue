import unittest

from mock import MagicMock

import glue

class HubLog(glue.hub.HubListener):
    def __init__(self):
        self.messages = []

    def register_to_hub(self, hub):
        hub.subscribe(self, glue.Message)

    def notify(self, message):
        self.messages.append(message)

class TestDataCollection(unittest.TestCase):
    def setUp(self):
        self.dc = glue.DataCollection()
        self.data = MagicMock()
        self.hub = glue.Hub()
        self.log = HubLog()
        self.log.register_to_hub(self.hub)

    def test_init(self):
        d = glue.Data()
        dc = glue.DataCollection(d)
        self.assertIn(d, dc)
        dc = glue.DataCollection([d])
        self.assertIn(d, dc)

    def test_append(self):
        self.dc.append(self.data)
        self.assertIn(self.data, self.dc)

    def test_ignore_multi_add(self):
        self.dc.append(self.data)
        self.dc.append(self.data)
        self.assertEquals(len(self.dc), 1)

    def test_remove(self):
        self.dc.append(self.data)
        self.dc.remove(self.data)
        self.assertNotIn(self.data, self.dc)

    def test_ignore_multi_remove(self):
        self.dc.append(self.data)
        self.dc.remove(self.data)
        self.dc.remove(self.data)
        self.assertNotIn(self.data, self.dc)

    def test_append_broadcast(self):
        self.dc.register_to_hub(self.hub)
        self.dc.append(self.data)
        msg = self.log.messages[-1]
        self.assertEquals(msg.sender, self.dc)
        self.assertIsInstance(msg, glue.message.DataCollectionAddMessage)
        self.assertIs(msg.data, self.data)

    def test_remove_broadcast(self):
        self.dc.register_to_hub(self.hub)
        self.dc.append(self.data)
        self.dc.remove(self.data)
        msg = self.log.messages[-1]
        self.assertEquals(msg.sender, self.dc)
        self.assertIsInstance(msg, glue.message.DataCollectionDeleteMessage)
        self.assertIs(msg.data, self.data)

    def test_register_adds_hub(self):
        self.dc.register_to_hub(self.hub)
        self.assertIs(self.dc.hub, self.hub)

    def test_register_assigns_hub_of_data(self):
        self.dc.append(self.data)
        self.dc.register_to_hub(self.hub)
        self.data.register_to_hub.assert_called_once_with(self.hub)

    def test_get_item(self):
        self.dc.append(self.data)
        self.assertIs(self.dc[0], self.data)

    def test_iter(self):
        self.dc.append(self.data)
        self.assertEquals(set(self.dc), set([self.data]))

    def test_len(self):
        self.assertEquals(len(self.dc), 0)
        self.dc.append(self.data)
        self.assertEquals(len(self.dc), 1)
        self.dc.append(self.data)
        self.assertEquals(len(self.dc), 1)
        self.dc.remove(self.data)
        self.assertEquals(len(self.dc), 0)


if __name__ == "__main__":
    unittest.main()