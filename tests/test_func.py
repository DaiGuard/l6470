import pytest

from l6470 import l6470

import time
import sys
import traceback


class TestClass(object):

    @classmethod
    def setup_class(self):
        self.device = l6470.Device(0, 0)

        self.device.resetDevice()

    @classmethod
    def teardown_class(self):
        pass

    def test_getStatus(self):
        try:
            status = self.device.getStatus()

            print('STATUS={}'.format([hex(i) for i in status]))

            assert True

        except Exception as e:
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))

            assert False

    def test_set_get_Param(self):
        try:            
            # ABS_POS
            send = l6470.ABS_POS.mask
            recv = []
            self.device.setParam(l6470.ABS_POS, send)
            recv = self.device.getParam(l6470.ABS_POS)            
            assert send == recv

            # EL_POS
            send = l6470.EL_POS.mask
            recv = []
            self.device.setParam(l6470.EL_POS, send)
            recv = self.device.getParam(l6470.EL_POS)
            assert send == recv

            # MARK
            send = l6470.MARK.mask
            recv = []
            self.device.setParam(l6470.MARK, send)
            recv = self.device.getParam(l6470.MARK)
            assert send == recv

            # ACC
            send = l6470.ACC.mask
            recv = []
            self.device.setParam(l6470.ACC, send)
            recv = self.device.getParam(l6470.ACC)
            assert send == recv

            # DEC
            send = l6470.DEC.mask
            recv = []
            self.device.setParam(l6470.DEC, send)
            recv = self.device.getParam(l6470.DEC)
            assert send == recv

            # MAX_SPEED
            send = l6470.MAX_SPEED.mask
            recv = []
            self.device.setParam(l6470.MAX_SPEED, send)
            recv = self.device.getParam(l6470.MAX_SPEED)
            assert send == recv

            # MIN_SPEED
            send = l6470.MIN_SPEED.mask
            recv = []
            self.device.setParam(l6470.MIN_SPEED, send)
            recv = self.device.getParam(l6470.MIN_SPEED)
            assert send == recv

            # FS_SPD
            send = l6470.FS_SPD.mask
            recv = []
            self.device.setParam(l6470.FS_SPD, send)
            recv = self.device.getParam(l6470.FS_SPD)
            assert send == recv

            # KVAL_HOLD
            send = l6470.KVAL_HOLD.mask
            recv = []
            self.device.setParam(l6470.KVAL_HOLD, send)
            recv = self.device.getParam(l6470.KVAL_HOLD)
            assert send == recv

            # KVAL_RUN
            send = l6470.KVAL_RUN.mask
            recv = []
            self.device.setParam(l6470.KVAL_RUN, send)
            recv = self.device.getParam(l6470.KVAL_RUN)
            assert send == recv

            # KVAL_ACC
            send = l6470.KVAL_ACC.mask
            recv = []
            self.device.setParam(l6470.KVAL_ACC, send)
            recv = self.device.getParam(l6470.KVAL_ACC)
            assert send == recv

            # KVAL_DEC
            send = l6470.KVAL_DEC.mask
            recv = []
            self.device.setParam(l6470.KVAL_DEC, send)
            recv = self.device.getParam(l6470.KVAL_DEC)
            assert send == recv

            # INIT_SPEED
            send = l6470.INIT_SPEED.mask
            recv = []
            self.device.setParam(l6470.INIT_SPEED, send)
            recv = self.device.getParam(l6470.INIT_SPEED)
            assert send == recv

            # ST_SLP
            send = l6470.ST_SLP.mask
            recv = []
            self.device.setParam(l6470.ST_SLP, send)
            recv = self.device.getParam(l6470.ST_SLP)
            assert send == recv

            # FN_SLP_ACC
            send = l6470.FN_SLP_ACC.mask
            recv = []
            self.device.setParam(l6470.FN_SLP_ACC, send)
            recv = self.device.getParam(l6470.FN_SLP_ACC)
            assert send == recv

            # FN_SLP_DEC
            send = l6470.FN_SLP_DEC.mask
            recv = []
            self.device.setParam(l6470.FN_SLP_DEC, send)
            recv = self.device.getParam(l6470.FN_SLP_DEC)
            assert send == recv

            # K_THERM
            send = l6470.K_THERM.mask
            recv = []
            self.device.setParam(l6470.K_THERM, send)
            recv = self.device.getParam(l6470.K_THERM)
            assert send == recv

            # OCD_TH
            send = l6470.OCD_TH.mask
            recv = []
            self.device.setParam(l6470.OCD_TH, send)
            recv = self.device.getParam(l6470.OCD_TH)
            assert send == recv

            # STALL_TH
            send = l6470.STALL_TH.mask
            recv = []
            self.device.setParam(l6470.STALL_TH, send)
            recv = self.device.getParam(l6470.STALL_TH)
            assert send == recv

            # STEP_MODE
            send = l6470.STEP_MODE.mask
            recv = []
            self.device.setParam(l6470.STEP_MODE, send)
            recv = self.device.getParam(l6470.STEP_MODE)
            assert send == recv

            # ALARM_EN
            send = l6470.ALARM_EN.mask
            recv = []
            self.device.setParam(l6470.ALARM_EN, send)
            recv = self.device.getParam(l6470.ALARM_EN)
            assert send == recv

        except Exception as e:
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))

            assert False

    def test_run(self):
        try:
            self.device.resetDevice()
            self.device.setParam(l6470.MAX_SPEED, [0x03, 0xff])
            self.device.setParam(l6470.MIN_SPEED, [0x00, 0x00])
            self.device.setParam(l6470.INIT_SPEED, [0x00, 0x00])
            self.device.setParam(l6470.KVAL_HOLD, [0x39])
            self.device.setParam(l6470.KVAL_RUN, [0x39])
            self.device.setParam(l6470.KVAL_ACC, [0x39])
            self.device.setParam(l6470.KVAL_DEC, [0x39])
            self.device.setParam(l6470.STEP_MODE, [0x07])

            self.device.run(True, [0x00, 0x3f, 0xff])
            
            time.sleep(5)                
            status = self.device.updateStatus()

            assert status['BUSY'] == 0b1
            assert status['DIR'] == 0b0
            assert status['MOT_STATUS'] == 0b11

            speed = self.device.getParam(l6470.SPEED)
            assert speed == [0x00, 0x3f, 0xff]

            self.device.softStop()

        except Exception as e:
            t, v, tb = sys.exc_info()
            print(traceback.format_exception(t,v,tb))
            print(traceback.format_tb(e.__traceback__))

            assert False
