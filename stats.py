from collections import Counter
import operator

class Stats:
    @staticmethod
    def makeEmpy():
        s = Stats()
        s.pagesToNumberOfAccesses = Counter()
        s.unsuccessfulPages = Counter()
        s.successful = 0
        s.unsuccessful = 0
        s.ipToNumberOfAccesses = Counter()
        s.ipToPages = {}
        s.accessesPerMinute = {}
        return s
    def __init__(self,
                 pagesToNumberOfAccesses = Counter(),
                 unsuccessfulPages = Counter(),
                 successful = 0,
                 unsuccessful = 0,
                 ipToNumberOfAccesses = Counter(),
                 ipToPages = {},
                 accessesPerMinute = {}
                 ):
        self.pagesToNumberOfAccesses = pagesToNumberOfAccesses
        self.unsuccessfulPages = unsuccessfulPages
        self.successful = successful
        self.unsuccessful = unsuccessful
        self.ipToNumberOfAccesses = ipToNumberOfAccesses
        self.ipToPages = ipToPages
        self.accessesPerMinute = accessesPerMinute

    def __add__(self, other):
        return Stats(self.pagesToNumberOfAccesses + other.pagesToNumberOfAccesses,
                     self.unsuccessfulPages + other.unsuccessfulPages,
                     self.successful + other.successful,
                     self.unsuccessful + other.unsuccessful,
                     self.ipToNumberOfAccesses + other.ipToNumberOfAccesses,
                     Stats.combine(self.ipToPages, other.ipToPages, operator.add),
                     Stats.combine(self.accessesPerMinute, other.accessesPerMinute, operator.add)
                     )
        #new_stats.pagesToNumberOfAccesses = self.pagesToNumberOfAccesses + other.pagesToNumberOfAccesses # sum((Counter(dict(x)) for x in [self.pagesToNumberOfAccesses,other.pagesToNumberOfAccesses]), Counter())
        #new_stats.unsuccessfulPages = self.unsuccessfulPages + other.unsuccessfulPages
        #new_stats.successful = self.successful + other.successful
        #new_stats.unsuccessful = self.unsuccessful + other.unsuccessful
        #new_stats.ipToNumberOfAccesses = self.ipToNumberOfAccesses + other.ipToNumberOfAccesses
        #new_stats.ipToPages = Stats.combine(self.ipToPages, other.ipToPages, operator.add)
        #new_stats.accessesPerMinute = Stats.combine(self.accessesPerMinute, other.accessesPerMinute, operator.add)
        #return new_stats

    @staticmethod
    def combine(a, b, op=operator.add):
        return dict(a.items() + b.items() + \
            [(k, op(a[k], b[k])) for k in set(b) & set(a)])
