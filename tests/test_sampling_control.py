import unittest
from math import comb
from sampling_control import upper_binomial


class SamplingTests(unittest.TestCase):
    def test_upper_tail_coverage(self):
        for n in (3,11,30):
            for j in range(101):
                p=j/100
                fail=sum(comb(n,k)*p**k*(1-p)**(n-k) for k in range(n+1) if upper_binomial(n,k)<p)
                self.assertLessEqual(fail,1/480+1e-14)
