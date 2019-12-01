#!/usr/bin/env python3
# coding: utf-8

# モジュールインポート
import spidev

# L6470パラメータリスト
class Param(object):
    """パラメータレジスタ情報を格納するクラス
    """
    def __init__(self, _addr, _mask, _rw):
        """パラメータレジスタクラスコンストラクタ
        
        Arguments:
            _addr {int} -- パラメータレジスタアドレス
            _mask {[int]} -- 書込みデータマスク
            _rw {[int]} -- 書込み可能タイミング -1:R, 0:WR, 1:WS, 2:WH
        """        
        self.addr = _addr
        self.mask = _mask
        self.rw = _rw

ABS_POS     = Param(0x01, [0x3f, 0xff, 0xff], 1)
EL_POS      = Param(0x02, [0x01, 0xff]      , 1)
MARK        = Param(0x03, [0x3f, 0xff, 0xff], 0)
SPEED       = Param(0x04, [0x0f, 0xff, 0xff],-1)
ACC         = Param(0x05, [0x0f, 0xff]      , 1)
DEC         = Param(0x06, [0x0f, 0xff]      , 1)
MAX_SPEED   = Param(0x07, [0x03, 0xff]      , 0)
MIN_SPEED   = Param(0x08, [0x1f, 0xff]      , 1)
FS_SPD      = Param(0x15, [0x03, 0xff]      , 0)
KVAL_HOLD   = Param(0x09, [0xff]            , 0)
KVAL_RUN    = Param(0x0a, [0xff]            , 0)
KVAL_ACC    = Param(0x0b, [0xff]            , 0)
KVAL_DEC    = Param(0x0c, [0xff]            , 0)
INIT_SPEED  = Param(0x0d, [0x3f, 0xff]      , 2)
ST_SLP      = Param(0x0e, [0xff]            , 2)
FN_SLP_ACC  = Param(0x0f, [0xff]            , 2)
FN_SLP_DEC  = Param(0x10, [0xff]            , 2)
K_THERM     = Param(0x11, [0x0f]            , 0)
ADC_OUT     = Param(0x12, [0x1f]            ,-1)
OCD_TH      = Param(0x13, [0x0f]            , 0)
STALL_TH    = Param(0x14, [0x7f]            , 0)
STEP_MODE   = Param(0x16, [0xff]            , 2)
ALARM_EN    = Param(0x17, [0xff]            , 1)
CONFIG      = Param(0x18, [0xff ,0xff]      , 2)
STATUS      = Param(0x19, [0xff ,0xff]      ,-1)

# L6470コマンドリスト
class Command(object):
    """コマンドレジスタ情報を格納するクラス
    """
    def __init__(self, _addr, _mask):
        """[summary]
        
        Arguments:
            _addr {int} -- コマンドアドレス
            _mask {[int]} -- コマンドデータマスク
        """
        self.addr = _addr
        self.mask = _mask

SET_PARAM   = Command(0x00, [])
GET_PARAM   = Command(0x20, [0x00, 0x00])
RUN         = Command(0x50, [0x0f, 0xff, 0xff])
STEP_CLOCK  = Command(0x58, [])
MOVE        = Command(0x40, [0x3f, 0xff, 0xff])
GO_TO       = Command(0x60, [0x3f, 0xff, 0xff])
GO_TO_DIR   = Command(0x68, [0x3f, 0xff, 0xff])
GO_UTIL     = Command(0x82, [0x0f, 0xff, 0xff])
RELEASE_SW  = Command(0x92, [])
GO_HOME     = Command(0x70, [])
GO_MARK     = Command(0x78, [])
RESET_POS   = Command(0xd8, [])
RESET_DEVICE= Command(0xc0, [])
SOFT_STOP   = Command(0xb0, [])
HARD_STOP   = Command(0xb8, [])
SOFT_HIZ    = Command(0xa0, [])
HARD_HIZ    = Command(0xa8, [])
GET_STATUS  = Command(0xd0, [0x00, 0x00])


