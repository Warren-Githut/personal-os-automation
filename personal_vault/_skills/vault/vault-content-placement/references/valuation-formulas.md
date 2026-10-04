# Valuation Formulas — reference bank

## Canonical definitions (Peter Lynch)
- **P/E** = Price ÷ EPS. Lower = cheaper.
- **PEG** = P/E ÷ EPS growth rate (%). <1 = potentially undervalued.
- **PEGY** = P/E ÷ (growth% + dividend yield%). <1 = potentially undervalued.
  - Note: video called it "Peggy" — correct name is **PEGY** (Price/Earnings to Growth & Yield).

## Verification example — GAS §5B (031-GAS/Thesis.md)
FY2025 inputs: P/E = 18.2x, EPS growth = +12.2%, dividend yield = 2.49%.
- PEG = 18.2 / 12.2 = **1.49** ✓
- PEGY = 18.2 / (12.2 + 2.49) = 18.2 / 14.69 = **1.24** ✓
Both match the vault. Source of formulas: YouTube (transcript via `youtube-content` skill), tagged [LOW].

## Edge case — negative growth
FY2024 GAS: growth = -9%. Stored PEGY = 1.72, which does NOT match the formula
(18.2 / (-9 + ~6.8) is nonsensical). When growth is negative, the <1 rule and the
standard denominator break — flag the convention instead of trusting the number.
