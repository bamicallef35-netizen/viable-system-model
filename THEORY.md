# Theory — every construct, and where it comes from

The point of this file is that an interviewer can pick any line of the code and trace it to a page. Where a construct is my operationalization rather than Beer's or Ashby's, it says so.

| Construct | In the code | Source |
|---|---|---|
| Variety as the count of distinguishable states, or its log₂ | `variety(states, bits=...)`, `variety_of(...)` | Ashby, *An Introduction to Cybernetics* (1956), p. 126 |
| Law of Requisite Variety: "only variety can destroy variety"; outcome variety V_O ≥ V_D − V_R | `requisite(...)`, `RequisiteResult.residual_outcome_bits` | Ashby (1956), p. 207 |
| "Variety absorbs variety" — Beer's management restatement | docstring of `vsm/variety.py` | Beer, *The Heart of Enterprise* (1979), p. 286 |
| Variety engineering: attenuate the disturbance, amplify the regulator, until balanced | `Attenuator`, `Amplifier`, `balance(...)` | Beer (1979), the treatment of attenuators and amplifiers throughout Part Two |
| Channel capacity must exceed the variety of the subsystem it serves; transducer variety must match the channel | `Channel`, `channel_violations(...)` | Beer (1979), the Principles of Organization |
| Systems 1–5; System 3* as a sporadic audit channel | `ViableSystem` fields `s2, s3, s3_star, s4, s5`; `operations` for System 1 | Beer, *Brain of the Firm* (1972; 2nd ed. 1981); *Diagnosing the System for Organizations* (1985) |
| Recursive System Theorem: any viable system contains, and is contained in, a viable system | `System1.subsystem`, `ViableSystem.is_structurally_viable()` recursing | Beer (1972), the Recursive System Theorem |
| The triple vector: actuality, capability, potentiality; productivity, latency, performance | `Metrics` and its properties | Beer (1972) — **wording to verify against the primary text before quoting as his** |
| Algedonic signals: pain/pleasure alarms that escalate up the recursion, bypassing normal routing | `propagate(...)`, `AlgedonicEvent` | Beer (1972; 1979) — the channel is described informally |
| **Threshold held for a timeout of consecutive readings fires one event; a recovery re-arms it** | `propagate(..., threshold, timeout)` | **Mine.** Beer gives no algorithm; this is one defensible, testable operationalization |
| Project Cybersyn as context | README only | Medina, *Cybernetic Revolutionaries* (MIT Press, 2011) |

Two abstractions are deliberately thin. `Attenuator` and `Amplifier` are pure bit-transforms; they do not say *which* filter or *which* delegation does the work, because any such claim would need to be about a real organization. `channel_violations` checks capacity inequalities only; it models neither timing nor noise nor coding.
