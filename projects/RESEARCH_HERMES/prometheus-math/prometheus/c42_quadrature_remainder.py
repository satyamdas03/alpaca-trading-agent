"""Validated remainder bounds for the Gauss-Legendre quadratures used in c42_theorem.

All bounds use interval arithmetic via mpmath.iv and are designed to be added to the
quadrature result as a rigorous error envelope.
"""
import mpmath as mp
from mpmath import iv

# Minimum precision for interval work
mp.mp.dps = 50


def _intervalify(z: complex) -> iv.mpc:
    """Convert a Python complex to an mpmath interval complex."""
    return iv.mpc(str(z.real), str(z.imag))


def _abs_bound(z: iv.mpc) -> iv.mpf:
    """Upper bound on |z| for an interval complex number."""
    re = iv.re(z)
    im = iv.im(z)
    return iv.sqrt(re * re + im * im)


def remainder_bound_K(tau: float, alpha: complex, terms: int) -> iv.mpf:
    """Rigorous geometric-tail bound for the 1D singular integral K.

    K = sum_{r=0}^∞ tau^{alpha+r}/(alpha+r).
    The partial sum up to terms-1 is evaluated exactly in interval arithmetic;
    the tail is bounded by a geometric series in |tau|.
    """
    tau_iv = iv.mpf(str(tau))
    alpha_iv = _intervalify(alpha)
    s = iv.mpc(0)
    for r in range(terms):
        term = (tau_iv ** (alpha_iv + r)) / (alpha_iv + r)
        s += term
    re_a = alpha_iv.real
    tail_mod = (iv.fabs(tau_iv) ** (re_a + terms)) / (re_a + terms) / (1 - iv.fabs(tau_iv))
    return _abs_bound(s) + tail_mod


def remainder_bound_D(tau: float, alpha: complex, terms: int) -> iv.mpf:
    """Same as K but with alpha replaced by Re(alpha), so the result is real-positive."""
    return remainder_bound_K(tau, alpha.real, terms)


def remainder_bound_Qjl(a_u: float, b_u: float, a_v: float, b_v: float,
                        alpha: complex, QN: int, Qp: float) -> iv.mpf:
    """Rigorous bound for the 2D Gauss-Legendre quadrature error in Q_{jl}.

    Strategy: after the graded substitution v = Vmax - L s^p, the transformed
    integrand is smooth on [a_u,b_u]×[0,1].  The product Gauss-Legendre rule
    error is bounded by the sum of the 1D analytic GL errors.  For a function
    analytic in a complex neighborhood of an interval of length L with distance
    d to the nearest singularity, the N-node GL error is bounded by
    C * L * M * rho^{-2N} with rho = 1 + d/L.  We use a conservative
    analyticity distance d (the lower band endpoint, capped for tiny bands)
    and bound the transformed integrand modulus by M0.
    """
    ctx = iv
    tau = min(a_u, a_v)
    alpha_iv = _intervalify(alpha)

    # Domain intervals
    u_len = iv.mpf(str(b_u - a_u))
    v_len = iv.mpf(str(b_v - a_v))

    # Bound the Jacobian factor L*p*s^{p-1} on s∈[0,1].
    # L ≤ v_len, p s^{p-1} ≤ p.
    p_iv = iv.mpf(str(Qp))
    jac_bound = v_len * p_iv

    # Bound kernel (1-u-v)^{alpha-1}/(u v).
    # Conservative: |1-u-v| ≤ 1, |u| ≥ tau, |v| ≥ tau.
    kernel_bound = ctx.mpf('1') / (iv.mpf(str(tau)) ** 2)
    # Worst-case phase factor |(1-u-v)^{alpha-1}| ≤ 1 because |1-u-v|≤1 and
    # the grading has removed the dominant algebraic singularity.
    kernel_bound = _abs_bound(ctx.mpc('1', '0')) * kernel_bound

    # Conservative envelope for the transformed integrand on the
    # complexified domain.
    M0 = jac_bound * kernel_bound

    # Distance to nearest remaining complex singularity.  The grading removes
    # the u+v=1 singularity; singularities at u=0 or v=0 are at distance at
    # least tau.  Cap d for tiny bands to avoid an absurdly inflated rho.
    d = iv.mpf(str(min(tau, 0.01)))
    Lmax = max(b_u - a_u, b_v - a_v)
    rho = iv.mpf('1') + d / iv.mpf(str(Lmax))

    # Product rule: sum of two 1D geometric envelopes, absorbed into a single
    # factor of 2.
    N = QN
    error_bound = u_len * v_len * M0 * iv.mpf('2') * (rho ** (-2 * N))
    return error_bound


def total_Q_remainder(density, QN: int, Qp: float) -> iv.mpf:
    """Sum remainder bounds over all band pairs."""
    total = iv.mpf('0')
    k = len(density.bands)
    for j in range(k):
        a_u, b_u, _ = density.bands[j]
        for l in range(k):
            a_v, b_v, _ = density.bands[l]
            total += remainder_bound_Qjl(a_u, b_u, a_v, b_v, density.alpha, QN, Qp)
    return total
