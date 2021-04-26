from .ip175g import IP175G


class SwitchbloxNano(IP175G):
    def __init__(self):
        super().__init__(nano=True)
