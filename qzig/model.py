import logging
import json

LOGGER = logging.getLogger(__name__)


class Model():
    def _update_data(self):
        pass

    def get_data(self):
        self.update_data()
        return self.data

    def save(self):
        pass

    def _parse(self, data):
        pass

    def load(self, file):
        raw = json.load(file)
        self._parse(raw)
