from machine import Pin, ADC, PWM
from utime import sleep

def duty(strength):
    return int(65535*(max(min(strength/100, 1), 0)))

led = Pin("LED", Pin.OUT)
temppin = ADC(Pin(26))
light = PWM(Pin(2))
light.freq(11)
light.duty_u16(duty(100))
fan = PWM(Pin(3))
fan.freq(11)
fan.duty_u16(duty(10))
thermo = PWM(Pin(4))
thermo.freq(11)
thermo.duty_u16(duty(0))

controlFreq = 1     # Hz
pGain = 10          # %/C
iGain = 0.1         # %/C/s
iHighLim = 50       # %
iLowLim = -10       # %
setpoint = 90       # C
thermoBreak = 30    # % for thermostat vs fan
fanRange = 100 - thermoBreak
iTerm = 0

print("controller: startup")
sleep(1)
light.duty_u16(duty(0))

while True:
    led.value(not led.value())

    tempv = (3.3*temppin.read_u16())/65535
    if tempv > 0.75406:
        temp = -27.013*tempv + 100.37
    else:
        temp = -70.335*tempv + 132.79

    if temp > 115:
        light.duty_u16(duty(100))
    else:
        light.duty_u16(duty(0))

    error = temp - setpoint
    pTerm = error * pGain
    iTerm = iTerm + error * iGain/controlFreq
    iTerm = min(iHighLim, max(iLowLim, iTerm))
    control = pTerm + iTerm
    control = min(100, max(0, control))

    fanPercent = min(90, 100 - 100 * max(0, control - thermoBreak)/fanRange)
    fan.duty_u16(duty(fanPercent))
    thermoPercent = 100 * max(0, min(thermoBreak, control))/thermoBreak
    thermo.duty_u16(duty(thermoPercent))

    print("Temp: " + str(round(temp)) + " degC iTerm: " + str(round(iTerm)) + " % Fan: " + str(round(100-fanPercent)) + " % Thermo: " + str(round(thermoPercent)) + " %")

    sleep(1/controlFreq)