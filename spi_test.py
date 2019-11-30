#!/usr/bin/env python
# coding: utf-8

# モジュールインポート
import spidev
from enum import Enum

# L6470パラメータリスト
ABS_POS     = (0x01, 3)
EL_POS      = (0x02, 2)
MARK        = (0x03, 3)
SPEED       = (0x04, 3)
ACC         = (0x05, 2)
DEC         = (0x06, 2)
MAX_SPEED   = (0x07, 2)
MIN_SPEED   = (0x08, 2)
FS_SPD      = (0x15, 2)
KVAL_HOLD   = (0x09, 1)
KVAL_RUN    = (0x0a, 1)
KVAL_ACC    = (0x0b, 1)
KVAL_DEC    = (0x0c, 1)
INIT_SPEED  = (0x0d, 2)
ST_SLP      = (0x0e, 1)
FN_SLP_ACC  = (0x0f, 1)
FN_SLP_DEC  = (0x10, 1)
K_THERM     = (0x11, 1)
ADC_OUT     = (0x12, 1)
OCD_TH      = (0x13, 1)
STALL_TH    = (0x14, 1)
STEP_MODE   = (0x16, 1)
ALARM_EN    = (0x17, 1)
CONFIG      = (0x18, 2)
STATUS      = (0x19, 2)

# L6470コマンドリスト
SET_PARAM   = (0x00,-1)
GET_PARAM   = (0x20,-1)
RUN         = (0x50, 3)
STEP_CLOCK  = (0x58, 0)
MOVE        = (0x40, 3)
GO_TO       = (0x60, 3)
GO_TO_DIR   = (0x68, 3)
GO_UTIL     = (0x82, 3)
RELEASE_SW  = (0x92, 0)
GO_HOME     = (0x70, 0)
GO_MARK     = (0x78, 0)
RESET_POS   = (0xd8, 0)
RESET_DEVICE= (0xc0, 0)
SOFT_STOP   = (0xb0, 0)
HARD_STOP   = (0xb8, 0)
SOFT_HIZ    = (0xa0, 0)
HARD_HIZ    = (0xa8, 0)
GET_STATUS  = (0xd0, 2)


