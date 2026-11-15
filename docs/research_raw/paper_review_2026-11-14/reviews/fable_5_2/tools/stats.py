"""Exact binomial and Fisher arithmetic quoted by the referees. Standard library only."""
from math import comb
from fractions import Fraction

def binom_cdf(k, n, p):
    return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(0, k + 1))

def clopper_pearson(k, n, alpha=0.05):
    lo, hi = 0.0, 1.0
    if k > 0:
        a, b = 0.0, 1.0
        for _ in range(200):
            m = (a + b) / 2
            # P(X >= k | m) = alpha/2
            if 1 - binom_cdf(k - 1, n, m) < alpha / 2: a = m
            else: b = m
        lo = (a + b) / 2
    if k < n:
        a, b = 0.0, 1.0
        for _ in range(200):
            m = (a + b) / 2
            if binom_cdf(k, n, m) > alpha / 2: a = m
            else: b = m
        hi = (a + b) / 2
    return lo, hi

def fisher(a, b, c, d):
    """Two-sided Fisher exact p for table [[a,b],[c,d]] by summing tables no more probable than observed."""
    r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d
    def p(x):
        return Fraction(comb(r1, x) * comb(r2, c1 - x), comb(n, c1))
    obs = p(a)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    two = sum(p(x) for x in range(lo, hi + 1) if p(x) <= obs)
    one = sum(p(x) for x in range(a, hi + 1))
    return float(two), float(one)

print("14/16 Clopper-Pearson 95%:", [round(100 * x, 1) for x in clopper_pearson(14, 16)])
for k, n, name in [(2, 3, "Sol"), (5, 6, "Gemini"), (5, 5, "Opus"), (2, 2, "Grok")]:
    print(f"  {name} {k}/{n}:", [round(100 * x, 1) for x in clopper_pearson(k, n)])
print("Fisher failures 2/16 vs 1/115 (two-sided, one-sided):", fisher(2, 14, 1, 114))
print("Fisher failures 2/16 vs 0/115 (dropping the G12 d249 call conflict):", fisher(2, 14, 0, 115))
print("Fisher 2/16 vs 1/53 (middle category only):", fisher(2, 14, 1, 52))
print("16/188 =", round(100 * 16 / 188, 2), "%; 16/131 =", round(100 * 16 / 131, 2), "%; 16/6989 =", round(100 * 16 / 6989, 3), "%; 58/6989 =", round(100 * 58 / 6989, 2), "%; 338/6989 =", round(100 * 338 / 6989, 2), "%")
# bargaining arithmetic
for name, (a, b, c, d) in {"all swaps": (95, 116, 37, 72), "no Grok authors": (90, 108, 24, 36), "no conflicting openings": (93, 112, 26, 43), "cash bids": (42, 70, 67, 103), "Grok recipient cash bids": (19, 24, 27, 34)}.items():
    print(name, round(100 * (a / b - c / d), 3))
print("thinking table FinBoard (as summed by reviewer) 4/36 vs 10/36 Fisher:", fisher(4, 32, 10, 26))
print("cost/attempt", 141.39 / 8679, "cost/decision", 141.39 / 6989)
