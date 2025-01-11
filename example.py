import time
import machine
import lvgl as lv
import lvgl_esp32
from machine import ADC, Pin, PWM, I2C, SoftI2C
import time
from audio import player, recorder
import sys
import os

##############挂载SD卡##############
import vfs
sdcard = machine.SDCard(clk=15, cmd=7, d0=4)
vfs.mount(sdcard, '/sdcard')
print(os.listdir('/sdcard'))
sys.path.append('/sdcard')
#print("sys.path:",sys.path)

##############TCA9554(io expander)##############
# 定义寄存器地址
INPUT_PORT_REG = 0x0
OUTPUT_PORT_REG = 0x1
POLARITY_INVERSION_REG = 0x2
CONFIG_REG = 0x3

class TCA9554:
    def __init__(self, i2c: I2C, address: int):
        self.i2c = i2c
        self.address = address

    def pin_set_mode(self, pin: int, mode: bool) -> int:
        """
        设置引脚模式 (INPUT/OUTPUT)
        :param pin: 引脚号 (0-7)
        :param mode: 模式 (True 为 INPUT, False 为 OUTPUT)
        """
        config_reg = self.i2c.readfrom_mem(self.address, CONFIG_REG, 1)[0]
        if mode:  # INPUT
            config_reg |= (1 << pin)
        else:  # OUTPUT
            config_reg &= ~(1 << pin)
        self.i2c.writeto_mem(self.address, CONFIG_REG, bytes([config_reg]))

    def digital_write(self, pin: int, state: bool) -> int:
        """
        设置引脚电平 (HIGH/LOW)
        :param pin: 引脚号 (0-7)
        :param state: 状态 (True 为 HIGH, False 为 LOW)
        """
        output_reg = self.i2c.readfrom_mem(self.address, OUTPUT_PORT_REG, 1)[0]
        if state:  # HIGH
            output_reg |= (1 << pin)
        else:  # LOW
            output_reg &= ~(1 << pin)
        self.i2c.writeto_mem(self.address, OUTPUT_PORT_REG, bytes([output_reg]))

    def digital_read(self, pin: int) -> int:
        """
        读取引脚状态
        :param pin: 引脚号 (0-7)
        :return: 1 为 HIGH, 0 为 LOW, -1 为失败
        """
        input_reg = self.i2c.readfrom_mem(self.address, INPUT_PORT_REG, 1)[0]
        return 1 if input_reg & (1 << pin) else 0

# import i2c
# import time
# i2c_bus = i2c.I2C.Bus(host=1, scl=7, sda=15)
# print(i2c_bus.scan())
# expander = TCA9554(i2c_bus, 0x20)
# expander.pin_set_mode(4, 0) # 设置引脚5为输出
# while 1:
#     time.sleep(0.002)
#     expander.digital_write(4, 0)  # 将引脚5设置为低电平
#     time.sleep(0.001)
#     expander.digital_write(4, 1)  # 将引脚5设置为高电平
##############TCA9554 END##############

#tca9554的处理
i2c = SoftI2C(scl=Pin(18), sda=Pin(17), freq=100000)
print("i2c列表:",i2c.scan())
expander = TCA9554(i2c, 56) #0x38 OK)
expander.pin_set_mode(1, 0) #False 为 OUTPUT) LCD_CTRL_GPIO
expander.pin_set_mode(2, 0) #False 为 OUTPUT) LCD_RST_GPIO
expander.pin_set_mode(3, 0) #False 为 OUTPUT)LCD_CS_GPIO

expander.digital_write(1, 1) #设置为高电平
expander.digital_write(3, 1) #设置为高电平
time.sleep(0.1)
expander.digital_write(3, 0) #设置为低电平
time.sleep(0.1)


# 参见原理图
spi = machine.SPI(
    2,
    baudrate=80_000_000,
    sck=machine.Pin(1, machine.Pin.OUT),
    mosi=machine.Pin(0, machine.Pin.OUT),
    miso=None 
)

display = lvgl_esp32.Display(
    spi=spi,
    width=320,
    height=240,
    swap_xy=False,
    mirror_x=True,
    mirror_y=True,
    invert=False,
    bgr=True,
    reset=47, #用-1会因为参数检查报错 实际上没用
    dc=2,
    cs=47, #用-1会因为参数检查报错 实际上没用
    pixel_clock=20_000_000,
)
# Enable LCD backlight
#bl = machine.Pin(1,  machine.Pin.OUT)
#bl.on()

display.init()
wrapper = lvgl_esp32.Wrapper(display)
wrapper.init()

screen = lv.screen_active()
screen.set_style_bg_color(lv.color_hex(0x003a57), lv.PART.MAIN)

label = lv.label(screen)
label.set_text("Hello world")
label.set_style_text_color(lv.color_hex(0x0), lv.PART.MAIN)
label.align(lv.ALIGN.CENTER, 0, 0)

btn = lv.button(screen)
label1 = lv.label(btn)
label1.set_text("button1")
btn.align(lv.ALIGN.CENTER, 0, 40)

def wait_playing(p):
    stattt= p.get_state()
    print(stattt, '\n')
    i=1
    while p.get_state()['status'] == player.STATUS_RUNNING:
        print('\rPlaying: %s' % ('*' * i), end='')
        time.sleep(1)
        i += 1
    print('\n')

def run():
    def callback(stat):
        print("callback->", stat)
        pass

    mPlayer=player(callback)
    mPlayer.set_vol(80)
    print('Set volume to: ', mPlayer.get_vol())
    print('Play source: ', '/sdcard/2.mp3')
    mPlayer.play('file://sdcard/2.mp3')
    wait_playing(mPlayer)

def btn_event_cb(event):
    #LV_EVENT_locals_dict_table
    if event.code == lv.EVENT.PRESSED:
        print("Button LV_EVENT_PRESSED!")
    elif event.code == lv.EVENT.CLICKED:
        print("Button LV_EVENT_CLICKED!")
        run()

btn.add_event_cb(btn_event_cb, lv.EVENT.ALL, None)

while True:
    lv.timer_handler_run_in_period(5)
    #time.sleep(0.1)

'''
# a = lv.anim_t()
# a.init()
# a.set_var(label)
# a.set_values(10, 50)
# a.set_duration(1000)
# a.set_playback_delay(100)
# a.set_playback_duration(300)
# 
# a.set_repeat_delay(500)
# a.set_repeat_count(lv.ANIM_REPEAT_INFINITE)
# a.set_path_cb(lv.anim_t.path_ease_in_out)
# a.set_custom_exec_cb(lambda _, v: label.set_y(v))
# a.start()
# 
# while True:
#     lv.timer_handler_run_in_period(5)
'''

