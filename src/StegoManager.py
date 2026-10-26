from enum import IntEnum, Enum
from pathlib import Path

from src.encoders import LSBEncoder, ByteEncoder, MetadataEncoder, FITSEncoder, HybridEncoder


IMG = {'.pgm', '.vda', '.png', '.sgi', '.ico', '.ps', '.jpe', '.tiff', '.rgba', '.icb', '.j2k', '.fit', '.apng', '.tga', '.fli', '.wmf', '.eps', '.ftc', '.gbr', '.j2c', '.tif', '.msp', '.bw', '.pcx', '.dcx', '.jpx', '.icns', '.bufr', '.iim', '.flc', '.pdf', '.gif', '.grib', '.mpo', '.jpeg', '.jpg', '.mpg', '.pbm', '.psd', '.fits', '.jpf', '.palm', '.im', '.h5', '.rgb', '.mpeg', '.hdf', '.jfif', '.pfm', '.ras', '.dib', '.cur', '.vst', '.webp', '.jp2', '.xbm', '.xpm', '.pnm', '.dds', '.bmp', '.jpc', '.blp', '.pxr', '.ppm', '.ftu', '.qoi', '.emf', '.pcd'} 
FITS = {".fits", ".fit"}
AUDIO = {".wav", ".aiff", ".aif"}
ARCHIVE = {".zip", ".tar", ".7z", ".rar"}


class StegoMode(IntEnum):
    STEALTH = 0
    BALANCED = 1
    CAPACITY = 2


class StegoMethod(Enum):
    #LSB
    LSB = 'lsb'

    #Byte
    BYTE = 'byte'
    
    #Metadata
    METADATA = 'meta'

    #FITS
    FITS_HEADER = 'fits_header'
    FITS_HEADER_AND_DATA = 'fits_header_data'
    FITS_DATA = 'fits_data'

    #Hybrids
    METADATA_AND_LSB = 'meta_lsb'
    METADATA_AND_BYTE = 'meta_byte'


EMBED_METHODS = {
    ("image", StegoMode.STEALTH): StegoMethod.METADATA,
    ("image", StegoMode.BALANCED): StegoMethod.METADATA_AND_LSB,
    ("image", StegoMode.CAPACITY): StegoMethod.LSB,

    ("fits", StegoMode.STEALTH): StegoMethod.FITS_HEADER,
    ("fits", StegoMode.BALANCED): StegoMethod.FITS_HEADER_AND_DATA,
    ("fits", StegoMode.CAPACITY): StegoMethod.FITS_DATA,

    ("audio", StegoMode.STEALTH): StegoMethod.METADATA,
    ("audio", StegoMode.BALANCED): StegoMethod.METADATA_AND_LSB,
    ("audio", StegoMode.CAPACITY): StegoMethod.LSB,

    ("archive", StegoMode.STEALTH): StegoMethod.METADATA,
    ("archive", StegoMode.BALANCED): StegoMethod.METADATA_AND_BYTE,
    ("archive", StegoMode.CAPACITY): StegoMethod.BYTE,
}



class StegoManager():
    def __init__(self, carryFile: Path):
        self.carryFile = carryFile
        self.ext = carryFile.suffix.lower()


    def __detect_file_type(self):
        
        if self.ext in IMG:
            return "image"

        if self.ext in FITS:
            return "fits"

        if self.ext in AUDIO:
            return "audio"

        if self.ext in ARCHIVE:
            return "archive"

        return "binary"

    
    def select_encoder(self, mode: StegoMode):
        fileType = self.__detect_file_type()
        method = EMBED_METHODS[(fileType, mode)]

        match method:
            case StegoMethod.LSB:
                return LSBEncoder()

            case StegoMethod.BYTE:
                return ByteEncoder()
            
            case StegoMethod.METADATA:
                return MetadataEncoder(self.ext)
         
            case StegoMethod.FITS_HEADER:
                return FITSEncoder('header')
            
            case StegoMethod.FITS_HEADER_AND_DATA:
                return FITSEncoder('mixed')
            
            case StegoMethod.FITS_DATA:
                return FITSEncoder('data')
            
            case StegoMethod.METADATA_AND_LSB:
                return HybridEncoder(MetadataEncoder(self.ext), LSBEncoder())
            
            case StegoMethod.METADATA_AND_BYTE:
                return HybridEncoder(MetadataEncoder(self.ext), ByteEncoder())

            case _:
                raise ValueError(f"Unsupported embedding method '{method}' for filetype {fileType}.")



