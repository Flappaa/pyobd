"""
Two new OBDCommand objects for long-coding read/write.
"""
from obd import OBDCommand
from obd.utils import bytes_to_int
from .vag_security import vag_seed_key

# --- helpers --------------------------------------------------------------
UDS_READ  = 0x22
UDS_WRITE = 0x2E
UDS_SEC   = 0x27

def _sec_access(level, seed):
    return OBDCommand("SecurityAccess",
                      f"SecurityAccess {level:02X}",
                      f"{UDS_SEC:02X}{level:02X}{seed:04X}",
                      0, lambda m: m)

def _read_coding(ecu_id):
    return OBDCommand("ReadLongCoding",
                      "Read long coding",
                      f"{UDS_READ:02X}F190",   # DID F190 = coding
                      30,                      # 30-byte reply expected
                      lambda m: m)             # raw hex for GUI

def _write_coding(ecu_id, new_bytes):
    assert len(new_bytes) == 30
    hex_str = new_bytes.hex()
    return OBDCommand("WriteLongCoding",
                      "Write long coding",
                      f"{UDS_WRITE:02X}F190{hex_str}",
                      0, lambda m: m)

# --- public register ------------------------------------------------------
def install_coding_cmds(connection, ecu_id=0x09):
    # 1) security access 05 (5-digit SKC)
    seed_cmd = _sec_access(0x05, 0)
    resp     = connection.query(seed_cmd)
    seed     = bytes_to_int(resp.value) & 0xFFFF
    key      = vag_seed_key(seed)
    key_cmd  = _sec_access(0x06, key)
    connection.query(key_cmd)

    # 2) add the two long-coding commands to the connection
    connection.supported_commands.add(_read_coding(ecu_id))
    connection.supported_commands.add(_write_coding(ecu_id, b'\x00'*30))
