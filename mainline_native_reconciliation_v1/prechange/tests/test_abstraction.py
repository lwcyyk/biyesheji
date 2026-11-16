from copy import deepcopy
import unittest
from auth_lifecycle.abstraction import check_relation, lift_policy
from auth_lifecycle.adapters import TableAdapter
from auth_lifecycle.schema import ModelError
from auth_lifecycle.fixtures import stay_finish, session_probe, conflict_worlds, model, world, state, action, edge


def identity_maps(m):
    relation = {(w, s): {(w, s)} for w, world in m["worlds"].items() for s in world["states"]}
    actions = {a: a for a in m["actions"]}
    observations = {e["observation"]: e["observation"] for world in m["worlds"].values() for s in world["states"].values() for edges in s["transitions"].values() for e in edges}
    adapter = TableAdapter(m, tuple(m["initial"][0]))
    bindings = {a: (lambda a=a: adapter.execute(a)) for a in actions}
    return relation, actions, observations, bindings


class AbstractionTests(unittest.TestCase):
    def test_nontrivial_state_and_observation_coarsening(self):
        from auth_lifecycle.candidate import solve
        from auth_lifecycle.checker import check_policy
        c = model({"w": world({"s0": state(facts=["irrelevant:0"]), "s1": state(facts=["irrelevant:1"]), "done": state(facts=["done"])})},
                  {"finish": action()}, horizon=1, initial=[["w","s0"],["w","s1"]])
        for i in range(2):edge(c,("w",f"s{i}"),"finish",f"ok:{i}",("w","done"),effects=["goal-effect"])
        a = stay_finish(horizon=1); del a["actions"]["stay"];del a["worlds"]["w"]["states"]["s"]["transitions"]["stay"]
        a["worlds"]["w"]["states"]["s"]["transitions"]["finish"][0]["observation"] = "ok"
        rel = {("w","s0"):{("w","s")},("w","s1"):{("w","s")},("w","done"):{("w","done")}}
        acts = {"finish":"finish"};obs={"ok:0":"ok","ok:1":"ok"}
        adapter = TableAdapter(c,("w","s1"));bindings={"finish":lambda:adapter.execute("finish")}
        self.assertTrue(check_relation(c,a,rel,acts,obs,bindings)["valid"])
        lifted=lift_policy(c,a,solve(a).policy,rel,acts,obs,bindings)
        self.assertEqual(check_policy(c,lifted).verdict,"ACCEPTED")
        self.assertEqual(set(lifted["children"]),{"ok:0","ok:1"})
        self.assertEqual(bindings["finish"](),"ok:1")

    def test_identity_relation_and_executable_local_adapter(self):
        m = session_probe(); maps = identity_maps(m)
        checked = check_relation(m, m, *maps)
        self.assertTrue(checked["valid"], checked)
        self.assertEqual(checked["external_adapter_proof"], "NOT_PROVED")
        self.assertEqual(maps[-1]["probe"](), "authenticated")
        self.assertEqual(maps[-1]["cleanup"](), "closed")

    def test_coverage_counterexample(self):
        m = stay_finish(); relation, actions, obs, bindings = identity_maps(m)
        relation.pop(("w", "done"))
        self.assertFalse(check_relation(m, m, relation, actions, obs, bindings)["valid"])

    def test_precondition_and_approval_counterexample(self):
        c = stay_finish(); a = deepcopy(c)
        c["worlds"]["w"]["states"]["s"]["approvals"] = []
        c["worlds"]["w"]["states"]["done"]["approvals"] = []
        checked = check_relation(c, a, *identity_maps(c))
        self.assertFalse(checked["valid"])
        self.assertTrue(any("precondition_preservation" in x for x in checked["issues"]))

    def test_observation_counterexample(self):
        m = stay_finish(); rel, acts, obs, bindings = identity_maps(m)
        obs["finished"] = "invented"
        checked = check_relation(m, m, rel, acts, obs, bindings)
        self.assertFalse(checked["valid"])
        self.assertTrue(any("transition_simulation" in x for x in checked["issues"]))

    def test_effect_omission_counterexample(self):
        c = stay_finish(); a = deepcopy(c)
        a["worlds"]["w"]["states"]["s"]["transitions"]["finish"][0]["effects"] = []
        checked = check_relation(c, a, *identity_maps(c))
        self.assertFalse(checked["valid"])
        self.assertTrue(any("effect_omission" in x for x in checked["issues"]))

    def test_budget_counterexample(self):
        c = stay_finish(); a = deepcopy(c)
        for node in a["worlds"]["w"]["states"].values():node["budget"]["calls"] = 1
        checked = check_relation(c, a, *identity_maps(c))
        self.assertFalse(checked["valid"])
        self.assertTrue(any("budget_overestimate" in x for x in checked["issues"]))

    def test_terminal_and_obligation_counterexample(self):
        c = stay_finish(); a = deepcopy(c)
        # Well-formed concrete extra obligation, with a matching creation delta.
        c["worlds"]["w"]["states"]["done"]["obligations"] = ["verify-outcome"]
        c["worlds"]["w"]["states"]["s"]["transitions"]["finish"][0]["delta"]["obligations"]["add"] = ["verify-outcome"]
        checked = check_relation(c, a, *identity_maps(c))
        self.assertFalse(checked["valid"])
        self.assertTrue(any("terminal_reflection" in x for x in checked["issues"]))
        self.assertTrue(any("obligation_omission" in x for x in checked["issues"]))

    def test_missing_concrete_binding(self):
        m = stay_finish(); rel, acts, obs, _ = identity_maps(m)
        checked = check_relation(m, m, rel, acts, obs, {})
        self.assertFalse(checked["valid"])
        self.assertTrue(any("executable_binding" in x for x in checked["issues"]))

    def test_adapter_rejects_wrong_account(self):
        from auth_lifecycle.fixtures import account_case
        a = TableAdapter(account_case(True), ("w", "s"))
        with self.assertRaises(ModelError):a.execute("finish")
        self.assertEqual(a.history, [])


if __name__ == "__main__":unittest.main()
