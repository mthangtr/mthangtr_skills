#!/usr/bin/env python3
"""Post-launch A/B test sizing (two-proportion z-test, two-sided alpha=0.05, power=0.8 by default).

Usage:
    python scripts/test_plan.py --metric ctr --baseline 0.012 --lift 0.20 --arms 3 --cpm 9 --daily 150
    python scripts/test_plan.py --metric cvr --baseline 0.05 --lift 0.20 --arms 2 --cpc 1.2 --daily 200
    python scripts/test_plan.py --metric ctr --baseline 0.012 --arms 2 --cpm 9 --budget 1500   # -> detectable lift (MDE)

Baselines: use the account's own history. If none, channel reference bands (references/benchmarking.md):
  display CTR 0.1-0.5%, Meta feed CTR ~1-2.5% (median 1.7% traffic obj.), TikTok ~1-1.8%, LinkedIn ~0.4-0.65%.
"""
import argparse, math
from statistics import NormalDist

za = lambda alpha: NormalDist().inv_cdf(1 - alpha / 2)
zb = lambda power: NormalDist().inv_cdf(power)


def n_per_arm(p1, p2, alpha=0.05, power=0.8):
    z = (za(alpha) + zb(power)) ** 2
    return math.ceil(z * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2)


def mde(p, n, alpha=0.05, power=0.8):
    # absolute MDE (equal arms) ~ (za+zb) * sqrt(2 p (1-p) / n)
    return (za(alpha) + zb(power)) * math.sqrt(2 * p * (1 - p) / n)


def plan(metric, baseline, lift=None, arms=2, cpm=None, cpc=None, daily=None, budget=None, alpha=0.05, power=0.8):
    holm_alpha = alpha / max(1, arms - 1)  # conservative (Bonferroni bound for Holm's first step) vs control
    unit = "impressions" if metric == "ctr" else "clicks"
    price = (cpm / 1000.0) if metric == "ctr" else cpc
    lines = [f"### Post-launch test plan ({metric.upper()}, {arms} arms, alpha={alpha} two-sided, power={power}, multiple-arm alpha {holm_alpha:.3f})"]
    if lift is not None:
        p2 = baseline * (1 + lift)
        n = n_per_arm(baseline, p2, alpha=holm_alpha, power=power)
        total = n * arms
        lines.append(f"- Detect {baseline:.2%} -> {p2:.2%} (+{lift:.0%} relative): **{n:,} {unit} per arm**, {total:,} total.")
        if price:
            cost = total * price
            lines.append(f"- Cost ≈ ${cost:,.0f}" + (f"; at ${daily:,.0f}/day ≈ {math.ceil(cost / daily)} days (run ≥7 days regardless for weekly seasonality)." if daily else "."))
    if budget and price:
        n_avail = int(budget / price / arms)
        d = mde(baseline, n_avail, alpha=holm_alpha, power=power)
        lines.append(f"- With ${budget:,.0f}: {n_avail:,} {unit}/arm -> smallest detectable change ≈ {d:.3%} absolute ({d / baseline:.0%} relative). "
                     + ("Too coarse: test fewer arms or bigger concept differences." if d / baseline > 0.5 else ""))
    lines += [
        "- Rules: decide the stop date before launch; no peeking-and-stopping (use sequential tests if you must look early).",
        "- Read CTR only after ≥1,000-2,000 impressions/arm; CPA only after ≥50 conversions/arm or spend ≥2-3x target CPA.",
        "- Kill: CTR < 50% of channel/account median with upper 90% CI still below it; or spend ≥2x target CPA with 0 conversions.",
        "- Scale: significant win vs control AND CPA ≤ target at ≥50 conversions; raise budget ≤20-30% per 48-72h.",
        "- Fatigue: frequency >2.5 (cold) / >4 (retargeting), CTR -15% WoW, or CPM +18% over 2 weeks -> refresh with a NEW concept, not a recolour.",
        "- Meta: Experiments A/B test (separate audiences) or Creative testing tool (2-5 ads, ≤20% budget, ~7 days). TikTok: Split Test, 7-30 days, ≥80% power.",
        "- Log each ad's pre-launch scorecard next to its live CTR/CVR/CPA; after ≥20 ads refit the scorecard weights for this account.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--metric", choices=["ctr", "cvr"], default="ctr")
    ap.add_argument("--baseline", type=float, required=True)
    ap.add_argument("--lift", type=float, default=None, help="relative lift to detect, e.g. 0.2")
    ap.add_argument("--arms", type=int, default=2)
    ap.add_argument("--cpm", type=float, default=None)
    ap.add_argument("--cpc", type=float, default=None)
    ap.add_argument("--daily", type=float, default=None)
    ap.add_argument("--budget", type=float, default=None)
    a = ap.parse_args()
    if a.lift is None and a.budget is None:
        a.lift = 0.2
    print(plan(a.metric, a.baseline, a.lift, a.arms, a.cpm, a.cpc, a.daily, a.budget))
