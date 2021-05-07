class Port:
    def __init__(self, name: str, port_id: int) -> None:
        """
        :param name: Name of the port. This name is used in CLI commands to refer to the port.
        :param port_id: ID of the port. For internal use by the library.
        """
        self.name = name
        self.id = port_id

    def __repr__(self) -> str:
        return self.name
