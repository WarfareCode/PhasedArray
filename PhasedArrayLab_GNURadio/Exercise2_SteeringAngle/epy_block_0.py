"""
Embedded Python Blocks:  

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
import time
import spidev
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block

    def __init__(self, PhaseDelta=45, SignalFreq=10525000000, UpdateRate=2, Rx1_Phase_Cal=0, Rx2_Phase_Cal=0, Rx3_Phase_Cal=0, Rx4_Phase_Cal=0):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Calculate Steering Angle',   # will show up in GRC
            in_sig=[],   # we have no flowgraph inputs to this block
            out_sig=[np.float32]   # we have one flowgraph output, which is the calculated steering angle
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.UpdateRate = UpdateRate
        self.PhaseDelta = PhaseDelta
        self.Rx1_Phase_Cal = Rx1_Phase_Cal
        self.Rx2_Phase_Cal = Rx2_Phase_Cal
        self.Rx3_Phase_Cal = Rx3_Phase_Cal
        self.Rx4_Phase_Cal = Rx4_Phase_Cal
               
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  #set bus=0 and device=0
        self.spi.max_speed_hz = 500000
        self.spi.mode = 0
        
        self.c = 299792458    # speed of light in m/s
        self.d = 0.015        # element to element spacing of the antenna
        self.f = SignalFreq

    def work(self, input_items, output_items):
        # steering angle theta = arcsin(c*deltaphase/(2*pi*f*d)
        # if element spacing is lambda/2 then this simplifies to theta=arcsin(deltaphase(in radians)/pi)
        value1 = (self.c * np.radians(np.abs(self.PhaseDelta)))/(2*3.14159*self.f*self.d)
        clamped_value1 = max(min(1, value1), -1)     #arcsin argument must be between 1 and -1, or numpy will throw a warning
        theta = np.degrees(np.arcsin(clamped_value1))
        if self.PhaseDelta>=0:
            SteerAngle = 90 + theta   # positive PhaseDelta covers 0deg to 90 deg
            Phase_A = (np.abs(self.PhaseDelta*0) + self.Rx4_Phase_Cal) % 360
            Phase_B = (np.abs(self.PhaseDelta*1) + self.Rx3_Phase_Cal) % 360
            Phase_C = (np.abs(self.PhaseDelta*2) + self.Rx2_Phase_Cal) % 360
            Phase_D = (np.abs(self.PhaseDelta*3) + self.Rx1_Phase_Cal) % 360
            channels = [Phase_D, Phase_C, Phase_B, Phase_A]  # if PhaseDelta is positive, then signal source is to the right, so Rx1 needs to be delayed the most
        else:
            SteerAngle = 90 - theta # negative phase delta covers 0 deg to -90 deg
            Phase_A = (np.abs(self.PhaseDelta*0) + self.Rx1_Phase_Cal) % 360
            Phase_B = (np.abs(self.PhaseDelta*1) + self.Rx2_Phase_Cal) % 360
            Phase_C = (np.abs(self.PhaseDelta*2) + self.Rx3_Phase_Cal) % 360
            Phase_D = (np.abs(self.PhaseDelta*3) + self.Rx4_Phase_Cal) % 360  
            channels = [Phase_A, Phase_B, Phase_C, Phase_D]  #  if PhaseDelta is negative, then signal source is to the left, so Rx4 needs to be delayed the most
       
        # The ADDR is set by the address pins on the ADAR1000.  This is set by P10 on the eval board.
        ADDR=0x20            # ADDR 0x20 is set by jumpering pins 4 and 6 on P10
        #ADDR=0x00           # ADDR 0x00 is set by leaving all jumpers off of P10
        
        # Write vector I and Q to set Rx1 (see Table 13 in ADAR1000 datasheet)
        i=1
                
        for Channel_Phase in channels:
            #Channel_Phase = self.Rx1_phase     # Which Rx phase control channel are we looking at?
            if i==1:
                I = 0x14   # Rx1_I vector register address = 0x14
                Q = 0x15   # Rx1_Q vector register address = 0x15
            if i==2:
                I = 0x16   # Rx2_I vector register address = 0x16
                Q = 0x17   # Rx2_Q vector register address = 0x17
            if i==3:
                I = 0x18   # Rx3_I vector register address = 0x18
                Q = 0x19   # Rx3_Q vector register address = 0x19
            if i==4:
                I = 0x1A   # Rx4_I vector register address = 0x1A
                Q = 0x1B   # Rx4_Q vector register address = 0x1B
            i = i+1
            
             # Quadrant 1
            if Channel_Phase==0:
                self.spi.xfer2([ADDR, I, 0x3F])
                self.spi.xfer2([ADDR, Q, 0x20])
            if Channel_Phase==2.8125:
                self.spi.xfer2([ADDR, I, 0x3F])
                self.spi.xfer2([ADDR, Q, 0x21])
            if Channel_Phase==5.625:
                self.spi.xfer2([ADDR, I, 0x3F])
                self.spi.xfer2([ADDR, Q, 0x23])
            if Channel_Phase==8.4375:
                self.spi.xfer2([ADDR, I, 0x3F])
                self.spi.xfer2([ADDR, Q, 0x24])
            if Channel_Phase==11.25:
                self.spi.xfer2([ADDR, I, 0x3F])
                self.spi.xfer2([ADDR, Q, 0x26])
            if Channel_Phase==14.0625:
                self.spi.xfer2([ADDR, I, 0x3E])
                self.spi.xfer2([ADDR, Q, 0x27])
            if Channel_Phase==16.875:
                self.spi.xfer2([ADDR, I, 0x3E])
                self.spi.xfer2([ADDR, Q, 0x28])
            if Channel_Phase==19.6875:
                self.spi.xfer2([ADDR, I, 0x3D])
                self.spi.xfer2([ADDR, Q, 0x2A])
            if Channel_Phase==22.5:
                self.spi.xfer2([ADDR, I, 0x3D])
                self.spi.xfer2([ADDR, Q, 0x2B])
            if Channel_Phase==25.3125:
                self.spi.xfer2([ADDR, I, 0x3C])
                self.spi.xfer2([ADDR, Q, 0x2D])
            if Channel_Phase==28.125:
                self.spi.xfer2([ADDR, I, 0x3C])
                self.spi.xfer2([ADDR, Q, 0x2E])
            if Channel_Phase==30.9375:
                self.spi.xfer2([ADDR, I, 0x3B])
                self.spi.xfer2([ADDR, Q, 0x2F])
            if Channel_Phase==33.75:
                self.spi.xfer2([ADDR, I, 0x3A])
                self.spi.xfer2([ADDR, Q, 0x30])
            if Channel_Phase==36.5625:
                self.spi.xfer2([ADDR, I, 0x39])
                self.spi.xfer2([ADDR, Q, 0x31])
            if Channel_Phase==39.375:
                self.spi.xfer2([ADDR, I, 0x38])
                self.spi.xfer2([ADDR, Q, 0x33])
            if Channel_Phase==42.1875:
                self.spi.xfer2([ADDR, I, 0x37])
                self.spi.xfer2([ADDR, Q, 0x34])
            if Channel_Phase==45:
                self.spi.xfer2([ADDR, I, 0x36])
                self.spi.xfer2([ADDR, Q, 0x35])
            if Channel_Phase==47.8125:
                self.spi.xfer2([ADDR, I, 0x35])
                self.spi.xfer2([ADDR, Q, 0x36])
            if Channel_Phase==50.625:
                self.spi.xfer2([ADDR, I, 0x34])
                self.spi.xfer2([ADDR, Q, 0x37])
            if Channel_Phase==53.4375:
                self.spi.xfer2([ADDR, I, 0x33])
                self.spi.xfer2([ADDR, Q, 0x38])
            if Channel_Phase==56.25:
                self.spi.xfer2([ADDR, I, 0x32])
                self.spi.xfer2([ADDR, Q, 0x38])
            if Channel_Phase==59.0625:
                self.spi.xfer2([ADDR, I, 0x30])
                self.spi.xfer2([ADDR, Q, 0x39])
            if Channel_Phase==61.875:
                self.spi.xfer2([ADDR, I, 0x2F])
                self.spi.xfer2([ADDR, Q, 0x3A])
            if Channel_Phase==64.6875:
                self.spi.xfer2([ADDR, I, 0x2E])
                self.spi.xfer2([ADDR, Q, 0x3A])
            if Channel_Phase==67.5:
                self.spi.xfer2([ADDR, I, 0x2C])
                self.spi.xfer2([ADDR, Q, 0x3B])
            if Channel_Phase==70.3125:
                self.spi.xfer2([ADDR, I, 0x2B])
                self.spi.xfer2([ADDR, Q, 0x3C])
            if Channel_Phase==73.125:
                self.spi.xfer2([ADDR, I, 0x2A])
                self.spi.xfer2([ADDR, Q, 0x3C])
            if Channel_Phase==75.9375:
                self.spi.xfer2([ADDR, I, 0x28])
                self.spi.xfer2([ADDR, Q, 0x3C])
            if Channel_Phase==78.75:
                self.spi.xfer2([ADDR, I, 0x27])
                self.spi.xfer2([ADDR, Q, 0x3D])
            if Channel_Phase==81.5625:
                self.spi.xfer2([ADDR, I, 0x25])
                self.spi.xfer2([ADDR, Q, 0x3D])
            if Channel_Phase==84.375:
                self.spi.xfer2([ADDR, I, 0x24])
                self.spi.xfer2([ADDR, Q, 0x3D])
            if Channel_Phase==87.1875:
                self.spi.xfer2([ADDR, I, 0x22])
                self.spi.xfer2([ADDR, Q, 0x3D])
                
        # Quadrant 2
            if Channel_Phase==90:
                self.spi.xfer2([ADDR, I, 0x21])
                self.spi.xfer2([ADDR, Q, 0x3D])
            if Channel_Phase==92.8125:
                self.spi.xfer2([ADDR, I, 0x01])
                self.spi.xfer2([ADDR, Q, 0x3D])
            if Channel_Phase==95.625:
                self.spi.xfer2([ADDR, I, 0x03])
                self.spi.xfer2([ADDR, Q, 0x3D])
            if Channel_Phase==98.4375:
                self.spi.xfer2([ADDR, I, 0x04])
                self.spi.xfer2([ADDR, Q, 0x3D])
            if Channel_Phase==101.25:
                self.spi.xfer2([ADDR, I, 0x06])
                self.spi.xfer2([ADDR, Q, 0x3D])
            if Channel_Phase==104.0625:
                self.spi.xfer2([ADDR, I, 0x07])
                self.spi.xfer2([ADDR, Q, 0x3C])
            if Channel_Phase==106.875:
                self.spi.xfer2([ADDR, I, 0x08])
                self.spi.xfer2([ADDR, Q, 0x3C])
            if Channel_Phase==109.6875:
                self.spi.xfer2([ADDR, I, 0x0A])
                self.spi.xfer2([ADDR, Q, 0x3C])
            if Channel_Phase==112.5:
                self.spi.xfer2([ADDR, I, 0x0B])
                self.spi.xfer2([ADDR, Q, 0x3B])
            if Channel_Phase==115.3125:
                self.spi.xfer2([ADDR, I, 0x0D])
                self.spi.xfer2([ADDR, Q, 0x3A])
            if Channel_Phase==118.125:
                self.spi.xfer2([ADDR, I, 0x0E])
                self.spi.xfer2([ADDR, Q, 0x3A])
            if Channel_Phase==120.9375:
                self.spi.xfer2([ADDR, I, 0x0F])
                self.spi.xfer2([ADDR, Q, 0x39])
            if Channel_Phase==123.75:
                self.spi.xfer2([ADDR, I, 0x11])
                self.spi.xfer2([ADDR, Q, 0x38])
            if Channel_Phase==126.5625:
                self.spi.xfer2([ADDR, I, 0x12])
                self.spi.xfer2([ADDR, Q, 0x38])
            if Channel_Phase==129.375:
                self.spi.xfer2([ADDR, I, 0x13])
                self.spi.xfer2([ADDR, Q, 0x37])
            if Channel_Phase==132.1875:
                self.spi.xfer2([ADDR, I, 0x14])
                self.spi.xfer2([ADDR, Q, 0x36])
            if Channel_Phase==135:
                self.spi.xfer2([ADDR, I, 0x16])
                self.spi.xfer2([ADDR, Q, 0x35])
            if Channel_Phase==137.8125:
                self.spi.xfer2([ADDR, I, 0x17])
                self.spi.xfer2([ADDR, Q, 0x34])
            if Channel_Phase==140.625:
                self.spi.xfer2([ADDR, I, 0x18])
                self.spi.xfer2([ADDR, Q, 0x33])
            if Channel_Phase==143.4375:
                self.spi.xfer2([ADDR, I, 0x19])
                self.spi.xfer2([ADDR, Q, 0x31])
            if Channel_Phase==146.25:
                self.spi.xfer2([ADDR, I, 0x19])
                self.spi.xfer2([ADDR, Q, 0x30])
            if Channel_Phase==149.0625:
                self.spi.xfer2([ADDR, I, 0x1A])
                self.spi.xfer2([ADDR, Q, 0x2F])
            if Channel_Phase==151.875:
                self.spi.xfer2([ADDR, I, 0x1B])
                self.spi.xfer2([ADDR, Q, 0x2E])
            if Channel_Phase==154.6875:
                self.spi.xfer2([ADDR, I, 0x1C])
                self.spi.xfer2([ADDR, Q, 0x2D])
            if Channel_Phase==157.5:
                self.spi.xfer2([ADDR, I, 0x1C])
                self.spi.xfer2([ADDR, Q, 0x2B])
            if Channel_Phase==160.3125:
                self.spi.xfer2([ADDR, I, 0x1D])
                self.spi.xfer2([ADDR, Q, 0x2A])
            if Channel_Phase==163.125:
                self.spi.xfer2([ADDR, I, 0X1E])
                self.spi.xfer2([ADDR, Q, 0x28])
            if Channel_Phase==165.9375:
                self.spi.xfer2([ADDR, I, 0x1E])
                self.spi.xfer2([ADDR, Q, 0x27])
            if Channel_Phase==168.75:
                self.spi.xfer2([ADDR, I, 0x1E])
                self.spi.xfer2([ADDR, Q, 0x26])
            if Channel_Phase==171.5625:
                self.spi.xfer2([ADDR, I, 0x1F])
                self.spi.xfer2([ADDR, Q, 0x24])
            if Channel_Phase==174.375:
                self.spi.xfer2([ADDR, I, 0x1F])
                self.spi.xfer2([ADDR, Q, 0x23])
            if Channel_Phase==177.1875:
                self.spi.xfer2([ADDR, I, 0x1F])
                self.spi.xfer2([ADDR, Q, 0x21])
                
        # Quadrant 3
            if Channel_Phase==180:
                self.spi.xfer2([ADDR, I, 0x1F])
                self.spi.xfer2([ADDR, Q, 0x20])
            if Channel_Phase==182.8125:
                self.spi.xfer2([ADDR, I, 0x1F])
                self.spi.xfer2([ADDR, Q, 0x20])
            if Channel_Phase==185.625:
                self.spi.xfer2([ADDR, I, 0x1F])
                self.spi.xfer2([ADDR, Q, 0x03])
            if Channel_Phase==188.4375:
                self.spi.xfer2([ADDR, I, 0x1F])
                self.spi.xfer2([ADDR, Q, 0x04])
            if Channel_Phase==191.25:
                self.spi.xfer2([ADDR, I, 0x1F])
                self.spi.xfer2([ADDR, Q, 0x06])
            if Channel_Phase==194.0625:
                self.spi.xfer2([ADDR, I, 0x1E])
                self.spi.xfer2([ADDR, Q, 0x07])
            if Channel_Phase==196.875:
                self.spi.xfer2([ADDR, I, 0x1E])
                self.spi.xfer2([ADDR, Q, 0x08])
            if Channel_Phase==199.6875:
                self.spi.xfer2([ADDR, I, 0x1D])
                self.spi.xfer2([ADDR, Q, 0x0A])
            if Channel_Phase==202.5:
                self.spi.xfer2([ADDR, I, 0x1D])
                self.spi.xfer2([ADDR, Q, 0x0B])
            if Channel_Phase==205.3125:
                self.spi.xfer2([ADDR, I, 0x1C])
                self.spi.xfer2([ADDR, Q, 0x0D])
            if Channel_Phase==208.125:
                self.spi.xfer2([ADDR, I, 0x1C])
                self.spi.xfer2([ADDR, Q, 0x0E])
            if Channel_Phase==210.9375:
                self.spi.xfer2([ADDR, I, 0x1B])
                self.spi.xfer2([ADDR, Q, 0x0F])
            if Channel_Phase==213.75:
                self.spi.xfer2([ADDR, I, 0x1A])
                self.spi.xfer2([ADDR, Q, 0x10])
            if Channel_Phase==216.5625:
                self.spi.xfer2([ADDR, I, 0x19])
                self.spi.xfer2([ADDR, Q, 0x11])
            if Channel_Phase==219.375:
                self.spi.xfer2([ADDR, I, 0x18])
                self.spi.xfer2([ADDR, Q, 0x13])
            if Channel_Phase==222.1875:
                self.spi.xfer2([ADDR, I, 0x17])
                self.spi.xfer2([ADDR, Q, 0x14])
            if Channel_Phase==225:
                self.spi.xfer2([ADDR, I, 0x16])
                self.spi.xfer2([ADDR, Q, 0x15])
            if Channel_Phase==227.8125:
                self.spi.xfer2([ADDR, I, 0x15])
                self.spi.xfer2([ADDR, Q, 0x16])
            if Channel_Phase==230.625:
                self.spi.xfer2([ADDR, I, 0x14])
                self.spi.xfer2([ADDR, Q, 0x17])
            if Channel_Phase==233.4375:
                self.spi.xfer2([ADDR, I, 0x13])
                self.spi.xfer2([ADDR, Q, 0x18])
            if Channel_Phase==236.25:
                self.spi.xfer2([ADDR, I, 0x12])
                self.spi.xfer2([ADDR, Q, 0x18])
            if Channel_Phase==239.0625:
                self.spi.xfer2([ADDR, I, 0x10])
                self.spi.xfer2([ADDR, Q, 0x19])
            if Channel_Phase==241.875:
                self.spi.xfer2([ADDR, I, 0x0F])
                self.spi.xfer2([ADDR, Q, 0x1A])
            if Channel_Phase==244.6875:
                self.spi.xfer2([ADDR, I, 0x0E])
                self.spi.xfer2([ADDR, Q, 0x1A])
            if Channel_Phase==247.5:
                self.spi.xfer2([ADDR, I, 0x0C])
                self.spi.xfer2([ADDR, Q, 0x1B])
            if Channel_Phase==250.3125:
                self.spi.xfer2([ADDR, I, 0x0B])
                self.spi.xfer2([ADDR, Q, 0x1C])
            if Channel_Phase==253.125:
                self.spi.xfer2([ADDR, I, 0x0A])
                self.spi.xfer2([ADDR, Q, 0x1C])
            if Channel_Phase==255.9375:
                self.spi.xfer2([ADDR, I, 0x08])
                self.spi.xfer2([ADDR, Q, 0x1C])
            if Channel_Phase==258.75:
                self.spi.xfer2([ADDR, I, 0x07])
                self.spi.xfer2([ADDR, Q, 0x1D])
            if Channel_Phase==261.5625:
                self.spi.xfer2([ADDR, I, 0x05])
                self.spi.xfer2([ADDR, Q, 0x1D])
            if Channel_Phase==264.375:
                self.spi.xfer2([ADDR, I, 0x04])
                self.spi.xfer2([ADDR, Q, 0x1D])
            if Channel_Phase==267.1875:
                self.spi.xfer2([ADDR, I, 0x02])
                self.spi.xfer2([ADDR, Q, 0x1D])
        
        # Quadrant 4
            if Channel_Phase==270:
                self.spi.xfer2([ADDR, I, 0x01])
                self.spi.xfer2([ADDR, Q, 0x1D])
            if Channel_Phase==272.8125:
                self.spi.xfer2([ADDR, I, 0x21])
                self.spi.xfer2([ADDR, Q, 0x1D])
            if Channel_Phase==275.625:
                self.spi.xfer2([ADDR, I, 0x23])
                self.spi.xfer2([ADDR, Q, 0x1D])
            if Channel_Phase==278.4375:
                self.spi.xfer2([ADDR, I, 0x24])
                self.spi.xfer2([ADDR, Q, 0x1D])
            if Channel_Phase==281.25:
                self.spi.xfer2([ADDR, I, 0x26])
                self.spi.xfer2([ADDR, Q, 0x1D])
            if Channel_Phase==284.0625:
                self.spi.xfer2([ADDR, I, 0x27])
                self.spi.xfer2([ADDR, Q, 0x1C])
            if Channel_Phase==286.875:
                self.spi.xfer2([ADDR, I, 0x28])
                self.spi.xfer2([ADDR, Q, 0x1C])
            if Channel_Phase==289.6875:
                self.spi.xfer2([ADDR, I, 0x2A])
                self.spi.xfer2([ADDR, Q, 0x1C])
            if Channel_Phase==292.5:
                self.spi.xfer2([ADDR, I, 0x2B])
                self.spi.xfer2([ADDR, Q, 0x1B])
            if Channel_Phase==295.3125:
                self.spi.xfer2([ADDR, I, 0x2D])
                self.spi.xfer2([ADDR, Q, 0x1A])
            if Channel_Phase==298.125:
                self.spi.xfer2([ADDR, I, 0x2E])
                self.spi.xfer2([ADDR, Q, 0x1A])
            if Channel_Phase==300.9375:
                self.spi.xfer2([ADDR, I, 0x2F])
                self.spi.xfer2([ADDR, Q, 0x19])
            if Channel_Phase==303.75:
                self.spi.xfer2([ADDR, I, 0x31])
                self.spi.xfer2([ADDR, Q, 0x18])
            if Channel_Phase==306.5625:
                self.spi.xfer2([ADDR, I, 0x32])
                self.spi.xfer2([ADDR, Q, 0x18])
            if Channel_Phase==309.375:
                self.spi.xfer2([ADDR, I, 0x33])
                self.spi.xfer2([ADDR, Q, 0x17])
            if Channel_Phase==312.1875:
                self.spi.xfer2([ADDR, I, 0x34])
                self.spi.xfer2([ADDR, Q, 0x16])
            if Channel_Phase==315:
                self.spi.xfer2([ADDR, I, 0x36])
                self.spi.xfer2([ADDR, Q, 0x15])
            if Channel_Phase==317.8125:
                self.spi.xfer2([ADDR, I, 0x37])
                self.spi.xfer2([ADDR, Q, 0x14])
            if Channel_Phase==320.625:
                self.spi.xfer2([ADDR, I, 0x38])
                self.spi.xfer2([ADDR, Q, 0x13])
            if Channel_Phase==323.4375:
                self.spi.xfer2([ADDR, I, 0x39])
                self.spi.xfer2([ADDR, Q, 0x11])
            if Channel_Phase==326.25:
                self.spi.xfer2([ADDR, I, 0x39])
                self.spi.xfer2([ADDR, Q, 0x10])
            if Channel_Phase==329.0625:
                self.spi.xfer2([ADDR, I, 0x3A])
                self.spi.xfer2([ADDR, Q, 0x0F])
            if Channel_Phase==331.875:
                self.spi.xfer2([ADDR, I, 0x3B])
                self.spi.xfer2([ADDR, Q, 0x0E])
            if Channel_Phase==334.6875:
                self.spi.xfer2([ADDR, I, 0x3C])
                self.spi.xfer2([ADDR, Q, 0x0D])
            if Channel_Phase==337.5:
                self.spi.xfer2([ADDR, I, 0x3C])
                self.spi.xfer2([ADDR, Q, 0x0B])
            if Channel_Phase==340.3125:
                self.spi.xfer2([ADDR, I, 0x3D])
                self.spi.xfer2([ADDR, Q, 0x0A])
            if Channel_Phase==343.125:
                self.spi.xfer2([ADDR, I, 0x3E])
                self.spi.xfer2([ADDR, Q, 0x08])
            if Channel_Phase==345.9375:
                self.spi.xfer2([ADDR, I, 0x3E])
                self.spi.xfer2([ADDR, Q, 0x07])
            if Channel_Phase==348.75:
                self.spi.xfer2([ADDR, I, 0x3E])
                self.spi.xfer2([ADDR, Q, 0x06])
            if Channel_Phase==351.5625:
                self.spi.xfer2([ADDR, I, 0x3F])
                self.spi.xfer2([ADDR, Q, 0x04])
            if Channel_Phase==354.375:
                self.spi.xfer2([ADDR, I, 0x3F])
                self.spi.xfer2([ADDR, Q, 0x03])
            if Channel_Phase==357.1875:
                self.spi.xfer2([ADDR, I, 0x3F])
                self.spi.xfer2([ADDR, Q, 0x01])
                
        #print("hello " + str(self.Rx1_phase))
        #self.count=self.count+1
        self.spi.xfer2([ADDR, 0x28, 0x01])  # Loads Rx vectors from SPI.
        time.sleep(self.UpdateRate)
        output_items[0][:] = SteerAngle * (-1) + 90
        
        return len(output_items[0])
