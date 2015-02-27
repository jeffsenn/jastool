import time
import Adafruit_BBIO.GPIO as GPIO
RELAY_VCC='P8_15'
RELAY_PINS='P8_%d'
RELAY_PINOFFSET=7
CYCLE_OFF = 2.0
CONF=False

def confpin(p):
  GPIO.setup(p, GPIO.OUT)
  GPIO.output(p, GPIO.HIGH)

def confpins():
  GPIO.setup(RELAY_VCC, GPIO.OUT)
  GPIO.output(RELAY_VCC, GPIO.LOW)
  for a in [RELAY_PINS % i for i in xrange(RELAY_PINOFFSET,15)]:
    confpin(a)
  GPIO.output(RELAY_VCC, GPIO.HIGH)

def relay(n,on_off):
  global CONF
  if not CONF:
        confpins()
        CONF = True
  if on_off:
    v = GPIO.LOW
  else:
    v = GPIO.HIGH
  r = n * 2
  if n > 3: 
     r -= 7
  GPIO.output(RELAY_PINS % (r+RELAY_PINOFFSET,), v)

def toggle(n,delay=CYCLE_OFF):
    relay(n,1)
    time.sleep(delay)
    relay(n,0)

if __name__ == '__main__':
    import sys
    delay = CYCLE_OFF
    if len(sys.argv) > 2: delay = float(sys.argv[2])
    toggle(float(sys.argv[1]),delay)
