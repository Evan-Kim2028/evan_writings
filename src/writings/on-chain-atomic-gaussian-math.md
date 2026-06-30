---
title: "On-chain Atomic Gaussian Math"
date: "2025-12-01"
collection: latest
tags:
  - writing
  - latest
  - paragraph
source_url: https://paragraph.com/@evandekim/on-chain-atomic-gaussian-math
source_platform: paragraph
slug: on-chain-atomic-gaussian-math
---

## TL;DR

GaussianMove uses the [AAA algorithm](https://arxiv.org/abs/1612.00337) to generate near-optimal rational approximations offline, then evaluates them on-chain via [Horner's method](https://en.wikipedia.org/wiki/Horner%27s_method)—achieving CDF error of 3.35×10⁻⁹ and PPF error of 3.11×10⁻¹³ with predictable gas costs. Sui's native `sui::random` then makes Gaussian sampling operationally simple inside a single transaction. This article describes the constraints, the approximation methods, and several applications once these functions are available as ordinary library calls.

On-chain, Gaussian machinery is usually pushed off to oracles, hidden inside off-chain engines, or avoided entirely because gas and fixed-point arithmetic make it challenging. GaussianMove asks a simple question:

> What does it actually take to compute Φ and Φ⁻¹ on Sui when all you have are integers, fixed-point scaling, and strict gas limits?

We’ll start from the mathematical constraints, choose an approximation strategy that is compatible with those constraints, and then plug the resulting primitives into familiar objects like Black–Scholes, VaR, and Gaussian-shaped AMMs.

---

## Deployed Packages (Sui Testnet)

GaussianMove and its companion Black-Scholes package are deployed on Sui testnet:

| Package | Version | Package ID | Explorer |
| --- | --- | --- | --- |
| **gaussian** | v0.9.0 | `0x66f9087a3d9ae3fe07a5f3c1475d503f1b0ea508d3b83b73b0b8637b57629f7f` | [View](https://suiscan.xyz/testnet/object/0x66f9087a3d9ae3fe07a5f3c1475d503f1b0ea508d3b83b73b0b8637b57629f7f) |
| **black\_scholes** | v0.2.0 | `0x1637ddc0495a8833ebd580224dad7154dfb33477f73d2c7fb41e2b350efa55b3` | [View](https://suiscan.xyz/testnet/object/0x1637ddc0495a8833ebd580224dad7154dfb33477f73d2c7fb41e2b350efa55b3) |

**Repositories:**

* [move-gaussian](https://github.com/Evan-Kim2028/move-gaussian) — Core Gaussian library (399 tests)
* [move-black-scholes](https://github.com/Evan-Kim2028/move-black-scholes) — European options pricing (83 tests)

---

## Part I: The Mathematical Problem

Why is Gaussian math hard on-chain? The difficulty is not just gas; it’s that you only get integers, fixed-point scaling, and inverse functions that amplify small errors, which constrains the approximation method choices.

### Gaussian Math in Traditional Finance

Gaussian-based models are standard tools in traditional finance.

* The [Black–Scholes–Merton model](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model) for European options pricing literally contains Φ(d₁) and Φ(d₂), where Φ is the standard normal CDF.
* Risk measures such as [Value at Risk](https://en.wikipedia.org/wiki/Value_at_risk) and Expected Shortfall often assume (log)normal returns and use the inverse CDF Φ⁻¹(α) to convert a confidence level α into a loss threshold.
* Many factor and term-structure models linearize around Gaussian assumptions even when reality is heavier-tailed.

In banks and brokerages, these functions are evaluated using high-quality numerical libraries (BLAS/LAPACK, Boost, SciPy, etc.), and their error properties are well understood. The question here is what it takes to bring that level of Gaussian math *on-chain*, where the only primitives are integer arithmetic and fixed-point representations.

### From Off-Chain Models to On-Chain Systems

DeFi derivatives protocols already lean heavily on Gaussian-style thinking, but most of the heavy numerical work happens off-chain:

* [Lyra](https://mirror.xyz/lyra.eth/JRj-8JInwtW8jp5y6QzyUHq0suTcH_B1iGO7V5LYwVQ) (~$58M TVL, one of the largest on-chain options protocols) prices options with Black–Scholes-style formulas but relies on [Chainlink price feeds](https://blog.lyra.finance/lyra-integrates-chainlink-price-feeds/) and off-chain Greeks; it does *not* evaluate Φ/Φ⁻¹ directly on-chain.
* [Hegic](https://www.hegic.co/), [Dopex](https://dopex.io/), [Rysk](https://docs.rysk.finance/), and [Valorem](https://valorem.xyz/) use a mix of RFQ mechanisms, oracles, and simplified pricing rules rather than full on-chain Gaussian math.
* [Panoptic](https://ar5iv.labs.arxiv.org/html/2204.14232) is explicitly oracle-free but achieves this by deriving option payoffs from [Uniswap v3](https://uniswap.org/whitepaper-v3.pdf) LP mechanics instead of computing Gaussian functions.
* [Primitive RMM-01](https://primitive.mirror.xyz/l5F1BLMhfmcm_B1R2w-by003_oiAz2-Ir_Jj_rCvGCs) together with [solstat](https://github.com/primitivefinance/solstat) is the clearest EVM example of explicit on-chain Gaussian CDF usage, but the protocol has since closed down.

In practice, most production DeFi options protocols avoid full on-chain Gaussian computation. They either use oracles to import off-chain pricing, derive prices from AMM mechanics, or accept simplified models. The few that attempted full on-chain Black–Scholes (like early Primitive) faced gas costs and complexity that limited adoption.

**So why build this?**

Three reasons:

1. **The landscape is changing.** Sui’s native randomness and lower compute costs make on-chain statistical computation more practical than on EVM.
2. **Research infrastructure matters.** Even if production protocols use hybrid approaches, having audited, well-documented Gaussian primitives enables experimentation. The Paradigm [pm-AMM](https://www.paradigm.xyz/2024/11/pm-amm) paper (2024) and [Distribution Markets](https://www.paradigm.xyz/2024/12/distribution-markets) work show continued research interest in Gaussian-based mechanisms.
3. **The mathematical problem is nontrivial.** Computing Φ⁻¹(p) without floating-point is a substantive applied mathematics problem, independent of any particular application.

---

The fundamental question is deceptively simple: **how do you compute Φ⁻¹(p) when your only arithmetic primitives are integer addition, subtraction, multiplication, and division?** This is a timeless numerical analysis challenge from the 1960s—blockchain merely adds gas costs and determinism constraints.

#### Key Constraints for On-Chain Gaussian Math

* **Fixed-point arithmetic constraints.** On-chain environments (Solidity, Move, etc.) operate with integers and implicit scaling (typically WAD = 10¹⁸). This introduces overflow risk for `(a * b) / SCALE`, truncation error in division, and a hard floor on the smallest representable probabilities. Practical accuracy is limited by cumulative rounding, even though u256 offers ~77 decimal digits of intermediate precision.
* **Randomness source.** Gaussian sampling via inverse transform requires a high-quality uniform variate U ∈ (0,1). On EVM/Solana/Aptos this usually comes from external VRF providers such as [Chainlink VRF](https://docs.chain.link/vrf) or [Switchboard VRF](https://docs.switchboard.xyz/product-documentation/randomness), adding multi-transaction flows, callbacks, and gas. On Sui, `sui::random` exposes a [Random](https://docs.sui.io/references/framework/sui_sui/random) object that can be consumed inside a single transaction.
* **Inverse functions amplify errors.** Even if Φ(x) is approximated accurately, inverting it to obtain Φ⁻¹(p) amplifies small forward errors, especially in the tails where d/dp Φ⁻¹(p) grows large. Classical work such as [Algorithm AS 241](https://www.jstor.org/stable/2347330) (Wichura) and [Acklam's normal quantile function](https://stackedboxes.org/2017/05/01/acklams-normal-quantile-function/) emphasizes careful piecewise design and tail handling; GaussianMove follows the same philosophy with AAA-based piecewise approximations.

---

### Fixed-Point Constraints: Working Without Floats

Before we talk about algorithms, we need to make peace with a simple fact: on-chain, there are no floats—only integers with a fixed scale. That single choice drives almost every design decision in GaussianMove.

DeFi universally uses WAD scaling: 1.0 is represented as 10¹⁸. This gives 18 decimal places of precision, sufficient for most financial calculations (basis points are 10⁻⁴), but it also means all transcendental functions (exp, ln, sqrt) must be realized as integer-based polynomial or rational approximations.

```
const SCALE: u256 = 1_000_000_000_000_000_000;  // 10^18

/// Fixed-point multiplication: (a × b) / SCALE
public fun mul_wad(a: u256, b: u256): u256 {
    (a * b) / SCALE  // u256 intermediate prevents overflow
}

/// Fixed-point division: (a × SCALE) / b
public fun div_wad(a: u256, b: u256): u256 {
    (a * SCALE) / b
}
```

#### Precision Hierarchy

Understanding where precision is lost is crucial for error analysis:

```
Layer                          Precision       Notes
─────────────────────────────────────────────────────
1. Off-chain AAA fitting       ~10⁻¹⁴         Dominated by algorithm tolerance
2. Coefficient quantization    ~10⁻¹⁸         Negligible (WAD has 18 digits)
3. On-chain Horner rounding    ~10⁻¹⁵         ~0.5 ULP per operation
4. WAD representation          10⁻¹⁸          Hard floor
─────────────────────────────────────────────────────
Current achieved:              3.35×10⁻⁹      CDF
Theoretical floor:             ~10⁻¹⁵
```

The precision floor (~10⁻¹⁵) comes from accumulated rounding in Horner evaluation: each of the ~11 iterations loses approximately 0.5 ULP (unit in last place), totaling 5-10 ULP. In practical terms, the approximation method is not the bottleneck here—the fixed-point evaluation is.

### Approximation Theory: Why AAA?

Once you accept fixed-point arithmetic and u256 as your playing field, the next question is how to approximate Φ and Φ⁻¹ themselves.

#### The Landscape of Approximation Methods

Several approaches exist for approximating Φ and Φ⁻¹:

| Method | Era | Pros | Cons |
| --- | --- | --- | --- |
| **Taylor series** | 1700s | Simple, well-understood | Slow convergence, many terms |
| **Padé approximation** | 1890s | Better than Taylor for same degree | Non-trivial to compute |
| **Abramowitz-Stegun** | 1964 | Battle-tested, industry standard | Requires exp(), fixed formulas |
| **Chebyshev polynomials** | 1960s | Near-optimal for polynomials | Limited to polynomial (not rational) |
| **AAA (Adaptive Antoulas-Anderson)** | 2018 | Near-optimal rational, automatic | Requires offline toolchain |

GaussianMove uses AAA because it produces **near-optimal rational approximations automatically**, avoiding the need to hand-tune coefficients for each function.

#### The AAA Algorithm

AAA (Nakatsukasa et al., 2018) is a greedy algorithm that iteratively builds a barycentric rational approximation:

```
r(x) = Σⱼ (wⱼ × fⱼ) / (x - zⱼ)
       ─────────────────────────
       Σⱼ wⱼ / (x - zⱼ)
```

Where:

* **zⱼ** (nodes): Sample points chosen adaptively
* **wⱼ** (weights): Barycentric weights computed by the algorithm
* **fⱼ** (values): Function values at nodes (from high-precision baseline)

The algorithm's key property: it produces approximations close to the theoretical best rational function of a given degree, without requiring manual coefficient tuning. In practice, this lets us treat “pick a good rational approximation” as a design-time task handled by Python, not an on-chain concern.

#### From Barycentric to Polynomial Form

For on-chain evaluation, we convert the barycentric form to explicit polynomials:

```
r(x) = P(x) / Q(x) = (p₀ + p₁x + p₂x² + ... + pₙxⁿ) / (q₀ + q₁x + ... + qₘxᵐ)
```

This conversion happens offline. The Move code only evaluates P(x) and Q(x) using Horner's method, then computes their ratio.

#### Comparison with Morpheus (Aptos)

The Morpheus PM-AMM on Aptos uses a different approach: Abramowitz-Stegun (1964) for CDF and Acklam (2000) for inverse CDF, with Newton-Raphson refinement.

| Aspect | Morpheus (Aptos) | GaussianMove (Sui) |
| --- | --- | --- |
| **CDF algorithm** | Abramowitz-Stegun polynomial | AAA rational approximation |
| **CDF raw error** | ~7.5×10⁻⁸ | ~3.35×10⁻⁹ (10× better) |
| **PPF algorithm** | Acklam + Newton refinement | AAA piecewise + optional Newton |
| **Requires exp()?** | Yes (for PDF, Newton) | Only for Newton refinement |
| **Code complexity** | High (piecewise, multi-algorithm) | Medium (unified pipeline) |

Both approaches are valid. Morpheus prioritizes maximum precision with proven classical formulas; GaussianMove prioritizes a unified, auditable pipeline with modern approximation theory.

#### Piecewise Strategy for Φ⁻¹

The inverse CDF presents special challenges because its derivative approaches infinity as p → 0 or p → 1. A single rational approximation cannot maintain accuracy across the full domain.

GaussianMove uses three regions:

**Region 1: Central (0.02 ≥ p ≥ 0.98)**

* Direct AAA approximation of Φ⁻¹(p)
* Expected error: ~3.11×10⁻¹³

**Region 2: Lower tail (10⁻¹⁰ ≤ p < 0.02)**

* Transform: t = √(-2 ln(p))
* Approximate Φ⁻¹ as function of t
* Expected error: ~2.03×10⁻¹³

**Region 3: Upper tail (0.98 < p ≤ 1 - 10⁻¹⁰)**

* Symmetry: Φ⁻¹(p) = -Φ⁻¹(1-p)
* Reuses lower tail approximation

This piecewise approach mirrors classical algorithms (Wichura AS 241, Moro/Jäckel) but fits coefficients via AAA rather than reusing floating-point polynomials.

At this point, we have a clear picture of the constraints (fixed-point, randomness, error amplification) and a modern approximation strategy (AAA + piecewise design). Next we need to quantify how much error is actually left and how it propagates into financial models.

---

### Error Analysis and Bounds

Error bounds link approximation theory to practical finance. If the approximation error is many orders of magnitude smaller than model uncertainty and oracle noise, then from a DeFi perspective the numerical contribution of the approximation is relatively small.

#### Current Error Budget

From GaussianMove v0.9.0 coefficient generation:

| Function | Max Absolute Error | Notes |
| --- | --- | --- |
| **Φ (CDF)** | 3.35×10⁻⁹ | WAD output ≤ 3.35×10⁹ raw units |
| **φ (PDF)** | 7.61×10⁻¹⁵ | Negligible vs WAD quantization |
| **Φ⁻¹ central** | 3.11×10⁻¹³ | Applies on [0.02, 0.98] |
| **Φ⁻¹ tail** | 2.03×10⁻¹³ | Inputs clamped to (10⁻¹⁰, 1-10⁻¹⁰) |

These errors are validated against mpmath with 100-digit precision baselines.

#### How Error Propagates into Financial Models

**For VaR calculations:**

```
VaR(α) = μ + σ × Φ⁻¹(α)
```

With |Φ⁻¹ error| ≤ 3.11×10⁻¹³, the VaR error is:

```
|VaR error| ≤ σ × 3.11×10⁻¹³
```

For σ = $10,000 (typical portfolio volatility), this is $3.11×10⁻⁹—far below any practical threshold.

**For Black-Scholes:** The Greeks (Delta, Gamma, Vega) involve Φ(d₁) and φ(d₁). With CDF error 3.35×10⁻⁹:

* Delta error ≤ 3.35×10⁻⁹ (direct)
* Gamma involves φ, error ≤ 7.61×10⁻¹⁵
* Vega scales by √T, error remains negligible

**Comparison with model uncertainty:**

* Volatility estimation error: typically 5-20% (10⁻¹ to 10⁰)
* Oracle price staleness: seconds to minutes of drift
* Approximation error: 10⁻⁹ to 10⁻¹³

**Conclusion**: Approximation error is 6-10 orders of magnitude smaller than model/oracle uncertainty. For DeFi applications, even 10⁻⁸ precision (solgauss level) is overkill.

#### Domain Clamping

Probability inputs are clamped to (ε, 1-ε) with ε = 10⁻¹⁰ × WAD. This corresponds to approximately ±6.3σ—beyond which fixed-point arithmetic cannot meaningfully distinguish probabilities.

Applications requiring fatter tails (e.g., extreme risk modeling) should document this limitation and consider alternative approaches.

With constraints, approximation strategy, and error budgets in place, we can now switch from “math and theory” to “engineering”: how to turn all of this into a reproducible Python→Move pipeline.

---

## Part II: The Implementation

Part II describes how GaussianMove turns the previous section’s numerical choices into concrete code. The design-time Python pipeline finds and validates rational approximations; the runtime Move code evaluates them cheaply and deterministically on-chain.

### The Python-to-Move Pipeline

GaussianMove follows a "design-time vs runtime" separation:

```
┌─────────────────────────────────────────────────────────┐
│  PYTHON (Design-Time / Offline)                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 1. Sample function with mpmath (50+ digits)     │    │
│  │ 2. Run AAA algorithm (SciPy)                    │    │
│  │ 3. Convert barycentric → polynomial coeffs      │    │
│  │ 4. Quantize to WAD-scaled integers              │    │
│  │ 5. Validate accuracy, export to Move            │    │
│  └─────────────────────────────────────────────────┘    │
│                           │                             │
│                           ▼                             │
│                  [coefficient arrays]                   │
└───────────────────────────┼─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  MOVE (Runtime / On-Chain)                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 1. Load pre-computed coefficients (constants)   │    │
│  │ 2. Evaluate P(x), Q(x) using Horner's method    │    │
│  │ 3. Compute P(x) / Q(x)                          │    │
│  │ 4. Apply domain clamping and output bounds      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**Why this matters for auditability**: All numerically delicate work (node selection, coefficient fitting, convergence analysis) happens in a Python toolchain that can be inspected, re-run, and validated. The on-chain Move code is a small, predictable evaluation kernel.

### Horner's Method: O(n) Polynomial Evaluation

Evaluating P(x) = c₀ + c₁x + c₂x² + ... + cₙxⁿ naively requires O(n²) multiplications (computing x², x³, etc.). Horner's method restructures as:

```
P(x) = c₀ + x(c₁ + x(c₂ + ... + x(cₙ)))
```

This is O(n)—one multiplication and one addition per term.

```
/// Horner's method for polynomial evaluation
public fun horner_eval(x: u256, coeffs: &vector<u256>): u256 {
    let n = vector::length(coeffs);
    if (n == 0) { return 0 };
    
    // Start with highest-degree coefficient
    let mut result = *vector::borrow(coeffs, n - 1);
    
    // Work backwards: result = result × x + coeffs[i]
    let mut i = n - 1;
    while (i > 0) {
        i = i - 1;
        result = mul_wad(result, x);
        result = result + *vector::borrow(coeffs, i);
    };
    
    result
}
```

For degree-11 polynomials (typical for GaussianMove), this is 11 iterations—predictable gas cost, numerical stability, and minimal intermediate overflow risk.

### Signed WAD for Negative Quantiles

The standard normal distribution is symmetric around zero, so Φ⁻¹(p) can be negative. Move lacks native signed integers, so GaussianMove uses a `SignedWad` type:

```
public struct SignedWad has copy, drop, store {
    magnitude: u256,
    negative: bool,
}
```

Operations track sign explicitly:

```
public fun add(a: SignedWad, b: SignedWad): SignedWad {
    if (a.negative == b.negative) {
        // Same sign: add magnitudes
        SignedWad { magnitude: a.magnitude + b.magnitude, negative: a.negative }
    } else {
        // Different signs: subtract smaller from larger
        if (a.magnitude >= b.magnitude) {
            SignedWad { magnitude: a.magnitude - b.magnitude, negative: a.negative }
        } else {
            SignedWad { magnitude: b.magnitude - a.magnitude, negative: b.negative }
        }
    }
}
```

### v0.9.0 API Design Decisions

**Strict PPF Domain Validation**

The `ppf(p)` function enforces strict domain validation:

```
// Aborts with EProbOutOfDomain (302) if p is outside valid domain
let z = core::ppf(0);  // Aborts! p=0 is outside (EPS, 1-EPS)

// For sampling, use ppf_from_u64 which maps any u64 to valid domain
let z = core::ppf_from_u64(random_seed);  // Always succeeds
```

**Rationale:** Explicit failure surfaces invalid inputs immediately rather than silently clamping. For sampling use cases, `ppf_from_u64(seed)` provides a safe alternative that maps any u64 into the valid domain.

**SignedWad Fields**

The `SignedWad` struct uses short field names for ergonomics:

```
public struct SignedWad has copy, drop, store {
    mag: u256,   // magnitude (absolute value)
    neg: bool,   // true if negative
}
```

Accessor methods (`abs()`, `is_negative()`) provide a stable API.

### Sui's Randomness Advantage

With the mathematical machinery in place, Sui's `sui::random` completes the picture for sampling:

```
use sui::random::Random;
use gaussian::core;
use gaussian::signed_wad::SignedWad;

public entry fun sample_standard_normal(r: &Random, ctx: &mut TxContext): SignedWad {
    let mut gen = random::new_generator(r, ctx);
    
    // Generate uniform in (0, 1), avoiding exact 0 or 1
    let u = random::generate_u256_in_range(&mut gen, 1, WAD - 1);
    
    // Transform via inverse CDF
    core::ppf(u)
}
```

**Single transaction**: No VRF callback or second transaction.

**Validator consensus security**: Randomness derived from distributed validator set, not manipulable by any single party.

**Native integration**: `&Random` is a first-class Sui object, passed directly to functions that need it.

This is the one place where Sui provides a genuine platform advantage—but it only matters because the mathematical foundation (accurate Φ⁻¹ approximation) is already in place.

Taken together, the Python pipeline, Horner evaluation, SignedWad representation, and `sui::random` give us a complete implementation story. The next natural question is: what do you actually *do* with these primitives?

---

## Part III: Applications

Part III sketches how Φ and Φ⁻¹ plug into familiar financial formulas. These are not full protocol designs; they are case studies meant to show that once GaussianMove exists, Black–Scholes, VaR, and Gaussian-shaped AMMs can be expressed directly in terms of its API.

### Black-Scholes as a Mathematical Case Study

The Black-Scholes formula for European call options is:

```
C = S₀Φ(d₁) - Ke^(-rT)Φ(d₂)
```

where:

```
d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
d₂ = d₁ - σ√T
```

#### The Mathematical Components

**Computing d₁ requires:**

1. `ln(S₀/K)` — natural logarithm (transcendental)
2. `σ√T` — square root (algebraic but irrational)
3. Division and addition — straightforward in fixed-point

**Computing the option price requires:** 4. `Φ(d₁)`, `Φ(d₂)` — normal CDF (the hard part) 5. `e^(-rT)` — exponential (transcendental)

GaussianMove provides the CDF. The companion `move-black-scholes` package implements the transcendental helpers:

```
// From black_scholes::d_values
public fun compute_d1(
    spot: u256,      // S₀ in WAD
    strike: u256,    // K in WAD
    time: u256,      // T in WAD (years)
    rate: u256,      // r in WAD
    vol: u256        // σ in WAD
): SignedWad {
    // ln(S/K)
    let log_moneyness = transcendental::ln_wad(div_wad(spot, strike));
    
    // (r + σ²/2)T
    let drift = mul_wad(rate + mul_wad(vol, vol) / 2, time);
    
    // σ√T
    let vol_sqrt_t = mul_wad(vol, transcendental::sqrt_wad(time));
    
    // d₁ = (ln(S/K) + drift) / (σ√T)
    signed_wad::div(
        signed_wad::add(log_moneyness, drift),
        vol_sqrt_t
    )
}
```

The transcendental functions (`ln_wad`, `sqrt_wad`, `exp_wad`) are also implemented via polynomial approximation, following the same AAA pipeline philosophy. In practice, this means Black–Scholes-style pricing on Sui becomes a matter of wiring together a few math primitives.

---

### Empirical Validation: Live Testnet Transactions

The following transactions demonstrate GaussianMove in production, pricing ATM European options (S=$100, K=$100, T=1yr, r=5%, σ=20%):

**Transaction 1: Option Pricing**

* TX: `CdAxPyw1T7tF4xMPpfVqVhJMDL4Xy6zeyC24YeQxpjJt`
* Results: Call=$10.45, Put=$5.57, Put-Call Parity=✓

**Transaction 2: Greeks Calculation**

* TX: `48TFYV87TXRJMUuCzoMZ4T5CLVsFgQoT1fptR2w7NXPv`
* Results: Δ=0.637, Γ=0.019, ν=37.52, θ=-6.41, ρ=53.23

**Comparison with scipy reference:**

| Metric | On-Chain Result | scipy Reference | Error |
| --- | --- | --- | --- |
| Call Price | $10.4506 | $10.4506 | <0.01% |
| Put Price | $5.5735 | $5.5735 | <0.01% |
| Delta | 0.6368 | 0.6368 | <0.01% |
| Gamma | 0.0188 | 0.0188 | <0.01% |

These results validate that GaussianMove's ~10⁻⁹ CDF error propagates to <0.01% pricing error in Black-Scholes applications.

---

## Part IV: Ecosystem Context

Part IV places GaussianMove alongside existing Gaussian and options libraries in EVM and other ecosystems. The goal is not to declare a winner, but to show where a Sui-native, AAA-based library fits on the accuracy/gas/complexity frontier.

### EVM Gaussian Libraries: A Brief Comparison

The EVM ecosystem has seen two waves of Gaussian implementations:

**First wave (2014-2022)**: Production-driven

* `errcw/gaussian` (2014): JavaScript reference
* `primitivefinance/solstat` (2022): First DeFi library, ~10⁻⁷ error, ~5,000 gas

**Second wave (2024)**: Research-driven

* `GA006/gaussian-cdf`: Zelen-Severo polynomial, ~10⁻⁸ error
* `0xknxwledge/DegeGauss`: ABDK 128-bit float, ~10⁻¹⁶ error, ~53,000 gas
* `cairoeth/solgauss`: Rational Chebyshev, ~10⁻⁸ error, ~600 gas, includes PPF

**Key insight**: solgauss achieves the best gas/accuracy Pareto frontier via rational approximation—the same approach GaussianMove uses, but with AAA instead of hand-tuned Chebyshev coefficients.

### Algorithm Comparison

| Library | Algorithm | CDF Error | PPF? | Notes |
| --- | --- | --- | --- | --- |
| solstat | Abramowitz-Stegun | 10⁻⁷ | No | Uses exp(), high gas |
| solgauss | Rational Chebyshev | 10⁻⁸ | Yes | No exp() for CDF |
| DegeGauss | ABDK 128-bit float | 10⁻¹⁶ | No | Extreme precision, extreme gas |
| Morpheus | A-S + Acklam + Newton | 10⁻¹⁵ | Yes | Most complete, most complex |
| **GaussianMove** | AAA rational | 10⁻⁹ | Yes | v0.9.0, 399 tests, sui::random |

GaussianMove occupies a distinct position: better accuracy than solgauss, lower complexity than Morpheus, and native randomness integration that no EVM library can match.

---

## Conclusion

We started with a simple question: how do you compute Φ and Φ⁻¹ on a chain that only speaks integers? GaussianMove's answer is to treat this as an approximation-theory problem first, and an engineering problem second.

Concretely, GaussianMove:

1. Uses modern **AAA rational approximation** to generate near-optimal fits for Φ and Φ⁻¹ offline.
2. Enforces explicit **error budgets** (CDF 3.35×10⁻⁹, PPF 3.11×10⁻¹³) validated against high-precision baselines.
3. Wraps everything in an **auditable Python→Move pipeline** and a small, deterministic on-chain evaluation kernel.
4. Leverages Sui's **native randomness** so Gaussian sampling fits cleanly into single-transaction flows.

Whether or not DeFi fully embraces on-chain Gaussian math, it is useful to have a transparent implementation available.

---

## References

### Approximation Theory

* Nakatsukasa, Y., Sète, O., & Trefethen, L. N. (2018). The AAA algorithm for rational approximation. *SIAM J. Sci. Comput.*, 40(3), A1494-A1522. [arXiv:1612.00337](https://arxiv.org/abs/1612.00337)
* Nakatsukasa, Y., & Trefethen, L. N. (2023). [The first five years of the AAA algorithm](https://arxiv.org/abs/2312.03565). arXiv:2312.03565.
* Nakatsukasa, Y., & Trefethen, L. N. (2025). [Applications of AAA rational approximation](https://arxiv.org/abs/2510.16237). *Acta Numerica*. arXiv:2510.16237.
* Driscoll, T. A., Nakatsukasa, Y., & Trefethen, L. N. (2024). [AAA Rational Approximation on a Continuum](https://tobydriscoll.net/_docs/driscoll-rational-approximation-continuum-2024.pdf). *SIAM J. Sci. Comput.*, 46(2), A929-A952.

### Classical Algorithms for Normal Distribution

* Abramowitz, M., & Stegun, I. A. (1964). *Handbook of Mathematical Functions*. Ch. 26.2.17.
* Wichura, M. J. (1988). Algorithm AS 241: The Percentage Points of the Normal Distribution. *Applied Statistics*, 37(3), 477-484.
* Cody, W. J. (1969). Rational Chebyshev Approximations for the Error Function. *Mathematics of Computation*, 23(107).
* Acklam, P. J. (2000). [An algorithm for computing the inverse normal cumulative distribution function](https://stackedboxes.org/2017/05/01/acklams-normal-quantile-function/). (See also [John D. Cook's literate program](https://www.johndcook.com/normal_cdf_inverse.html))
* Koopman, R. (2025). [Some Simple Full-Range Inverse-Normal Approximations](https://doi.org/10.33993/jnaat541-1434). *Journal of Numerical Analysis and Approximation Theory*, 54(1).

### Horner's Method and Polynomial Evaluation

* Graillat, S., et al. (2024). [Accurate Horner methods in real and complex floating-point arithmetic](https://link.springer.com/article/10.1007/s10543-024-01017-w). *BIT Numerical Mathematics*, 64, article 17.
* Graillat, S., Langlois, P., & Louvet, N. (2009). [Algorithms for accurate, validated and fast polynomial evaluation](https://link.springer.com/article/10.1007/BF03186531). *Japan Journal of Industrial and Applied Mathematics*, 26(2), 191-214.
* [Horner's method - Wikipedia](https://en.wikipedia.org/wiki/Horner%27s_method)

### Fixed-Point Arithmetic in DeFi

* RareSkills. (2024). [Fixed Point Arithmetic in Solidity](https://rareskills.io/post/solidity-fixed-point). (Comprehensive tutorial on WAD/RAY standards)
* [PRBMath](https://github.com/PaulRBerg/prb-math): Solidity library for advanced fixed-point math.
* [ds-math](https://github.com/dapphub/ds-math): Original DappHub WAD/RAY implementation.
* [brine-fp](https://github.com/zfedoran/brine-fp): Fixed-point math library with logarithmic and exponential functions for blockchain.

### Solidity Gaussian Implementations

* [primitivefinance/solstat](https://github.com/primitivefinance/solstat): First production DeFi Gaussian library (Primitive RMM-01).
* [cairoeth/solgauss](https://github.com/cairoeth/solgauss): Rational Chebyshev approximation, most complete API.
* [0xknxwledge/DegeGauss](https://github.com/0xknxwledge/DegeGauss): ABDK 128-bit floating-point approach.
* [simontianx/OnChainRNG/GaussianRNG](https://github.com/simontianx/OnChainRNG/tree/main/GaussianRNG): CLT-based Gaussian approximation.
* [araghava/cairo-black-scholes](https://github.com/araghava/cairo-black-scholes): Black-Scholes on StarkNet.
* [opynfinance/BlackScholes](https://github.com/opynfinance/BlackScholes): Opyn's Black-Scholes implementation.

### Move Implementations

* [GaussianMove (move-gaussian)](https://github.com/Evan-Kim2028/move-gaussian) — v0.9.0, Package: `0x66f9087a3d9ae3fe07a5f3c1475d503f1b0ea508d3b83b73b0b8637b57629f7f`
* [BlackScholes (move-black-scholes)](https://github.com/Evan-Kim2028/move-black-scholes) — v0.2.0, Package: `0x1637ddc0495a8833ebd580224dad7154dfb33477f73d2c7fb41e2b350efa55b3`
* [Morpheus PM-AMM (Aptos)](https://github.com/Apostlex0/PredictionMarket_AMM)

### AMMs and Options Protocols

* Evans, A., Angeris, G., & Chitra, T. (2021). [Introducing Primitive RMM-01](https://primitive.mirror.xyz/l5F1BLMhfmcm_B1R2w-by003_oiAz2-Ir_Jj_rCvGCs). Primitive Finance.
* Sterrett, E., & Jepsen, W. (2022). [Replicating Portfolios: Constructing Permissionless Derivatives](https://arxiv.org/abs/2205.09890). arXiv:2205.09890.
* [RMM Primer](https://primitive.mirror.xyz/Audtl29HY_rnhN4E2LwnP7-zjDcDGAyXZ4h3QpDeajg): Friendly guide to Primitive.
* [Primitive Library Documentation](https://library.primitive.xyz/)
* Moallemi, C., & Robinson, D. (2024). [pm-AMM: A Uniform AMM for Prediction Markets](https://www.paradigm.xyz/2024/11/pm-amm). Paradigm.
* White, D. (2024). [Distribution Markets](https://www.paradigm.xyz/2024/12/distribution-markets). Paradigm.

### DeFi Risk Management and VaR

* Chainrisk. (2024). [VaR Methodology for DeFi](https://www.chainrisk.xyz/blog-posts/var-methodology).
* Gauntlet. (2023). [Improved VaR Methodology](https://medium.com/gauntlet-networks/improved-var-methodology-9f4f0c4cdb6f).
* GARP. (2024). [Digital-Asset Risk Management: VaR Meets Cryptocurrencies](https://www.garp.org/risk-intelligence/market/digital-asset-risk-241018).
* Aufiero, S., et al. (2025). [Mapping Microscopic and Systemic Risks in TradFi and DeFi](https://arxiv.org/abs/2508.12007). arXiv:2508.12007.
* KernelDAO. (2024). [Traditional vs DeFi Risk Management: A Quantitative Comparison](https://blogs.kerneldao.com/blog/traditional-vs-defi-risk-management-a-quantitative-comparison).

### Black-Scholes in DeFi

* Polygon. (2022). [Black Scholes Merton Model to Price DeFi Options](https://polygontech.medium.com/black-scholes-merton-model-to-price-defi-options-part-1-a-tale-of-the-king-with-torn-clothes-dff043eadea6).
* Chainlink. (2020). [Build a DeFi Call Option Exchange With Chainlink Price Feeds](https://blog.chain.link/defi-call-option-exchange-in-solidity/).
* Auctus. (2020). [ACO Black-Scholes: A Pooled Liquidity Model for Options Powered by Chainlink](https://blog.auctus.org/aco-black-scholes-a-pooled-liquidity-model-for-options-powered-by-chainlink-is-now-live-9638dccf1825).
* Panoptic. (2024). [How to Price Perpetual Options: Five Models Compared](https://panoptic.xyz/research/perpetual-option-pricing-model-comparison).

### Sui Documentation

* [Sui Randomness Guide](https://docs.sui.io/guides/developer/advanced/randomness-onchain)
* [sui::random Framework Reference](https://docs.sui.io/references/framework/sui_sui/random)

### Tools

* [SciPy AAA](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.AAA.html)
* [mpmath (Arbitrary Precision)](https://mpmath.org/)
* [baryrat (AAA Implementation)](https://github.com/c-f-h/baryrat)
* [SciPy PINV (Polynomial interpolation based INVersion of CDF)](https://docs.scipy.org/doc/scipy/tutorial/stats/sampling_pinv.html)
