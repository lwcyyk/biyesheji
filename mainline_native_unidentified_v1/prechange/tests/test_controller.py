import unittest
from auth_lifecycle.adapters import TableAdapter
from auth_lifecycle.controller import BoundedController
from auth_lifecycle.fixtures import stay_finish,declared_regime_change,account_case


class ControllerTests(unittest.TestCase):
    def test_real_local_dispatch_cannot_stay_forever(self):
        m=stay_finish(horizon=8);c=BoundedController(m);a=TableAdapter(m,('w','s'))
        for _ in range(7):self.assertEqual(c.step('stay',a).status,'CONTINUE')
        self.assertEqual(c.state.remaining,1)
        self.assertEqual(c.step('stay',a).status,'REJECTED')
        self.assertEqual(len(a.history),7)
        self.assertEqual(c.step('finish',a).status,'COMPLETED')
        self.assertEqual(c.state.remaining,0)
        self.assertEqual(len(a.history),8)

    def test_limit_does_not_dispatch(self):
        m=stay_finish();c=BoundedController(m);a=TableAdapter(m,('w','s'))
        self.assertEqual(c.step('finish',a,node_limit=0).status,'INCONCLUSIVE')
        self.assertEqual(a.history,[])
        self.assertEqual(c.state.remaining,2)

    def test_observable_model_conflict_does_not_finish(self):
        m=declared_regime_change();c=BoundedController(m)
        class ConflictingAdapter(TableAdapter):
            def execute(self,*args,**kw):
                super().execute(*args,**kw)
                return 'not-declared-v3'
        a=ConflictingAdapter(m,('v1','s'))
        self.assertEqual(c.step('probe',a).status,'UNKNOWN')
        self.assertEqual(c.pending_action,'probe')
        self.assertEqual(c.step('finish',a).status,'UNKNOWN')
        self.assertEqual(len(a.history),1)

    def test_exception_after_effect_stays_unknown(self):
        m=stay_finish();c=BoundedController(m)
        class LostResult(TableAdapter):
            def execute(self,*args,**kw):
                super().execute(*args,**kw)
                raise RuntimeError('synthetic lost response')
        a=LostResult(m,('w','s'))
        self.assertEqual(c.step('finish',a).status,'UNKNOWN')
        self.assertIn('done',a.audit_state()['facts'])
        self.assertEqual(c.pending_action,'finish')
        self.assertEqual(c.pending_context['belief_before'],[['w','s']])
        self.assertTrue(c.pending_context['unmodelled_effects_possible'])
        self.assertEqual(c.last_valid_state.remaining,2)
        self.assertEqual(c.step('finish',a).status,'UNKNOWN')
        self.assertEqual(len(a.history),1)

    def test_wrong_account_has_no_effect(self):
        m=account_case(True);c=BoundedController(m);a=TableAdapter(m,('w','s'))
        self.assertEqual(c.step('finish',a).status,'REJECTED')
        self.assertEqual(a.history,[])


if __name__=='__main__':unittest.main()
