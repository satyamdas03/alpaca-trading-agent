"""Formal definitions of the admissible density class and continuum functional.

This module is intentionally independent of c42_kband.py so that the theorem
machinery can be read and tested on its own.
"""
from dataclasses import dataclass
from typing import Callable
import numpy as np
from numpy.polynomial.legendre import leggauss


@dataclass
class AdmissibleDensity:
    """Represents ρ ∈ 𝒫.

    Attributes
    ----------
    alpha : complex
        The parameter in the first block ρ(u) = 1 - α on [0, tau].
    tau : float
        End of the first block (must be > 0).
    bands : list[tuple[float, float, complex]]
        Each tuple is (start, end, value) for bands on (tau, 1].
        The union of intervals must cover (tau, 1] without overlap.
    """
    alpha: complex
    tau: float
    bands: list[tuple[float, float, complex]]

    def __post_init__(self):
        if self.tau <= 0:
            raise ValueError("tau must be positive")
        if self.alpha.real <= 0:
            raise ValueError("Re(alpha) must be positive")
        if not self.bands:
            # single-band case: empty tail means ρ = 1 (free block) on (tau,1]
            return
        # basic sanity: intervals sorted and within (tau,1]
        prev_end = self.tau
        for start, end, _ in self.bands:
            if not (start == prev_end and end > start and end <= 1.0):
                raise ValueError(f"Invalid band {(start, end)} after tau={self.tau}")
            prev_end = end
        if prev_end > 1.0 + 1e-12:
            raise ValueError("Bands must not extend beyond 1")
        # A gap at the end (prev_end < 1) is the implicit free block where ρ = 1.

    def __call__(self, u: float | np.ndarray) -> complex | np.ndarray:
        """Evaluate ρ(u)."""
        u = np.asarray(u, dtype=float)
        scalar = u.ndim == 0
        u = np.atleast_1d(u)
        # Default to the implicit free block value 1 on (last_band_end, 1].
        out = np.full_like(u, 1.0 + 0.0j, dtype=complex)
        mask_first = u <= self.tau
        out[mask_first] = 1.0 - self.alpha
        for start, end, val in self.bands:
            mask = (u > start) & (u <= end)
            out[mask] = val
        return out.item() if scalar else out


def density_from_kband_params(params: np.ndarray, k: int) -> AdmissibleDensity:
    """Convert the flat parameter vector used by c42_kband.py to AdmissibleDensity.

    This layout is byte-compatible with c42_kband.py: for k >= 3 the internal
    cutoffs are encoded as fractions f_j in (0,1) and mapped to absolute cutoffs
    by the same formula used in c42_kband._cutoffs_from_raw:

        t_j = t1 + f_j * (1 - 2*t1)      for j = 1, ..., k-2

    The first block ends at tau = t1, the internal bands occupy (t_j, t_{j+1}],
    and the final cutoff is always t_k = 1 - t1 (the implicit free block).

    Parameter layout for k bands (3k - 1 real numbers):
        [t1,
         f_1, ..., f_{k-2},                # only for k >= 3; fractions in (0,1)
         Re(alpha), Im(alpha),
         Re(eta_2), Im(eta_2), ..., Re(eta_k), Im(eta_k)]
    For k=2: [tau, Re(alpha), Im(alpha), Re(eta), Im(eta)]
    """
    params = np.asarray(params, dtype=float)
    expected_len = (k - 1) + 2 + 2 * (k - 1)
    if len(params) != expected_len:
        raise ValueError(f"Expected {expected_len} parameters for k={k}, got {len(params)}")

    if k == 2:
        tau = float(params[0])
        alpha = complex(params[1], params[2])
        eta = complex(params[3], params[4])
        # Last cutoff is tk = 1 - t1; the free block (tk, 1] is implicit.
        bands = [(tau, 1.0 - tau, eta)]
        return AdmissibleDensity(alpha=alpha, tau=tau, bands=bands)

    # k >= 3: internal entries are fractions; map to absolute cutoffs.
    t1 = float(params[0])
    tk = 1.0 - t1
    scale = tk - t1
    fracs = np.sort(np.clip(np.asarray(params[1 : k - 1], dtype=float), 1e-12, 1 - 1e-12))
    internal = t1 + fracs * scale
    all_cutoffs = np.concatenate(([t1], internal, [tk]))

    alpha = complex(params[k - 1], params[k])
    eta_start = k + 1
    bands = []
    for j in range(1, k):
        start = float(all_cutoffs[j - 1])
        end = float(all_cutoffs[j])
        re_eta = float(params[eta_start + 2 * (j - 1)])
        im_eta = float(params[eta_start + 2 * (j - 1) + 1])
        bands.append((start, end, complex(re_eta, im_eta)))
    return AdmissibleDensity(alpha=alpha, tau=t1, bands=bands)


def _series_IA(x: complex, alpha: complex, terms: int) -> complex:
    """Compute I_A(x) = sum_{r=0}^∞ x^{alpha+r} / (alpha+r) using a partial sum + tail bound.

    For 0 < x < 1 and Re(alpha) > 0 the tail is bounded by a geometric series.
    """
    if x <= 0 or x >= 1:
        raise ValueError("x must be in (0,1)")
    s = 0.0 + 0.0j
    for r in range(terms):
        s += x ** (alpha + r) / (alpha + r)
    # Geometric tail bound: |x^{alpha+r}| ≤ x^{Re(alpha)+r}
    # tail ≤ x^{Re(alpha)+terms} / (Re(alpha)+terms) / (1 - x)
    r = terms
    re_a = alpha.real
    tail = (x ** (re_a + r)) / (re_a + r) / (1.0 - x)
    return s + tail


