class PixelMock():
    def __init__(self, gid: str = None):
        self._gid = gid

    def open(self) -> bool:
        return True

    def get_factory_identification(self, _: int) -> str:
        return "Pixel display mock. It ain't doing anything"

    def get_gid(self, _: int) -> str:
        return "G120x16x14/S101" if self._gid is None else self._gid

    def get_did(self, _: int) -> str:
        return "MOCK"

    def get_available_commands(self, _: int) -> str:
        return ""

    def set_validators_block(self, blocked: bool) -> None:
        print(f"[PIXEL MOCK] Set validators block to {blocked}")

    def send_command(self, displayNo: int, command: str) -> bool:
        if displayNo < 0 or displayNo > 15:
            raise ValueError('Display number is out of supported range (0-15)')
        print(f'[PIXEL MOCK] Would send command to display {displayNo}:\n{command}')
        return True

    def delete_all_pages(self, displayNo: int) -> None:
        print(f'[PIXEL MOCK] Would delete all pages on display {displayNo}')

    def display_data_block(self, displayNo: int, block) -> None:
        if hasattr(block, "to_hex"):
            block = block.to_hex()
        elif isinstance(block, (bytes, bytearray)):
            block = bytes(block).hex().upper()
        self.send_command(displayNo, 'DDB {}'.format(block))
