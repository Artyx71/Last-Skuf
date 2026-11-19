"""Read-only analysis of immutable baseline; no engine or Controller imports."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "reports/pre_p07/qa-pacing-calibration-01/actual-evidence"
OUT = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stats(values):
    ordered = sorted(values)
    assert ordered and all(math.isfinite(v) and v >= 0 for v in ordered)
    return {"samples": len(ordered), "p50": ordered[math.ceil(.5*len(ordered))-1],
            "p95": ordered[math.ceil(.95*len(ordered))-1],
            "p99": ordered[math.ceil(.99*len(ordered))-1], "max": ordered[-1]}

raw = json.loads((DATA / "raw.json").read_text())
metrics = json.loads((DATA / "metrics.json").read_text())
contract = json.loads((DATA / "contract.PROPOSED.json").read_text())
assert sha(DATA / "raw.json") == "5ec6a6896ba577043ce42d4940b805c4d61bcdd3fbd5aa98c28795a0442fc69d"
assert raw["failed"] == 0 and raw["passed"] == len(raw["checks"]) == 74
assert all(row["passed"] is True for row in raw["checks"])
requests = raw["requests"]
assert len(requests) == len({row["id"] for row in requests}) == 48
counts = {context: dict(Counter(row["kind"] for row in requests if row["context"] == context))
          for context in {row["context"] for row in requests}}
assert len(counts) == 8
assert all(count == {"move": 4, "melee": 1, "restart": 1} for count in counts.values())
for series in [raw["physics"], raw["draws"]]:
    assert all(right["usec"] > left["usec"] for left, right in zip(series, series[1:]))
accepted, rendered, retries, windups = [], [], [], []
for request in requests:
    physical = [row for row in raw["physics"] if row["usec"] == request["accepted_usec"] and row["tick"] == request["accepted_tick"]]
    draw = [row for row in raw["draws"] if row["usec"] == request["render_usec"] and row["draw"] == request["render_draw"]]
    assert len(physical) == len(draw) == 1
    assert physical[0]["state"] == request["accepted_state"] and draw[0]["state"] == request["render_state"]
    assert physical[0]["state"]["context"] == draw[0]["state"]["context"] == request["context"]
    assert request["input_usec"] <= request["accepted_usec"] <= request["render_usec"]
    before = request["before_state"]
    changed = [row for row in raw["draws"] if row["usec"] >= request["accepted_usec"]
               and row.get("state", {}).get("context") == request["context"]
               and any(row["state"][key] != before[key] for key in ["draw_position", "animation", "frame"])]
    assert changed and changed[0]["usec"] == request["render_usec"]
    accepted.append((request["accepted_usec"]-request["input_usec"])/1000)
    rendered.append((request["render_usec"]-request["input_usec"])/1000)
    if request["kind"] == "restart":
        deaths = [row for row in raw["contacts"] if row["usec"] == request["death_usec"]
                  and row["context"] == request["context"] and row["lethal"] is True and row["target"] == row["player_id"]]
        assert len(deaths) == 1
        retries.append((request["accepted_usec"]-request["death_usec"])/1000)
    if request["kind"] == "melee":
        contacts = [row for row in raw["contacts"] if row["usec"] == request["contact_usec"]
                    and row["context"] == request["context"] and row["action"] == "shove" and row["target"] != row["player_id"]]
        assert len(contacts) == 1 and request["contact_usec"] > request["accepted_usec"]
        windups.append((request["contact_usec"]-request["accepted_usec"])/1000)

pairs = [(right["segment"], (right["usec"]-left["usec"])/1000)
         for left, right in zip(raw["draws"], raw["draws"][1:]) if left["segment"] == right["segment"]]
idle = [value for segment, value in pairs if segment == "idle_calibration"]
controlled = [value for segment, value in pairs if segment in ["controlled_movement", "controlled_melee", "controlled_restart"]]
derived = {"input_accept_ms": stats(accepted), "input_render_ms": stats(rendered),
           "death_to_control_ms": stats(retries), "accepted_to_contact_ms": stats(windups),
           "old_mixed_movement_frame_ms": stats(idle+controlled),
           "controlled_only_frame_ms": stats(controlled), "idle_calibration_frame_ms": stats(idle)}
for own, original in [("input_accept_ms", "input_accept_ms"), ("input_render_ms", "input_render_ms"),
                      ("death_to_control_ms", "death_to_control_ms"), ("accepted_to_contact_ms", "accepted_to_contact_ms"),
                      ("old_mixed_movement_frame_ms", "movement_frame_ms"), ("idle_calibration_frame_ms", "idle_frame_ms")]:
    assert derived[own] == metrics[original]
idle95 = derived["idle_calibration_frame_ms"]["p95"]
limits = {"accept_p95_ms": min(50, math.ceil(idle95*2)), "render_p95_ms": min(83.334, math.ceil(idle95*3.5)),
          "frame_p95_ms": min(25, math.ceil(idle95*1.4)), "frame_p99_ms": min(33.334, math.ceil(idle95*1.9)), "restart_max_ms": 1000}
assert limits == contract["limits"]
assessment = {"schema": 1, "status": "ACTUAL_BASELINE_VALID_DATA_NOT_CONTRACT_APPROVAL",
              "raw_sha256": sha(DATA/"raw.json"), "old_contract_sha256": sha(DATA/"contract.PROPOSED.json"),
              "functional_checks": 74, "raw_draws": len(raw["draws"]), "raw_physics": len(raw["physics"]),
              "request_kind_counts": counts, "all48_full_physics_context_and_first_changed_draw_bindings": True,
              "actual8_outgoing_and8_lethal_contact_bindings": True, "derived_stats_independent": derived,
              "derived_limit_values": limits, "hardware_raw": raw["hardware"], "capture_texture_dimensions": [640, 360],
              "legacy_hardware_viewport_is_Window_size": [466, 508], "old_budget_includes_idle_despite_plan": True,
              "guard_and_scope_findings_prevent_GO": True, "no_engine_Controller_Git_network_calls": True}
(OUT/"baseline-assessment.json").write_text(json.dumps(assessment, ensure_ascii=False, indent=2)+"\n")
print(json.dumps(derived, indent=2))
print("Original contract:", assessment["old_contract_sha256"], "limits:", limits)
