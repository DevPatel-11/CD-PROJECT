from typing import Any, List, Dict, Set, Tuple, Optional
from .parser_core import Grammar
from .first_follow import compute_first_sets


# ----------------------------------------------------------------------
# Helper: FIRST(seq)
# ----------------------------------------------------------------------
def _first_seq(seq: List[str], first_sets: Dict[str, List[str]]) -> Set[str]:
    result = set()
    for sym in seq:
        f = set(first_sets.get(sym, [sym]))
        result.update(f - {"ε"})
        if "ε" not in f:
            break
    else:
        result.add("ε")
    return result


# ----------------------------------------------------------------------
# LR(1) CLOSURE
# ----------------------------------------------------------------------
def _closure_core(
    items: Set[Tuple[str, Tuple[str, ...], int, str]],
    grammar: Grammar,
    first_sets: Dict[str, List[str]],
):
    closure = set(items)
    added = True

    while added:
        added = False
        new_items = set()

        for lhs, rhs, dot, la in closure:
            if dot < len(rhs):
                B = rhs[dot]
                if B in grammar.nonterminals:
                    next_seq = list(rhs[dot + 1 :]) + [la]
                    lookaheads = _first_seq(next_seq, first_sets)

                    for prod_rhs in grammar.productions[B]:
                        for lk in lookaheads:
                            item = (B, tuple(prod_rhs), 0, lk)
                            if item not in closure:
                                new_items.add(item)

        if new_items:
            closure.update(new_items)
            added = True

    return closure


# ----------------------------------------------------------------------
# LR(1) GOTO
# ----------------------------------------------------------------------
def _goto(items, symbol, grammar, first_sets):
    shifted = set()
    for lhs, rhs, dot, la in items:
        if dot < len(rhs) and rhs[dot] == symbol:
            shifted.add((lhs, rhs, dot + 1, la))
    return _closure_core(shifted, grammar, first_sets) if shifted else set()


# ----------------------------------------------------------------------
# Canonical Collection of LR(1) item sets
# ----------------------------------------------------------------------
def _canonical_lr1_collection(grammar, first_sets):
    start_rhs = grammar.productions[grammar.start][0]
    start_item = (grammar.start, tuple(start_rhs), 0, "$")

    c0 = _closure_core({start_item}, grammar, first_sets)

    collection = [c0]
    state_map = {frozenset(c0): 0}
    queue = [c0]

    while queue:
        I = queue.pop(0)
        idx = state_map[frozenset(I)]

        symbols = set()
        for lhs, rhs, dot, la in I:
            if dot < len(rhs):
                symbols.add(rhs[dot])

        for X in symbols:
            gotoI = _goto(I, X, grammar, first_sets)
            if gotoI:
                key = frozenset(gotoI)
                if key not in state_map:
                    state_map[key] = len(collection)
                    collection.append(gotoI)
                    queue.append(gotoI)

    return collection, state_map


# ----------------------------------------------------------------------
# Build LR(1)
# ----------------------------------------------------------------------
def build_lr1(grammar, first_sets, follow_sets):
    items, state_map = _canonical_lr1_collection(grammar, first_sets)

    lr1_item_sets = []
    for idx, item_set in enumerate(items):
        lr1_item_sets.append(
            {
                "id": idx,
                "items": [
                    {
                        "production": f"{lhs} -> {' '.join(rhs)}",
                        "dot": dot,
                        "lookahead": la,
                    }
                    for (lhs, rhs, dot, la) in sorted(item_set)
                ],
            }
        )

    return {
        "item_sets": lr1_item_sets,
        "states": items,
        "state_map": state_map,
        "grammar": grammar,
    }


