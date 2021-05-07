from .ip175g import IP175G


class SwitchbloxNano(IP175G):
    """
    Switchblox Nano.
    """
    def __init__(self) -> None:
        super().__init__(nano=True)
