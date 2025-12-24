"""
5-digit SKC seed->key algorithm (pre-2015 VAG).
"""
def vag_seed_key(seed: int) -> int:
    key = ((seed ^ 0x7891) + 0x2278) & 0xFFFF
    return ((key >> 8) | (key << 8)) & 0xFFFF   # endian swap
