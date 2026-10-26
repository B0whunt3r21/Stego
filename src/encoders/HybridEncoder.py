

class HybridEncoder:
    def __init__(self, headerEncoder, dataEncoder):
        self.headerEnc = headerEncoder
        self.dataEnc = dataEncoder

    def encode(self, carrier, header: bytearray, payload: bytearray):
        carrier = self.headerEnc.encode(carrier, header)
        carrier = self.dataEnc.encode(carrier, payload)
        return carrier