# ----------------------------------------------------------------------
# Build ACTION / GOTO TABLES
# ----------------------------------------------------------------------
def build_action_goto_tables(lr1_result, grammar):
    action = {}
    goto = {}

    state_map = lr1_result["state_map"]
    items = lr1_result["states"]
    first_sets = compute_first_sets(grammar)

    for s, item_set in enumerate(items):
        s_str = str(s)
        action[s_str] = {}
        goto[s_str] = {}

        for lhs, rhs, dot, la in item_set:

            # SHIFT or GOTO
            if dot < len(rhs):
                sym = rhs[dot]

                # SHIFT
                if sym in grammar.terminals:
                    next_items = _goto(item_set, sym, grammar, first_sets)
                    next_state = state_map.get(frozenset(next_items))
                    if next_state is not None:
                        entry = f"shift {next_state}"

                        if sym in action[s_str]:
                            parts = set(action[s_str][sym].split(" | "))
                            parts.add(entry)
                            action[s_str][sym] = " | ".join(sorted(parts))
                        else:
                            action[s_str][sym] = entry

                # GOTO
                elif sym in grammar.nonterminals:
                    next_items = _goto(item_set, sym, grammar, first_sets)
                    next_state = state_map.get(frozenset(next_items))
                    if next_state is not None:
                        goto[s_str][sym] = next_state

            # REDUCE or ACCEPT
            else:
                if lhs == grammar.start and la == "$":
                    action[s_str][la] = "accept"
                else:
                    prod_str = f"{lhs} -> {' '.join(rhs)}"
                    entry = f"reduce {prod_str}"

                    if la in action[s_str]:
                        parts = set(action[s_str][la].split(" | "))
                        parts.add(entry)
                        action[s_str][la] = " | ".join(sorted(parts))
                    else:
                        action[s_str][la] = entry

    return action, goto


# ----------------------------------------------------------------------
# Detect Conflicts
# ----------------------------------------------------------------------
def detect_conflicts(action_table):
    conflicts = []

    for state, row in action_table.items():
        for symbol, cell in row.items():
            actions = [a.strip() for a in cell.split("|")]
            types = [a.split()[0] for a in actions if a != "accept"]

            if types.count("shift") and types.count("reduce"):
                detail_str = " | ".join(actions)
                conflicts.append(
                    {
                        "state": int(state),
                        "symbol": symbol,
                        "type": "shift/reduce",
                        "details": f"Actions: {detail_str}",
                    }
                )

            if types.count("reduce") > 1:
                detail_str = " | ".join(actions)
                conflicts.append(
                    {
                        "state": int(state),
                        "symbol": symbol,
                        "type": "reduce/reduce",
                        "details": f"Actions: {detail_str}",
                    }
                )

    return {"has_conflict": len(conflicts) > 0, "conflicts": conflicts}


# ----------------------------------------------------------------------
# Resolve Conflicts (left associative default)
# ----------------------------------------------------------------------
def resolve_conflicts_default_left(action_table):
    resolutions = []

    for st, row in action_table.items():
        for sym, cell in list(row.items()):
            acts = [a.strip() for a in cell.split("|")]
            types = [a.split()[0] for a in acts if a != "accept"]

            if types.count("shift") and types.count("reduce"):
                reduce_act = [a for a in acts if a.startswith("reduce")][0]
                row[sym] = reduce_act
                resolutions.append(
                    {
                        "state": int(st),
                        "symbol": sym,
                        "type": "shift/reduce",
                        "original": acts,
                        "chosen": reduce_act,
                    }
                )

    return action_table, resolutions


