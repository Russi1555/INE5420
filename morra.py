import signal
import sys
from time import sleep

class Classe:
    def termination_handler(self, signal, frame):
        print("POR FAVOR NAO NAO NAO")
        sleep(2)
        print("EU FAÇO QUALQUER COISAAAAAAA")
        sleep(1)
        print("💀")
        sys.exit(0)

    def run(self):
       signal.signal(signal.SIGTERM, self.termination_handler)
       while True:
          pass

if __name__ == "__main__":
   Classe().run()