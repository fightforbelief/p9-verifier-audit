from itertools import combinations, product
from fractions import Fraction
from math import comb
import unittest

from audit import interval, mass, summarize


class AuditTests(unittest.TestCase):
    def test_ties_missing_and_all_subset_sizes(self):
        for scores in ([0,0,1],[1,1,1,1],[],[1,2,3,4]):
            for n in range(1,6):
                wanted = [Fraction(0) for _ in scores]
                for subset in combinations(range(5),n):
                    valid = [i for i in subset if i<len(scores)]
                    if valid:
                        top = max(scores[i] for i in valid)
                        wins = [i for i in valid if scores[i]==top]
                        for i in wins:
                            wanted[i] += Fraction(1,len(wins)*comb(5,n))
                self.assertEqual(wanted,[Fraction(x,12*comb(5,n)) for x in mass(scores,5,n,12)])

    def test_corrupted_prefix_interval(self):
        weights = [3,-7,0,12,-8]
        for observed in product(range(2),repeat=3):
            for e in range(4):
                possible = [sum(x*y for x,y in zip(weights,truth))
                            for truth in product(range(2),repeat=5)
                            if sum(x!=y for x,y in zip(observed,truth))<=e]
                self.assertEqual(interval(list(zip(weights,observed+(0,0))),3,e),
                                 (min(possible),max(possible)))

    def test_sign_and_corruption_radius(self):
        a,b = [8,4,3,2,1,0],[1,1,2,3,4,7]
        for y in product(range(2),repeat=len(a)):
            units = list(zip(a,b,y))
            s = summarize(units,sum(a))
            full = sum((u-v)*j for u,v,j in units)
            possible = [sum(i!=j for i,j in zip(x,y)) for x in product(range(2),repeat=len(y))
                        if full*sum((u-v)*j for u,v,j in zip(a,b,x))<=0]
            self.assertEqual(min(possible),s['erase'])
            for name,priority in [('difference',lambda r:abs(r[0]-r[1])),('pooled',lambda r:max(r[:2]))]:
                records = [(u-v,j) for u,v,j in sorted(units,key=priority,reverse=True)]
                for e in (0,1,5):
                    found = next((i for i in range(len(y)+1) if
                                  (lambda t:t[0]>0 or t[1]<0)(interval(records,i,e))),None)
                    self.assertEqual(found,s['policies'][name]['sign'][e])

    def test_minimax_review_with_corruption(self):
        weights=[2,13,6,8,-4]
        for b in range(1,6):
            for e in (0,1,2):
                widths=[]
                for chosen in combinations(range(5),b):
                    ordered = [weights[i] for i in (*chosen,*(j for j in range(5) if j not in chosen))]
                    worst=0
                    for y in product(range(2),repeat=b):
                        lo,hi=interval(list(zip(ordered,y+(0,)*(5-b))),b,e)
                        worst=max(worst,hi-lo)
                    expected=sum(map(abs,ordered[b:]))+sum(sorted(map(abs,ordered[:b]),reverse=True)[:2*e])
                    self.assertEqual(expected,worst)
                    widths.append(worst)
                ranked=sorted(map(abs,weights),reverse=True)
                self.assertEqual(min(widths),sum(ranked[b:])+sum(ranked[:min(b,2*e)]))
