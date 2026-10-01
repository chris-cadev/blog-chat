def get_username_color(username: str) -> str:
    hash_value = 0x811C9DC5
    for byte in username.encode("utf-8"):
        hash_value ^= byte
        hash_value = (hash_value * 0x01000193) & 0xFFFFFFFF
    hue = hash_value % 360
    return f"hsl({hue}, 70%, 45%)"
