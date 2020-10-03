from mindwave.parser import ThinkGearParser, TimeSeriesRecorder

import unittest

class ParserTests(unittest.TestCase):

    def testParser(self):
        s = file("baseline.bytes").read()
        ts_recorder = TimeSeriesRecorder()
        parser = ThinkGearParser(recorders=[ts_recorder])
        parser.feed(s)
        
        self.assertTrue(len(ts_recorder.attention) == len(ts_recorder.meditation) == len(ts_recorder.blink) == len(ts_recorder.poor_signal))

        

def main():
    unittest.main()

if __name__ == '__main__':
    main()
    
     def __init__(self, name, balance):
        self._name = name
        self.__balance = balance
        self._transaction_list = [(Account._current_time(), balance)]
        print("Account created for " + self._name)
        self.show_balance()
