"""Explicit diagnostic negative controls; never authorized for real dispatch."""
from copy import deepcopy
from . import candidate, joint_reference, runtime, audit


def no_acquisition(bundle, *, node_limit=100_000):
    return joint_reference.solve(bundle, node_limit=node_limit, use_probes=False)


def missing_obligation_abstraction(bundle, *, feedback=False):
    """Intentionally omit probe sessions from the controller's abstraction.

    Keep the original concrete plant for scoring. This must fail the independent
    compilation audit, and is not a B-A or B-AB baseline.
    """
    broken = deepcopy(bundle)
    for record in broken["points"].values():record["point"]["sessions"] = []
    for world in broken["l0"]["worlds"].values():
        for node in world["states"].values():
            node["capabilities"] = [c for c in node["capabilities"] if not c.startswith("session:")]
            node["obligations"] = []
            for edges in node["transitions"].values():
                for edge in edges:
                    edge["delta"]["obligations"] = {"add": [], "remove": []}
                    for which in ["add", "remove"]:
                        edge["delta"]["capabilities"][which] = [c for c in edge["delta"]["capabilities"][which] if not c.startswith("session:")]
    result = candidate.solve(broken, feedback=feedback)
    return {"diagnostic_only": True, "feedback": feedback, "obligation_tracking": False,
            "audit": audit.check_compilation(broken), "controller_result": result,
            "scorer": runtime.evaluate(bundle, result, diagnostic_unchecked=True)}