class L6470:
    """
    L6470コントロールクラス
    """
    
    def __init__(self, bus, client):        
        """L6470コンストラクタ
        
        Arguments:
            bus {int} -- SPIバスID
            client {int} -- SPIチップセレクトID
        """
        # SPIデバイス情報の設定
        self.devInfo = {'bus':0, 'client':0}
        self.devInfo['bus'] = bus
        self.devInfo['client'] =client

        # SPIデバイスの初期化
        self.spi = spidev.SpiDev(bus, client)
        self.spi.max_speed_hz = 5000
        self.spi.mode = 0b00        
        
        self.status = {
            'HiZ': 0b0,
            'BUSY': 0b0,
            'SW_F': 0b0,
            'SW_EVN': 0b00,
            'DIR': 0b0,
            'MOT_STATUS': 0b00,
            'NOTPERF_CMD': 0b0,
            'WRONG_CMD': 0b0,
            'UVLO': 0b0,
            'TH_WRN': 0b0,
            'TH_SD': 0b0,
            'OCD': 0b0,
            'STEP_LOSS_A': 0b0,
            'STEP_LOSS_B': 0b0,
            'SCK_MOD': 0b0
        }

        print('SPI.{}.{}を開きます'.format(bus, client))


    def __del__(self):
        """L6470デストラクタ
        """

        if(self.spi is not None):
            self.spi.close()

        print('SPI.{}.{}を閉じます'.format(self.devInfo['bus'], self.devInfo['client']))

    # === ハイレベル API ===
    def updateStatus(self):
        """ステータス情報の更新
        """
        status = self.getStatus()        

        # HiZ: 
        self.status['HiZ']        = (0x01 & status[1])
        # BUSY: 
        self.status['BUSY']       = (0x02 & status[1]) >> 1
        # SW_F: 
        self.status['SW_F']       = (0x04 & status[1]) >> 2
        # SW_ENV: 
        self.status['SW_ENV']     = (0x08 & status[1]) >> 3
        # DIR: 
        self.status['DIR']        = (0x10 & status[1]) >> 4        
        # MOT_STATUS: モータ制御状態ビット
        #   0b00: STOPPED, 0b01: ACC, 0b10: DEC, 0b11: CONST
        self.status['MOT_STATUS'] = (0x60 & status[1]) >> 5
        # NOTPERF_CMD: 
        self.status['NOTPERF_CMD']= (0x80 & status[1]) >> 7
        # WRONG_CMD: 
        self.status['WRONG_CMD']  = (0x01 & status[0])
        # UVLO: 低電圧状態ビット
        self.status['UVLO']       = (0x02 & status[0]) >> 1
        # TH_WRN:
        self.status['TH_WRN']     = (0x04 & status[0]) >> 2
        # TH_SD: 
        self.status['TH_SD']      = (0x80 & status[0]) >> 3
        # OCD
        self.status['OCD']        = (0x10 & status[0]) >> 4
        # STEP_LOSS_A: 
        self.status['STEP_LOSS_A']= (0x20 & status[0]) >> 5
        # STEP_LOSS_B:
        self.status['STEP_LOSS_B']= (0x40 & status[0]) >> 6
        # SCK_MOD: 
        self.status['SCK_MOD']    = (0x80 & status[0]) >> 7

        return self.status

    # === ローレベル API ===
    def setParam(self, param, values):
        """パラメータレジスタに値を設定する
        
        Arguments:
            param {(int, int)} -- パラメータ情報 ex.(レジスタアドレス, サイズ) = (0x12, 3)
            values {[int]} -- パレメータ値 ex.[0x12, 0xab]
        """

        # 引数の型を確認する
        if(type(param) is not tuple
            or type(values) is not list):

            err  = '"setParam()"関数の引数不一致\n'
            err += '   setParam(param, values)\n'
            err += '      param : (int, int) ex.(0x12, 2)\n'
            err += '      values: [int] ex.[0x12, 0xab]\n'

            raise RuntimeError(err)

        # パラメータサイズを確認する
        if param[1] != len(values):

            err  = '"SET_PARAM"コマンドが要求している値サイズと不一致\n'
            err += '  指定レジスタ     : {}\n'.format(param[0])
            err += '  レジスタ要求サイズ: {}\n'.format(param[1])
            err += '  値サイズ　　　　　: {}\n'.format(len(values))

            raise RuntimeError(err)

        self.command(param[0], len(values), values)

    def getParam(self, param):
        """パラメータレジスタから値を取得する
        
        Arguments:
            param {(int, int)} -- パラメータ情報 ex.(レジスタアドレス, サイズ) = (0x12, 3)
        
        Returns:
            [int] -- パレメータレジスタ値 ex.[0x12, 0xab]
        """

        # 引数の型を確認する
        if(type(param) is not tuple):

            err  = '"getParam()"関数の引数不一致\n'
            err += '   setParam(param, values)\n'
            err += '      param : (int, int) ex.(0x12, 2)\n'            

            raise RuntimeError(err)


        reg = GET_PARAM[0] | param[0]

        return self.command(reg, param[1])

    def run(self, dir, speed):
        """RUNコマンドを実行する
        
        Arguments:
            dir {bool} -- 方向 True:CW, False:CCW
            speed {[int]} -- 速度 ex.[0x12, 0xab]
        """

        # 引数の型を確認する
        if(type(dir) is not bool
            or type(speed) is not list):

            err  = '"run()"関数の引数不一致\n'
            err += '   run(dir, speed)\n'
            err += '      dir  : bool\n'
            err += '      speed: [int]'

            raise RuntimeError(err)

        # 速度のリストサイズを確認する
        if(RUN[1] != len(speed)):
            
            err  = '"RUN"コマンドの速度データサイズ不一致\n'
            err += '   要求サイズ  : {}\n'.format(RUN[1])
            err += '   データサイズ: {}\n'.format(len(speed))

            raise RuntimeError(err)

        # "RUN"コマンドに方向ビットを適用する
        reg = RUN[0]        
        if not dir:
            reg = 0x01 | reg

        self.command(reg, RUN[1], speed)

    def stepClock(self, dir):
        pass

    def move(self, dir, n_step):
        pass

    def goTo(self, abs_pos):
        pass

    def goToDir(self, dir, abs_pos):
        pass

    def goUntil(self, act, dir, speed):
        pass

    def releaseSW(self, act, dir):
        pass

    def goHome(self):
        """GO_HOMEコマンドを実行する
        """
        self.command(GO_HOME[0])

    def goMark(self):
        """GO_MARKコマンドを実行する
        """
        self.command(GO_MARK[0])

    def resetPos(self):
        """RESET_POSコマンドを実行する
        """
        self.command(RESET_POS[0])

    def resetDevice(self):
        """RESET_DEVICEコマンドを実行する
        """
        self.command(RESET_DEVICE[0])

    def softStop(self):
        """SOFT_STOPコマンドを実行する
        """
        self.command(SOFT_STOP[0])

    def hardStop(self):
        """HARD_STOPコマンドを実行する
        """
        self.command(HARD_STOP[0])

    def softHiz(self):
        """SOFT_HIZコマンドを実行する
        """
        self.command(SOFT_HIZ[0])

    def hardHiz(self):
        """HARD_HIZコマンドを実行する
        """
        self.command(HARD_HIZ[0])

    def getStatus(self):
        """ステータスレジスタの値を取得する
        
        Returns:
            [int] -- ステータスレジスタ値
        """
        return self.command(GET_STATUS[0], GET_STATUS[1])


    def command(self, cmd, size=0, values=None):
        """コマンド実行を行う
        
        Arguments:
            cmd {int} -- コマンド値 ex.0xab
        
        Keyword Arguments:
            size {int} -- パラメータ値のリストサイズ (default: {0})
            values {[int]} -- パラメータ値 ex.[0x12, 0xab] (default: {None})
        
        Returns:
            [int] -- コマンド実行の返り値 ex.[0x00, 0x00]
        """

        # 引数の型を確認する
        if(type(cmd) is not int
            or type(size) is not int
            or (values is not None and type(values) is not list)):

            err  = '"command"関数の引数不一致\n'
            err += '   command(cmd, size, values)\n'
            err += '      cmd   : int   (ex. 0x70)\n'
            err += '      size  : int   (ex. 2)\n'
            err += '      values: [int] (ex. [0x00, 0x0d])\n'

            raise RuntimeError(err)

        # 送信データの先頭にコマンド値を設定する
        to_send = [cmd]

        # 送信データにコマンド値の後に続くデータを連結する
        if(values is None):
            nop = []
            for i in range(size):
                nop.append(0x00)
            to_send += nop
        else:
            to_send += values[0:size]

        from_recv = []        

        for value in to_send:
            from_recv += self.spi.xfer([value])        

        return from_recv[1:]


if __name__ == '__main__':
    pass