import struct
from pixel import Pixel
noImages = False
try:
    import numpy as np
    from PIL import Image
except ModuleNotFoundError:
    noImages = True

class PixelMock():
    def __init__(self, gid: str = None):
        self._pixelInst = Pixel("MOCK")
        self._gid = gid
    def get_factory_identification(self, _: int) -> str:
        return "Pixel display mock. It ain't doing anything"
    def get_gid(self, _: int) -> str:
        return "G120x16x14/S101" if self._gid is None else self._gid
    
    def set_validators_block(self, blocked: bool) -> None:
        print(f"[PIXEL MOCK] Set validators block to {blocked}")
    
    def send_command(self, displayNo: int, command: str) -> bool:
        if displayNo < 0 or displayNo > 7:
            raise ValueError('Display number is out of supported range (0-7)')
        print(f'[PIXEL MOCK] Would send command to display {displayNo}:\n{command}')
        return True

    def delete_all_pages(self, displayNo: int) -> None:
        print(f'[PIXEL MOCK] Would delete all pages on display {displayNo}')

    def display_data_block(self, displayNo: int, block: str) -> None:
        self.send_command(displayNo, 'DDB {}'.format(block))
    
    def create_data_block(self, data: bytes) -> str:
        return self._pixelInst.create_data_block(data)

    if not noImages:
        def get_image_data(self, imageData: np.ndarray = None, imageObj: Image = None, invert: bool = False, page: int = 0):
            return self._pixelInst.get_image_data(imageData, imageObj, invert, page)
        
    def _set_bit(self, value, bit):
        return value | (1<<bit)
    
    def _clear_bit(self, value, bit):
        return value & ~(1<<bit)