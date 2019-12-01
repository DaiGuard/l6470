# L6470

Python library for coontrolling STMicroelectronics L6470 using SPI.

## Install

Clone **l6470** repogitory local from github.

```
$ git clone https://github.com/DaiGuard/l6470
```

Install using setuptools.

```
$ cd l6470
$ sudo python3 setup.py install
```

## Demo Hardware

This demonstration is performed using [**JetsonNano (Nvidia)**](https://developer.nvidia.com/embedded/jetson-nano-developer-kit) and [**AE-L6470DRV (Akizukidenshi)**](http://akizukidenshi.com/catalog/g/gK-07024/).  
and the motor uses [**P-PMSA-B60D3 (Plexmotion)**](http://www.plexmotion.com/products/detail.php?q=P-PMSA-B60D3).

![](https://user-images.githubusercontent.com/26181834/69914558-12667100-1489-11ea-8e1e-1d98323d2cdb.jpg)

The pin assignment is show in the table.

| Jetson Nano | | AE-L6470DRV |
| --- | -- | --- |
| Pin 19 (SPI_MOSI) | --> | CN4-7 (SDI) |
| Pin 21 (SPI_MISO) | <-- | CN4-5 (SDO) |
| Pin 23 (SPI1_SCK) | --> | CN4-6 (CK) |
| Pin 24 (SPI1_CS0) | --> | CN4-8 (#CS) |
| Pin 25 (GND) | <-> | CN4-3 (GND) |

## Usage

Sample code ```tests/sample_l6470.py```

``` python
# coding: utf-8

# import l6470 module
from l6470 import l6470

import time

if __name__ == '__main__':

    device = None

    try:
        # open spi device bus:0, client0
        device = l6470.Device(0, 0)

        # reset L6470 
        device.resetDevice()

        # parameter value setting
        device.setParam(l6470.MAX_SPEED, [0x10, 0x00])
        device.setParam(l6470.STEP_MODE, [0x03])
        device.setParam(l6470.KVAL_HOLD, [0x39])
        device.setParam(l6470.KVAL_RUN,  [0x39])
        device.setParam(l6470.KVAL_ACC,  [0x39])
        device.setParam(l6470.KVAL_DEC,  [0x39])

        # exec "run" command
        device.run(True, [0x00, 0x10, 0x00])

        for i in range(5):

            time.sleep(1)

            # get device status
            status = device.updateStatus()
            print(status)

    except KeyboardInterrupt:
        pass
    finally:
        if device is not None:
            # exec "soft_stop" command
            device.softStop()
```

Run the sample with the following command

```
$ cd l6470/tests
$ python3 sample_l6470.py
```