def _integral_k1(tau: float, alpha: complex, terms: int) -> complex:
    """∫_0^tau u^{alpha-1}/(1-u) du = I_A(tau) for Re(alpha)>0."""
    return _series_IA(tau, alpha, terms)


def _integral_A1(a: float, b: float, alpha: complex, terms: int) -> complex:
    """∫_a^b u^{alpha-1}/(1-u) du = I_A(b) - I_A(a)."""
    return _series_IA(b, alpha, terms) - _series_IA(a, alpha, terms)


def _integral_D(tau: float, alpha: complex, terms: int) -> float:
    """∫_0^tau u^{Re(alpha)-1}/(1-u) du (real)."""
    re_alpha = alpha.real
    return float(_series_IA(tau, re_alpha, terms).real)


def _integral_Q2D(a_u: float, b_u: float, a_v: float, b_v: float,
                  alpha: complex, QN: int, Qp: float) -> complex:
    """∫_{a_u}^{b_u} ∫_{a_v}^{min(b_v, 1-u)} (1-u-v)^{alpha-1}/(u v) dv du via GL quadrature.

    Uses the graded substitution v = Vmax - (Vmax - c) * s^p to remove the
    singularity at the hypotenuse u+v=1.
    """
    xu, wu = leggauss(QN)
    xs, ws = leggauss(QN)
    half_ba = (b_u - a_u) / 2.0
    mid_u = (a_u + b_u) / 2.0
    total = 0.0 + 0.0j
    for i in range(QN):
        u = mid_u + half_ba * xu[i]
        # v interval for this u
        c = a_v
        Vmax = min(b_v, 1.0 - u)
        if Vmax <= c:
            continue
        L = Vmax - c
        inner = 0.0 + 0.0j
        for j in range(QN):
            s = 0.5 * (xs[j] + 1.0)
            v = Vmax - L * (s ** Qp)
            if v <= 0:
                continue
            wj = ws[j]
            jac = L * Qp * (s ** (Qp - 1.0)) * wj * 0.5
            base = max(1.0 - u - v, 0.0)
            if base <= 0:
                continue
            inner += (base ** (alpha - 1.0)) / (u * v) * jac
        total += inner * wu[i] * half_ba
    return total


def F_functional(density: AdmissibleDensity,
                   terms: int = 3000,
                   QN: int = 200,
                   Qp: float = 4.0) -> tuple[complex, float, float]:
    """Evaluate Y[ρ], D[ρ], and C[ρ] for an admissible density ρ.

    Returns
    -------
    Y : complex
    D : float
    C : float
    """
    alpha = density.alpha
    tau = density.tau
    k = len(density.bands)

    # 1D integrals
    K = _integral_k1(tau, alpha, terms)
    D = _integral_D(tau, alpha, terms)
    s = 1.0 - alpha

    A1 = np.zeros(k, dtype=complex)
    w = np.zeros(k, dtype=complex)
    for j, (a, b, eta) in enumerate(density.bands):
        A1[j] = _integral_A1(a, b, alpha, terms)
        w[j] = eta - s

    # 2D integrals Q_{jl}
    Q = np.zeros((k, k), dtype=complex)
    for j in range(k):
        a_u, b_u, _ = density.bands[j]
        for l in range(k):
            a_v, b_v, _ = density.bands[l]
            Q[j, l] = _integral_Q2D(a_u, b_u, a_v, b_v, alpha, QN, Qp)

    Y = 1.0 - np.dot(w, A1) + 0.5 * np.dot(w, Q @ w) + s * K
    C = abs(Y) / D
    return Y, D, float(C)


def discrete_sequence_from_density(density: AdmissibleDensity, n: int) -> np.ndarray:
    """Construct a finite complex sequence z_1,...,z_n whose empirical measure approximates ρ.

    This is a naive equidistribution construction used in the proof sketch of Part I.
    Points are placed at radii r_j = 1 (on the unit circle) with arguments derived from
    the cumulative distribution of the density. The first block maps to a ray/arc with
    argument governed by alpha; remaining bands use their band value arguments.
    """
    if n < 1:
        raise ValueError("n must be positive")
    z = np.zeros(n, dtype=complex)
    # Simplest construction: count points per band proportional to length
    tau = density.tau
    alpha = density.alpha

    # First block: n*tau points with argument -arg(1-alpha) * k scaling approximated here
    n_first = max(1, int(round(n * tau)))
    n_first = min(n_first, n)
    arg_s = np.angle(1.0 - alpha)
    for idx in range(n_first):
        # place on unit circle; exact phase chosen by band argument
        z[idx] = np.exp(1j * arg_s)

    # Remaining bands
    remaining = n - n_first
    if remaining > 0 and density.bands:
        band_lengths = np.array([b - a for a, b, _ in density.bands], dtype=float)
        total_tail = band_lengths.sum()
        if total_tail <= 0:
            counts = np.zeros(len(density.bands), dtype=int)
            counts[0] = remaining
        else:
            counts = (remaining * band_lengths / total_tail).astype(int)
            counts[-1] += remaining - counts.sum()
        pos = n_first
        for (a, b, eta), count in zip(density.bands, counts):
            arg_eta = np.angle(eta)
            for _ in range(count):
                z[pos] = np.exp(1j * arg_eta)
                pos += 1
    return z