# ----------------------------------------------------------------------
# PARSE SIMULATION
# ----------------------------------------------------------------------
def simulate_parse(
    grammar,
    input_tokens,
    action_table,
    goto_table,
    start_symbol,
    max_steps=250,
):
    stack = [0]
    tokens = list(input_tokens) + ["$"]
    index = 0
    steps = []
    errors = []
    final_status = "in_progress"

    for step_no in range(1, max_steps + 1):
        state = stack[-1]
        token = tokens[index] if index < len(tokens) else "$"
        action = action_table.get(str(state), {}).get(token)

        step_entry = {
            "step": step_no,
            "stack": [str(s) for s in stack],
            "input": tokens[index:],
            "action": action or "error",
            "notes": "",
        }
        steps.append(step_entry)

        if not action:
            errors.append(f"No action for state {state} on symbol '{token}'")
            final_status = "rejected"
            step_entry["notes"] = "Parsing halted due to missing ACTION entry."
            break

        if action == "accept":
            final_status = "accepted"
            step_entry["notes"] = "Input accepted."
            break

        if action.startswith("shift"):
            next_state = int(action.split()[1])
            stack.extend([token, next_state])
            index += 1
            step_entry["notes"] = f"Shift '{token}' and goto state {next_state}."
            continue

        if action.startswith("reduce"):
            prod = action[len("reduce ") :]
            lhs, rhs = prod.split("->")
            lhs = lhs.strip()
            rhs_symbols = rhs.strip().split()

            pop_count = 0 if rhs_symbols == ["ε"] or rhs_symbols == [] else len(rhs_symbols)
            for _ in range(2 * pop_count):
                stack.pop()

            prev_state = stack[-1]
            stack.append(lhs)
            goto_state = goto_table.get(str(prev_state), {}).get(lhs)

            if goto_state is None:
                errors.append(f"No goto for state {prev_state} on symbol '{lhs}'")
                final_status = "rejected"
                step_entry["notes"] = "Parsing halted due to missing GOTO entry."
                break

            stack.append(goto_state)
            rhs_desc = "ε" if not rhs_symbols or rhs_symbols == ["ε"] else " ".join(rhs_symbols)
            step_entry["notes"] = f"Reduce {lhs} -> {rhs_desc}; goto state {goto_state}."
            continue

        errors.append(f"Unknown parser action '{action}'")
        final_status = "rejected"
        step_entry["notes"] = "Parsing halted due to unknown action."
        break
    else:
        final_status = "max_steps"
        errors.append(f"Simulation exceeded {max_steps} steps.")

    return {
        "steps": steps,
        "final_status": final_status,
        "errors": errors,
    }




# ----------------------------------------------------------------------
# SIMULATE PARSING (for frontend/back-end interaction)
# ----------------------------------------------------------------------
def simulate_parse(grammar, input_tokens, action_table, goto_table, start_symbol, max_steps=1000):
    steps = []
    errors = []

    stack = [0]
    tokens = list(input_tokens) + ["$"]
    index = 0

    step_no = 0

    while True:
        if step_no >= max_steps:
            errors.append("Maximum steps exceeded")
            return {"steps": steps, "final_status": "timeout", "errors": errors}

        state = stack[-1]
        lookahead = tokens[index] if index < len(tokens) else "$"

        act = action_table.get(str(state), {}).get(lookahead)

        # Record current snapshot
        steps.append(
            {
                "step": step_no,
                "stack": list(stack),
                "input": tokens[index:],
                "action": act if act is not None else "error",
                "notes": "",
            }
        )

        if not act:
            errors.append(f"No action for state {state} and symbol '{lookahead}'")
            return {"steps": steps, "final_status": "error", "errors": errors}

        act = act.strip()

        # SHIFT
        if act.startswith("shift"):
            try:
                next_state = int(act.split()[1])
            except Exception:
                errors.append(f"Invalid shift action '{act}'")
                return {"steps": steps, "final_status": "error", "errors": errors}

            stack.append(lookahead)
            stack.append(next_state)
            index += 1

        # REDUCE
        elif act.startswith("reduce"):
            prod = act[len("reduce ") :]
            if "->" not in prod:
                errors.append(f"Invalid reduce production '{prod}'")
                return {"steps": steps, "final_status": "error", "errors": errors}

            lhs, rhs = prod.split("->")
            lhs = lhs.strip()
            rhs_symbols = rhs.strip().split()

            # pop 2*len(rhs_symbols) items (state and symbol) unless epsilon
            if rhs_symbols == ["ε"] or rhs_symbols == []:
                pop_len = 0
            else:
                pop_len = 2 * len(rhs_symbols)

            for _ in range(pop_len):
                if stack:
                    stack.pop()

            prev_state = stack[-1]
            stack.append(lhs)
            goto_state = goto_table.get(str(prev_state), {}).get(lhs)
            if goto_state is None:
                errors.append(f"GOTO error: no entry for state {prev_state} and symbol {lhs}")
                return {"steps": steps, "final_status": "error", "errors": errors}

            stack.append(goto_state)

        # ACCEPT
        elif act == "accept":
            steps.append(
                {
                    "step": step_no + 1,
                    "stack": list(stack),
                    "input": ["$"],
                    "action": "accept",
                    "notes": "",
                }
            )
            return {"steps": steps, "final_status": "accepted", "errors": []}

        else:
            # Unknown action
            errors.append(f"Unknown action '{act}'")
            return {"steps": steps, "final_status": "error", "errors": errors}

        step_no += 1
