import logging
import time
from typing import Any, Generic, List, TypeVar

import serial


CommandType = TypeVar('CommandType')


class ConfigWriter(Generic[CommandType]):

    def __init__(self, device_name: str) -> None:
        pass

    def __name__(self) -> str:
        return self.device_description()

    @classmethod
    def device_description(cls: 'ConfigWriter') -> str:
        raise NotImplementedError()

    def write(self, data: CommandType) -> bool:
        raise NotImplementedError()


class TestWriter(ConfigWriter[Any]):
    @classmethod
    def device_description(cls: 'TestWriter') -> str:
        return "Test"

    def write(self, data: CommandType) -> bool:
        return True


class UARTWriter(ConfigWriter[List[Any]]):

    def __init__(self, device_name: str) -> None:
        super().__init__(device_name)
        if not device_name.startswith("/dev/"):
            raise ValueError("Wrong UART communication device " + device_name)
        self._device_name = device_name

    @classmethod
    def device_description(cls: 'UARTWriter') -> str:
        return "USB-to-UART converter"

    def write(self, data: List[Any]) -> bool:
        """
        Write data commands to serial port.

        Write data to serial port which the UART converter is connected to. The STM32 MCU
        on the SwitchBlox will then be interrupted and carry out the commands

        :param List[List] data: Commands created to write to STM32 MCU
        :return: Flag to indicate whether the write data to serial was successful or not
        """

        ser = serial.Serial(
            port=self._device_name,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            timeout=20,
            write_timeout=2,
        )

        for command in data:
            x = bytes(command)
            ser.write(x)
            time.sleep(0.1)

        condition = ser.read(size=1)
        ser.close()

        try:
            condition = list(condition)[0]
        except IndexError:
            logging.error('Failed to read condition message from board')
            return False
        else:
            if condition == 1:
                logging.info('Success setting configuration in EEPROM')
                return True
            elif condition == 2:
                logging.error('Failed saving configuration in EEPROM')
                return False
