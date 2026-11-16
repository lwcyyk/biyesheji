"""Independent raw-table interpreter used ONLY by R-I, checking and L0 replay.

No candidate/semantics imports. Sharing this small interpreter between R-I and
the checker is disclosed: they are not independent of each other.
"""


def state_record(data, key):
    w, s = key
    return data["worlds"][w]["states"][s]


def is_safe(data, key):
    record = state_record(data, key)
    for forbidden in data["safety"]["forbidden_facts"]:
        if forbidden in record["facts"]:return False
    for capability in data["safety"]["preserve_capabilities"]:
        if capability not in record["capabilities"]:return False
    return True


def is_goal(data, belief):
    if len(belief) == 0:return False
    for key in belief:
        record = state_record(data, key)
        if not is_safe(data, key):return False
        if record["account"] != data["goal"]["account"]:return False
        if len(record["obligations"]) != 0:return False
        for fact in data["goal"]["facts"]:
            if fact not in record["facts"]:return False
    return True


def expand(data, belief, aid):
    """No horizon logic here; caller must consume exactly one decision step."""
    failures = []; observations = {}
    if not belief:return {}, ["empty_knowledge"]
    if aid not in data["actions"]:return {}, [f"action:{aid}"]
    op = data["actions"][aid]
    for key in sorted(belief):
        world, local = key; record = state_record(data, key); label = world + "/" + local
        if not is_safe(data, key):failures.append("safe:" + label)
        if record["account"] != op["account"]:failures.append(f"account:{aid}:{label}")
        if op["approval"] not in record["approvals"]:failures.append(f"approval:{op['approval']}:{label}")
        if any(f not in record["facts"] for f in op["requires"]):failures.append(f"requires:{aid}:{label}")
        for resource in op["cost"]:
            if resource not in record["budget"] or record["budget"][resource] < op["cost"][resource]:
                failures.append(f"budget:{resource}:{label}")
        mapping = data["worlds"][world]["native_roots"]
        for pair in op["independent"]:
            l, r = pair
            if l not in mapping or r not in mapping or mapping[l] == mapping[r]:
                failures.append(f"independence:{l}:{r}:{label}")
        alternatives = record["transitions"].get(aid)
        if not alternatives:failures.append(f"successors:{aid}:{label}")
        else:
            for edge in alternatives:
                observation = edge["observation"]
                observations.setdefault(observation, set()).add((edge["target"][0], edge["target"][1]))
    if failures:return {}, sorted(failures)
    return {o: frozenset(values) for o, values in observations.items()}, []
