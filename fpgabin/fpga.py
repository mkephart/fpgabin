#! /usr/bin/env python
import struct

class MemType:
    """Class for writing various memory types"""
    def __init__(self,vals=None):
        self.vals = vals

    def pack_val(self,val,stream=''):
        """Packs one value as the type specified in self.fmt."""
        return stream + struct.pack(">"+self.fmt,val)

    def pack_mem(self,stream=''):
        """Creates concatenated binary stream of an array."""
        for v in self.vals:
            stream = self.pack_val(v,stream)
        return stream

    def write_file():
        """Writes files as e.g. 'RegMem.bin'. If an input array is
        not provided, or if the input array is the wrong size, the
        memory type is skipped and no file is written."""
        print 'Writing '+self.name+' binary...'
        if self.vals is not None:
            if len(self.vals) == self.size:
                stream = self.pack_mem()
                with open(self.name+'.bin','wb') as f:
                    f.write(stream)
                print 'File written: '+self.name+'.bin'
            else:
                print 'Error: input array for '+self.name+'is not the right '+\
                        'size (should be '+str(self.size)+'). Skipping.'
        else:
            print 'No array provided, skipping.'


class RegMem(MemType):
    """Register memory; contains housekeeping and sequence control values."""
    def __init__(self,vals=None):
        self.vals = vals
        self.name = 'RegMem'
        self.fmt = "H"
        self.size = 16

class SeqMem(MemType):
    """Sequence memory; contains programs that control CCD clocks."""
    def __init__(self,vals=None):
        self.vals = vals
        self.name = 'SeqMem'
        self.fmt = "Q"
        self.size = 1024

class PrgMem(MemType):
    """Program memory; contains the programs that control the sequencer."""
    def __init__(self,vals=None):
        self.vals = vals
        self.name = 'PrgMem'
        self.fmt = "Q"
        self.size = 512

class HskMem(MemType):
    """Housekeeping memory; contains values for housekeeping component sample
    selection."""
    def __init__(self,vals=None):
        self.vals = vals
        self.name = 'HSKMem'
        self.fmt = "B"
        self.size = 512

class CLVMem(MemType):
    """Clock level voltage memory; contains values for programming FPE clock
    level voltages via DACs."""
    def __init__(self,vals=None):
        self.vals = vals
        self.name = 'CLVMem'
        self.fmt = "H"
        self.size = 128

def upload_to_fpga(REG_MEM=None, SEQ_MEM=None, PRG_MEM=None, HSK_SEL_MEM=None,
                        VOLT_MEM=None):
    """Writes binary files of appropriate type for each array loaded in.
    Iterables passed in must be of the correct order and size. If one of
    the types is not set, or is of the wrong size, it will be skipped (no
    values will be written)."""
    RegMem(REG_MEM).write_file()
    SeqMem(SEQ_MEM).write_file()
    PrgMem(PRG_MEM).write_file()
    HskMem(HSK_SEL_MEM).write_file()
    CLVMem(VOLT_MEM).write_file()
