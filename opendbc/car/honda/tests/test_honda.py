import re
import unittest

from opendbc.car.honda.fingerprints import FW_VERSIONS
from opendbc.car.honda.values import HONDA_BOSCH, HONDA_BOSCH_TJA_CONTROL

HONDA_FW_VERSION_RE = br"[A-Z0-9]{5}(-|,)[A-Z0-9]{3}(-|,)[A-Z0-9]{4}(\x00){2}$"


class TestHondaFingerprint(unittest.TestCase):
  def test_fw_version_format(self):
    # Asserts all FW versions follow an expected format
    for fw_by_ecu in FW_VERSIONS.values():
      for fws in fw_by_ecu.values():
        for fw in fws:
          assert re.match(HONDA_FW_VERSION_RE, fw) is not None, fw

  def test_tja_bosch_only(self):
    assert set(HONDA_BOSCH_TJA_CONTROL).issubset(set(HONDA_BOSCH)), "Nidec car found in TJA control list"


class TestHondaHybridBGear(unittest.TestCase):
  def test_b_position_is_decoded_and_drivable(self):
    # the CR-V hybrid sends GEAR_SHIFTER = 11 in "B"; it used to read as unknown and raise wrongGear
    from opendbc.can import CANDefine
    from opendbc.car import Bus, structs
    from opendbc.car.honda.interface import CarInterface
    from opendbc.car.honda.values import CAR, DBC
    from opendbc.car.interfaces import CarStateBase

    GearShifter = structs.CarState.GearShifter
    shifter_values = CANDefine(DBC[CAR.HONDA_CRV_6G][Bus.pt]).dv["GEARBOX_AUTO"]["GEAR_SHIFTER"]
    assert shifter_values[11] == "B"
    assert CarStateBase.parse_gear_shifter(shifter_values.get(11)) == GearShifter.brake
    assert GearShifter.brake in CarInterface.DRIVABLE_GEARS
    # D and the other positions keep their meaning
    assert CarStateBase.parse_gear_shifter(shifter_values.get(4)) == GearShifter.drive
    assert CarStateBase.parse_gear_shifter(shifter_values.get(1)) == GearShifter.park
    assert CarStateBase.parse_gear_shifter(shifter_values.get(2)) == GearShifter.reverse
