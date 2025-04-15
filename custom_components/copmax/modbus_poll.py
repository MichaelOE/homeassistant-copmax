import asyncio
from logging import getLogger
import time

from .const import HOLDING_REGISTER_CODE, INPUT_REGISTER_CODE
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = getLogger(__name__)


class CopmaxModbusPoll:
    def __init__(self, host, port):
        self._lock = asyncio.Lock()
        self._host = host
        self._port = port
        self._errorcount = 0
        self._client = AsyncModbusTcpClient(self._host, port=self._port, timeout=3)

        self.temperatures_valid = False
        self.temperatures_timestamp = time.time()
        self.temperatures = []

        self.user_settings_valid = False
        self.user_settings_timestamp = time.time()
        self.user_settings = []

        self.status_valid = False
        self.status_timestamp = time.time()
        self.status = []

        self.special_functions_valid = False
        self.special_functions_timestamp = time.time()
        self.special_functions = []

    async def poll_heat_pump_data(self):
        try:
            await self._poll_temperatures()
            await self._poll_user_settings()
            await self._poll_status_registers()
            await self._poll_special_functions()
            self._client.close()
            return True
        except Exception as e:
            _LOGGER.error(f"Error PollHeatPumpData: {e}")
            return False

    async def _poll_temperatures(self):
        register_start = 0
        no_of_registers = 6

        _LOGGER.debug(f"Poll temperatures {register_start}:{no_of_registers}")

        temp = await self._modbus_poll_registers(
            INPUT_REGISTER_CODE, register_start, no_of_registers
        )
        if len(temp) == no_of_registers:
            temp2dict = [self.convert_16bit_to_signed(tmp) for tmp in temp]
            self.temperatures = dict(enumerate(temp2dict, start=register_start))

            self.temperatures_valid = True
            self.temperatures_timestamp = time.time()
            _LOGGER.debug(f"Heat pump temperatures {self.temperatures}")
        elif (
            self.temperatures_timestamp + 300
        ) < time.time() or not self.temperatures_valid:
            self.temperatures_valid = False
            _LOGGER.error(f"Invalid temperature data: {temp}")

    async def _poll_user_settings(self):
        register_start = 38
        no_of_registers = 6

        _LOGGER.debug(f"Poll user_Settings {register_start}:{no_of_registers}")

        temp = await self._modbus_poll_registers(
            HOLDING_REGISTER_CODE, register_start, no_of_registers
        )
        if len(temp) == no_of_registers:
            temp2dict = [self.convert_16bit_to_signed(tmp) for tmp in temp]
            self.user_settings = dict(enumerate(temp2dict, start=register_start))

            self.user_settings_valid = True
            self.user_settings_timestamp = time.time()
            _LOGGER.debug(f"Heat pump user_settings {self.user_settings}")
        elif (
            self.user_settings_timestamp + 300
        ) < time.time() or not self.user_settings_valid:
            self.user_settings_valid = False
            _LOGGER.error(f"Invalid user settings data: {temp}")

        if self.user_settings_valid:
            register_start = 44
            no_of_registers = 6

            _LOGGER.debug(f"Poll user_Settings {register_start}:{no_of_registers}")

            temp = await self._modbus_poll_registers(
                HOLDING_REGISTER_CODE, register_start, no_of_registers
            )
            if len(temp) == no_of_registers:
                temp2dict = [self.convert_16bit_to_signed(tmp) for tmp in temp]
                self.user_settings |= dict(enumerate(temp2dict, start=register_start))

                self.user_settings_valid = True
                self.user_settings_timestamp = time.time()
                # _LOGGER.debug(f"Heat pump user_settings {self.user_settings}")
            elif (
                self.user_settings_timestamp + 300
            ) < time.time() or not self.user_settings_valid:
                self.user_settings_valid = False
                _LOGGER.error(f"Invalid user settings data: {temp}")

        if self.user_settings_valid:
            self.user_settings_valid = False
            register_start = 50
            no_of_registers = 7

            _LOGGER.debug(f"Poll user_Settings {register_start}:{no_of_registers}")

            temp = await self._modbus_poll_registers(
                HOLDING_REGISTER_CODE, register_start, no_of_registers
            )
            if len(temp) == no_of_registers:
                temp2dict = [self.convert_16bit_to_signed(tmp) for tmp in temp]
                self.user_settings |= dict(enumerate(temp2dict, start=register_start))

                self.user_settings_valid = True
                self.user_settings_timestamp = time.time()
                _LOGGER.debug(f"Heat pump user_settings {self.user_settings}")
            elif (
                self.user_settings_timestamp + 300
            ) < time.time() or not self.user_settings_valid:
                _LOGGER.error(f"Invalid user settings data: {temp}")

    async def _poll_status_registers(self):
        register_start = 6
        no_of_registers = 7

        _LOGGER.debug(f"Poll status_registers {register_start}:{no_of_registers}")

        temp = await self._modbus_poll_registers(
            INPUT_REGISTER_CODE, register_start, no_of_registers
        )
        if len(temp) == no_of_registers:
            temp2dict = temp
            self.status = dict(enumerate(temp2dict, start=register_start))

            self.status_valid = True
            self.status_timestamp = time.time()
            # _LOGGER.debug(f"Heat pump status {self.status}")
        elif (self.status_timestamp + 300) < time.time() or not self.status_valid:
            self.status_valid = False
            _LOGGER.error(f"Invalid status data: {temp}")

        if self.status_valid:
            self.status_valid = False
            register_start = 13
            no_of_registers = 8

            _LOGGER.debug(f"Poll status_registers {register_start}:{no_of_registers}")

            temp = await self._modbus_poll_registers(
                INPUT_REGISTER_CODE, register_start, no_of_registers
            )
            if len(temp) == no_of_registers:
                temp2dict = temp
                self.status |= dict(enumerate(temp2dict, start=register_start))

                self.status_valid = True
                self.status_timestamp = time.time()
                _LOGGER.debug(f"Heat pump status {self.status}")
            elif (self.status_timestamp + 300) < time.time() or not self.status_valid:
                _LOGGER.error(f"Invalid status data: {temp}")

    async def _poll_special_functions(self):
        register_start = 24
        no_of_registers = 6

        _LOGGER.debug(f"Poll special_functions {register_start}:{no_of_registers}")

        temp = await self._modbus_poll_registers(
            HOLDING_REGISTER_CODE, register_start, no_of_registers
        )
        if len(temp) == no_of_registers:
            temp2dict = [self.convert_16bit_to_signed(tmp) for tmp in temp]
            self.special_functions = dict(enumerate(temp2dict, start=register_start))

            self.special_functions_valid = True
            self.special_functions_timestamp = time.time()
            _LOGGER.debug(f"Heat pump special_functions {self.special_functions}")
        elif (
            self.special_functions_timestamp + 300
        ) < time.time() or not self.user_settings_valid:
            self.special_functions_valid = False
            _LOGGER.error(f"Invalid special_functions data: {temp}")

        if self.special_functions_valid:
            self.special_functions_valid = False
            register_start = 30
            no_of_registers = 8

            _LOGGER.debug(f"Poll special_functions {register_start}:{no_of_registers}")

            temp = await self._modbus_poll_registers(
                HOLDING_REGISTER_CODE, register_start, no_of_registers
            )
            if len(temp) == no_of_registers:
                temp2dict = [self.convert_16bit_to_signed(tmp) for tmp in temp]
                self.special_functions |= dict(
                    enumerate(temp2dict, start=register_start)
                )

                self.special_functions_valid = True
                self.special_functions_timestamp = time.time()
                _LOGGER.debug(f"Heat pump special_functions {self.special_functions}")
            elif (
                self.special_functions_timestamp + 300
            ) < time.time() or not self.special_functions_valid:
                _LOGGER.error(f"Invalid special_functions data: {temp}")

    async def _modbus_poll_registers(
        self, register_code: hex, start_addr: int, count_num: int, slave_addr: int = 1
    ):
        try:
            _LOGGER.debug(f"Modbus request:")
            if not self._client.connected:
                _LOGGER.debug(f"Connecting...")
                await self._client.connect()
            else:
                _LOGGER.debug(f"Already connected.")

            await asyncio.sleep(0.7)

            if self._client.connected:
                _LOGGER.debug(
                    f"Request for data, code:{register_code} start:{start_addr} count: {count_num}"
                )
                match register_code:
                    case 0x03:
                        resp = await self._client.read_holding_registers(
                            start_addr, count=count_num, slave=slave_addr
                        )
                    case 0x04:
                        resp = await self._client.read_input_registers(
                            start_addr, count=count_num, slave=slave_addr
                        )
                    # case _:

                if resp.isError():
                    _LOGGER.error(f"Error reading input registers: {resp}")
                    return []

                # Handle the response (process your data here)
                _LOGGER.debug(f"Result: {resp.registers}")
                return resp.registers

        except ModbusException as exception_error:
            _LOGGER.warning(
                f"{self._host}:{self._port} - connection failed, retrying in pymodbus ({exception_error!s})"
            )
        except Exception as general_error:
            _LOGGER.error(
                f"{self._host}:{self._port} - unexpected error during connection: {general_error!s}"
            )

        return []

    async def modbus_write_holding_register(
        self, register_addr: int, value: int, multiplier: int = 1, slave_addr: int = 1
    ) -> int:
        try:
            if not self._client.connected:
                await self._client.connect()

            intValue = int(self.convert_signed_to_16bit(value) * multiplier)

            if self._client.connected:
                resp = await self._client.write_register(
                    register_addr, intValue, slave=slave_addr
                )

                if resp.isError():
                    _LOGGER.error(f"Error reading input registers: {resp}")
                    return -2

                # Handle the response (process your data here)
                return intValue

        except ModbusException as exception_error:
            _LOGGER.warning(
                f"{self._host}:{self._port} - connection failed, retrying in pymodbus ({exception_error!s})"
            )
        except Exception as general_error:
            _LOGGER.error(
                f"{self._host}:{self._port} - unexpected error during connection: {general_error!s}"
            )

        return -1

    def convert_16bit_to_signed(self, value):
        # Ensure the value is within the 16-bit range
        if value < 0 or value > 65535:
            raise ValueError("Value must be between 0 and 65535 for a 16-bit register")

        # If the value is greater than 32767, it's a negative number in two's complement
        if value > 32767:
            return value - 65536  # Convert to signed by subtracting 65536 (2^16)

        return value  # It's already a positive signed number

    def convert_signed_to_16bit(self, value):
        # Ensure the value is within the signed 16-bit range
        if value < -32768 or value > 32767:
            raise ValueError(
                "Value must be between -32768 and 32767 for a signed 16-bit register"
            )

        # If the value is negative, convert it to its unsigned 16-bit representation
        if value < 0:
            return value + 65536  # Convert to unsigned by adding 65536 (2^16)

        return value  # It's already a positive unsigned number
