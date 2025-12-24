"""
VW-TP 2.0 transport for factory coding (500 k CAN, 29-bit, 0x200-0x2FF range).
"""
from obd.protocols.protocol import Protocol
from obd.utils import bytes_to_int

class VAG_TP20(Protocol):
    ID_MASK     = 0x1FFFFFFF
    TX_ID       = 0x200          # base diag request ID
    RX_ID       = 0x2FF          # base diag response ID

    def __init__(self, lines_0100):
        super().__init__(lines_0100)

    def parse_frame(self, frame):
        # strip 0xA0/0xB0 header, return pure UDS payload
        data = frame.data
        if len(data) < 2:
            return []
        if data[0] & 0xF0 == 0xA0:          # single frame
            length = data[0] & 0x0F
            return [data[1:1+length]]
        if data[0] == 0xB0:                  # first consecutive
            return [data[2:]]                 # ignore length byte
        return [data]                         # fallback

    def build_request(self, sid, pid=0, data=bytes()):
        # create a classic 8-byte CAN frame
        payload = bytes([sid, pid]) + data
        length  = len(payload)
        if length <= 7:
            return bytes([0xA0 + length]) + payload.ljust(7, b'\x00')
        # multi-frame not needed for coding cmds
        return bytes([0xA0 + 7]) + payload[:7]
