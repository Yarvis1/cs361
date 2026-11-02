import sys
import datetime

class Logger:
    def event(self, s):
        print(s)

    def warning(self, s):
        print(s, file=sys.stderr)

class Divider:
    def __init__(self,logger):
        self.logger = logger
        

    def divide(self, a, b):
        if b == 0:
            self.logger.warning("division by zero")
            return None
        self.logger.event(f"dividing {a} by {b}")
        return a / b

class TimeLogger:
    def isotime(self):
        return datetime.datetime.now().isoformat()

    def event(self, s):
        print(f"{self.isotime()}: {s}")

    def warning(self, s):
        print(f"{self.isotime()}: WARNING: {s}")

d = Divider(Logger())
t = Divider(TimeLogger())

d.divide(1,2)
d.divide(10,5)
d.divide(99,0)

t.divide(1,2)
t.divide(10,5)
t.divide(99,0)



