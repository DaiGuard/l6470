#!/usr/bin/env python3
# coding: utf-8

from l6470 import l6470

import time
import sys
import traceback


if __name__ == '__main__':

    device = None

    try:
        # open spi device bus:0, client0
        device = l6470.Device(0, 0)

        # reset L6470 
        device.resetDevice()

        # parameter value setting
        device.setParam(l6470.MAX_SPEED, [0x01, 0x80])        
        device.setParam(l6470.STEP_MODE, [0x07])
        device.setParam(l6470.KVAL_HOLD, [0x39])
        device.setParam(l6470.KVAL_RUN,  [0x39])
        device.setParam(l6470.KVAL_ACC,  [0x39])
        device.setParam(l6470.KVAL_DEC,  [0x39])

        # exec "run" command
        device.stepClock(True)

        for i in range(5):

            time.sleep(1)

            # get device status
            status = device.updateStatus()
            print(status)

    except Exception as e:
        t, v, tb = sys.exc_info()
        print(traceback.format_exception(t,v,tb))
        print(traceback.format_tb(e.__traceback__))
    except KeyboardInterrupt:
        pass
    finally:
        if device is not None:
            # exec "soft_stop" command
            device.softStop()