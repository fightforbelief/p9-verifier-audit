import unittest

from review import coefficients, evaluate, plan


class ReviewTests(unittest.TestCase):
    def test_blind_plan_and_partial_return(self):
        w,den=coefficients([dict(problem="p",candidates=[
            dict(unit="2",a=3,b=1),dict(unit="2",a=2,b=2),dict(unit="3",a=1,b=3)])],3,3)
        self.assertEqual(set(w),{("p","2"),("p","3")})
        self.assertEqual(evaluate(w,den,[],0)["exact"],["-1","1"])
        rows=plan(w,2,5,0)
        self.assertTrue(all(row["grade"] is None for row in rows))
        for row in rows:
            row["grade"]=row["unit"]=="2"
        self.assertEqual(evaluate(w,den,rows,0)["decision"],"A")
        self.assertEqual(evaluate(w,den,rows,1)["exact"],["0","1"])
        with self.assertRaises(ValueError):
            evaluate(w,den,rows+rows,0)
