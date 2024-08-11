class PixelMock():
    def get_factory_identification(self, _: int) -> str:
        return "Pixel display mock. It ain't doing anything"
    def get_gid(self, _: int) -> str:
        return "G84x16x14/S101"