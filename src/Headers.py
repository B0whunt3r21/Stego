from enum import IntEnum


class HeaderVersion(IntEnum):
    BASIC = 1
    ARCHIVE = 2
    FITS = 3


'''
Header reference:
[MARK][VERSION][FLAGS][PAYLOAD_LENGTH][NAME_LENGTH][SALT][NONCE][TAG][NAME]
    5       1       1           8            1         16    16    16   var
'''
HEADER_LAYOUTS = {
    HeaderVersion.BASIC: [
        ("magic", 5)
        ,("version", 1)
        ,("flags", 1)
        ,("payload_length", 8)
        ,("name_length", 1)
        ,("salt", 16)
        ,("nonce", 16)
        ,("tag", 16)
        ,("name", "var")
    ],


    HeaderVersion.ARCHIVE: [
        ("magic", 5)
        ,("version", 1)
        ,("flags", 1)
        ,("compressed", 1)
        ,("payload_length", 8)
        ,("name_length", 1)
        ,("salt", 16)
        ,("nonce", 16)
        ,("tag", 16)
        ,("name", "var")
    ],

        
    HeaderVersion.FITS: [
        ("magic", 5)
        ,("version", 1)
        ,("flags", 1)
        ,("payload_length", 8)
        ,("name_length", 1)
        ,("hdu_index", 2)
        ,("chunk_count", 2)
        ,("salt", 16)
        ,("nonce", 16)
        ,("tag", 16)
        ,("name", "var")
    ],
    
}



class Headers():
    def __init__(self, version: HeaderVersion):
        self.version = version
        self.structure = HEADER_LAYOUTS[version]


    def build(self, **fields) -> bytes:
            header = bytearray()

            for name, size in self.layout:
                value = fields[name]

                if size == "var":
                    header.extend(value)
                else:
                    if isinstance(value, int):
                        header.extend(value.to_bytes(size, "big"))
                    else:
                        header.extend(value)

            return bytes(header)


    def parse(self, data: bytes) -> dict:
        pos = 0
        result = {}

        for name, size in self.layout:
            if size == "var":
                length = result["name_length"]
                result[name] = data[pos:pos+length]
                pos += length
            else:
                result[name] = data[pos:pos+size]
                pos += size

        return result
    

