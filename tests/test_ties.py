import unittest
from itertools import permutations
from audit import rank_counts
from tie_sensitivity import totals


class TiePolicyTests(unittest.TestCase):
    def test_extreme_orders_with_ineligible_slots(self):
        scores=[3,3,2,2,2]
        grade=[True,False,False,True,True]
        pool=list(zip(range(5),scores,scores,grade))
        for n in range(1,7):
            rank=rank_counts(6,n)
            feasible=[sum(rank[j]*grade[i] for j,i in enumerate(order)) for order in permutations(range(5))
                      if all(scores[a]>=scores[b] for a,b in zip(order,order[1:]))]
            low,hi,forward,reverse=totals(pool,1,rank)
            self.assertEqual((low,hi),(min(feasible),max(feasible)))
            self.assertIn(forward,feasible)
            self.assertIn(reverse,feasible)
