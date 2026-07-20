"""Modbus TCP simulator for the SmartGrid Meter scenario.

Pretends to be three smart meters (slave IDs 1, 2, 3). Each meter holds
ten holding registers:
    0: instantaneous power (W)
    1: voltage L1 (V * 10)
    2: voltage L2 (V * 10)
    3: voltage L3 (V * 10)
    4: current L1 (A * 100)
    5: current L2 (A * 100)
    6: current L3 (A * 100)
    7: total energy kWh
    8: tariff index
    9: firmware version (encoded)
"""

import logging
import random
import threading
import time

from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server.sync import StartTcpServer

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("modbus-sim")


def make_meter(power_base):
    """Return a slave context preloaded with realistic register values.

    Modbus registers are uint16 (max 65535). Multi-word values such as
    cumulative energy use two registers (high word, low word).
    """
    total_kwh = random.randint(120000, 140000)
    initial = [
        power_base + random.randint(-150, 150),  # 0  power W
        2305 + random.randint(-30, 30),          # 1  voltage L1 *10
        2308 + random.randint(-30, 30),          # 2  voltage L2 *10
        2301 + random.randint(-30, 30),          # 3  voltage L3 *10
        random.randint(800, 1500),               # 4  current L1 *100
        random.randint(800, 1500),               # 5  current L2 *100
        random.randint(800, 1500),               # 6  current L3 *100
        (total_kwh >> 16) & 0xFFFF,              # 7  total kWh high word
        total_kwh & 0xFFFF,                      # 8  total kWh low word
        0x0103,                                  # 9  fw version 1.3
    ]
    return ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, initial))


def updater(context):
    """Periodically jiggle the register values so the meter feels live."""
    while True:
        for slave_id, base in [(1, 4200), (2, 3100), (3, 5500)]:
            slave = context[slave_id]
            current_values = slave.getValues(3, 0, count=10)
            current_values[0] = base + random.randint(-200, 200)
            # Increment the 32-bit kWh counter (registers 7=high, 8=low)
            total = (current_values[7] << 16) | current_values[8]
            total = (total + random.randint(0, 3)) & 0xFFFFFFFF
            current_values[7] = (total >> 16) & 0xFFFF
            current_values[8] = total & 0xFFFF
            slave.setValues(3, 0, current_values)
        time.sleep(2)


def main():
    slaves = {
        1: make_meter(4200),
        2: make_meter(3100),
        3: make_meter(5500),
    }
    context = ModbusServerContext(slaves=slaves, single=False)
    threading.Thread(target=updater, args=(context,), daemon=True).start()
    log.info("modbus simulator listening on 0.0.0.0:5020 (slaves 1/2/3)")
    StartTcpServer(context, address=("0.0.0.0", 5020))


if __name__ == "__main__":
    main()