class Device:
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
        
        self.param = {
            'ABS_POS'
        }

        # ステータス情報の初期化
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

        # 起動時ステータスに更新
        self.updateStatus()

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
        if(type(param) is not Param
            or type(values) is not list):

            err  = '"setParam()"関数の引数不一致\n'
            err += '   setParam(param, values)\n'
            err += '      param : (int, [int], int) ex.(0x12, [0xff], 0)\n'
            err += '      values: [int] ex.[0x12, 0xab]\n'

            raise RuntimeError(err)

        # パラメータサイズを確認する
        i = 0
        for mask in param.mask:
            if (~mask & values[i]) > 0:      

                err  = '"SET_PARAM"コマンドが要求している値サイズと不一致\n'
                err += '  指定レジスタ     : {}\n'.format(hex(param[0]))
                err += '  レジスタ要求サイズ: {}\n'.format([bin(j) for j in param.mask])
                err += '  値サイズ　　　　　: {}\n'.format([bin(j) for j in values])

                raise RuntimeError(err)

            i += 1

        self.command(param.addr, values)

    def getParam(self, param):
        """パラメータレジスタから値を取得する
        
        Arguments:
            param {(int, int)} -- パラメータ情報 ex.(レジスタアドレス, サイズ) = (0x12, 3)
        
        Returns:
            [int] -- パレメータレジスタ値 ex.[0x12, 0xab]
        """

        # 引数の型を確認する
        if(type(param) is not Param):

            err  = '"getParam()"関数の引数不一致\n'
            err += '   setParam(param, values)\n'
            err += '      param : (int, int) ex.(0x12, 2)\n'            

            raise RuntimeError(err)


        reg = GET_PARAM.addr | param.addr

        return self.command(reg, [0x00]*len(param.mask))

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

        # 速度パラメータサイズを確認する
        i = 0
        for mask in RUN.mask:
            if (~mask & speed[i]) > 0:      

                err  = '"RUN"コマンドが要求している値サイズと不一致\n'
                err += '  指定レジスタ     : {}\n'.format(hex(RUN.addr))
                err += '  レジスタ要求サイズ: {}\n'.format([bin(j) for j in RUN.mask])
                err += '  値サイズ　　　　　: {}\n'.format([bin(j) for j in speed])

                raise RuntimeError(err)

            i += 1

        # "RUN"コマンドに方向ビットを適用する
        reg = RUN.addr
        if not dir:
            reg = 0x01 | reg

        self.command(reg, speed)

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
        self.command(GO_HOME.addr)

    def goMark(self):
        """GO_MARKコマンドを実行する
        """
        self.command(GO_MARK.addr)

    def resetPos(self):
        """RESET_POSコマンドを実行する
        """
        self.command(RESET_POS.addr)

    def resetDevice(self):
        """RESET_DEVICEコマンドを実行する
        """
        self.command(RESET_DEVICE.addr)

    def softStop(self):
        """SOFT_STOPコマンドを実行する
        """
        self.command(SOFT_STOP.addr)

    def hardStop(self):
        """HARD_STOPコマンドを実行する
        """
        self.command(HARD_STOP.addr)

    def softHiz(self):
        """SOFT_HIZコマンドを実行する
        """
        self.command(SOFT_HIZ.addr)

    def hardHiz(self):
        """HARD_HIZコマンドを実行する
        """
        self.command(HARD_HIZ.addr)

    def getStatus(self):
        """ステータスレジスタの値を取得する
        
        Returns:
            [int] -- ステータスレジスタ値
        """
        return self.command(GET_STATUS.addr, GET_STATUS.mask)


    def command(self, cmd, values=[]):
        """コマンド実行を行う
        
        Arguments:
            cmd {int} -- コマンド値 ex.0xab
        
        Keyword Arguments:            
            values {[int]} -- パラメータ値 ex.[0x12, 0xab] (default: {None})
        
        Returns:
            [int] -- コマンド実行の返り値 ex.[0x00, 0x00]
        """

        # 引数の型を確認する
        if(type(cmd) is not int           
            or type(values) is not list):

            err  = '"command"関数の引数不一致\n'
            err += '   command(cmd, size, values)\n'
            err += '      cmd   : int   (ex. 0x70)\n'            
            err += '      values: [int] (ex. [0x00, 0x0d])\n'

            raise RuntimeError(err)

        # 送信データの先頭にコマンド値を設定する
        to_send = [cmd]

        # 送信データにコマンド値の後に続くデータを連結する
        if(len(values) > 0):
            to_send += values

        from_recv = []        

        for value in to_send:
            from_recv += self.spi.xfer([value])        

        return from_recv[1:]


if __name__ == '__main__':
    pass