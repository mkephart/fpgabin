#! /usr/bin/env python
import unittest
import fpga
import struct

class TestPackVal(unittest.TestCase):
    """Tests that a value of various types is correctly converted
    to binary."""
    def setUp(self):
        self.obj = fpga.MemType()

    def test_8bit(self):
        """8-bit value, type = "B"."""
        self.obj.fmt = "B"
        val = 1
        self.assertEqual('\x01',self.obj.pack_val(val))
        val = 255
        self.assertEqual('\xff',self.obj.pack_val(val))

    def test_16bit(self):
        """16-bit value, type = "H"."""
        self.obj.fmt = "H"
        val = 1
        self.assertEqual('\x00\x01',self.obj.pack_val(val))
        val = 1024
        self.assertEqual('\x04\x00',self.obj.pack_val(val))

    def test_64bit(self):
        """64-bit value, type = "Q"."""
        self.obj.fmt = "Q"
        val = 1
        self.assertEqual('\x00\x00\x00\x00\x00\x00\x00\x01',self.obj.pack_val(val))
        val = 18374686479671623680
        self.assertEqual('\xff\x00\x00\x00\x00\x00\x00\x00',self.obj.pack_val(val))

    def test_invalid_vals(self):
        """Value outside allowed range raises ValueError."""
        self.obj.fmt = "B"
        val = 256
        self.assertRaises(ValueError,self.obj.pack_val,val)

class TestPackMem(unittest.TestCase):
    """Tests the binary stream produced from an array of values."""
    def setUp(self):
        self.obj = fpga.MemType()

    def test_value8(self):
        """8-bit values."""
        self.obj.fmt = "B"
        data = [1,2,3,4]
        self.obj.vals = data
        expout = '\x01\x02\x03\x04'
        self.assertEqual(expout,self.obj.pack_mem())

    def test_value16(self):
        """16-bit values."""
        self.obj.fmt = "H"
        data = [1,2,3,4]
        self.obj.vals = data
        expout = '\x00\x01\x00\x02\x00\x03\x00\x04'
        self.assertEqual(expout,self.obj.pack_mem())

    def test_empty_array(self):
        """Empty array of any type produces empty string."""
        self.obj.fmt = "B"
        self.obj.vals = []
        self.assertEqual('',self.obj.pack_mem())
        self.obj.fmt = "Q"
        self.assertEqual('',self.obj.pack_mem())

class TestUploadToFPGA(unittest.TestCase):
    """Tests that arrays are successfully written to binary files."""
    @classmethod
    def setUpClass(TestUploadToFPGA):
        """Loads a small set of values into memory, of all 5 different types."""
        regmem = [1,6,8,4] + [0]*12
        prgmem = [18,24,0,5] + [0]*508
        hskmem = [0,1,2,3] + [0]*508
        seqmem = [1,2] + [0]*1022
        clvmem = [3,4] + [0]*126
        fpga.upload_to_fpga(REG_MEM=regmem, SEQ_MEM=seqmem, PRG_MEM=prgmem,
                            HSK_SEL_MEM=hskmem,VOLT_MEM=clvmem)

    def get_32bit(self,fname):
        """Reads a binary file as a set of 32-bit values (as read
        by the FPGA)."""
        with open(fname,'rb') as f:
            data = f.read()
        return list(struct.unpack(">"+"I"*(len(data)/4),data))

    def test_check_regmem(self):
        """Tests register memory (16-bit values)."""
        self.assertEqual([65542,524292]+[0]*6,
                self.get_32bit('RegMem.bin'))

    def test_check_prgmem(self):
        """Tests program memory (64-bit values)."""
        self.assertEqual([0,18,0,24,0,0,0,5]+[0]*1016,
                self.get_32bit('PrgMem.bin'))

    def test_check_hskmem(self):
        """Tests housekeeping memory (8-bit values)."""
        self.assertEqual([66051]+[0]*127,
                self.get_32bit('HSKMem.bin'))

    def test_check_seqmem(self):
        """Tests sequence memory (64-bit values)."""
        self.assertEqual([0,1,0,2]+[0]*2044,
                self.get_32bit('SeqMem.bin'))

    def test_update(self):
        """Tests that if a new array is input, the file is changed
        (and no other files are altered)."""
        clvmem = [19,27] + [0]*126
        fpga.upload_to_fpga(VOLT_MEM=clvmem)
        self.assertEqual([1245211]+[0]*63,
                self.get_32bit('CLVMem.bin'))
        clvmem = [0]*128
        fpga.upload_to_fpga(VOLT_MEM=clvmem)
        self.assertEqual([0]*64,
                self.get_32bit('CLVMem.bin'))
        self.assertEqual([65542,524292]+[0]*6,
                self.get_32bit('RegMem.bin'))
        self.assertEqual([0,1,0,2]+[0]*2044,
                self.get_32bit('SeqMem.bin'))
        self.assertEqual([0,18,0,24,0,0,0,5]+[0]*1016,
                self.get_32bit('PrgMem.bin'))
        self.assertEqual([66051]+[0]*127,
                self.get_32bit('HSKMem.bin'))


if __name__=="__main__":
    unittest.main(buffer=True)
