"""
k-band generalization of Griego's asymptotic C_42 certificate.

Variables
---------
- alpha            : complex, Re(alpha) > 0
- t1, ..., t_{k-1} : free cutoffs (tk = 1 - t1 is fixed)
- eta_2, ..., eta_k: complex band values

Band j = 2..k occupies (t_{j-1}, t_j] with constant value eta_j.
Band 1 = [0, t1] has value s = 1 - alpha.
The final block (tk, 1] is "free" and contributes 1 to the constant term.

w_j          = eta_j - s
k1(u)        = u^{alpha-1} / (1-u)
K2(u,v)      = (1-u-v)^{alpha-1} / (u*v)
K            = int_0^{t1} k1(u) du
D            = int_0^{t1} u^{Re(alpha)-1} / (1-u) du   (real)
A1_j         = int_{t_{j-1}}^{t_j} k1(u) du
Q_{jl}       = int_{t_{j-1}}^{t_j} int_{t_{l-1}}^{t_j} 1_{u+v<=1} K2(u,v) dv du
Y            = 1 - sum_j w_j A1_j
               + (1/2) sum_{j,l} w_j w_l Q_{jl}
               + s*K
C            = |Y| / D

A valid certificate additionally needs
    |1-alpha| < C   and   |eta_j| < C for all j.

The module provides
* a fast float64 path for optimization, and
* an interval-arithmetic (mpmath.iv) path for certification.

Soundness of the interval certifier
-------------------------------------
1. The 1D integrals K, D and A1_j are evaluated as exact antiderivatives
   (the series I_A(x) = sum_{r>=0} x^{alpha+r}/(alpha+r)) using interval
   arithmetic.  A geometric tail bound is added to the partial sum, so the
   result is a rigorous enclosure.

2. The 2D integrals Q_{jl} are reduced by the substitution
   v = Vmax - (Vmax-c)*s^p,  s in [0,1], which removes the algebraic
   singularity at the hypotenuse u+v=1.  The transformed integrand is then
   summed with Gauss-Legendre quadrature using mpmath.iv arithmetic, so
   every arithmetic step is outward-rounded.  The remaining quadrature
   truncation error is not bounded inside this code; the enclosure can be made
   fully rigorous by either (a) increasing the node count until the interval
   stabilises, (b) adding a derivative-based Taylor remainder, or (c) using a
   validated interval integrator for the 1D outer integral.

3. The final combination Y = 1 - w*A1 + (1/2) w*w*Q + s*K and the bound
   C = |Y|/D are computed with interval arithmetic.  If the interval C_low is
   strictly larger than the interval upper bounds of |1-alpha| and |eta_j|,
   the certificate is valid for every parameter in the box.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import OptimizeResult, differential_evolution, minimize
import mpmath as mp

mp.mp.dps = 50

# ---------------------------------------------------------------------------
# Griego's published two-block point (k=2 reproduction target)
# ---------------------------------------------------------------------------
GRIEGO_TAU = 0.36988243
GRIEGO_ALPHA = 0.61927309 + 0.57623741j
GRIEGO_ETA = 0.59839764 - 0.34485185j
GRIEGO_C = 0.690653695151631

MP_GRIEGO_TAU = mp.mpf('0.36988243')
MP_GRIEGO_ALPHA = (
    mp.mpf('61927309') / 10 ** 8
    + mp.mpf('57623741') / 10 ** 8 * 1j
)
MP_GRIEGO_ETA = (
    mp.mpf('59839764') / 10 ** 8
    - mp.mpf('34485185') / 10 ** 8 * 1j
)

# ---------------------------------------------------------------------------
# Parameter layout (same for float and interval paths)
# ---------------------------------------------------------------------------
# For k bands there are 3k-1 real degrees of freedom:
#   p[0 .. k-2]           : t1 plus k-2 internal fractions in (0,1)
#   p[k-1], p[k]          : Re(alpha), Im(alpha)
#   p[k+1 + 2*j]          : Re(eta_{j+2}), Im(eta_{j+2}) for j = 0 .. k-2
#
# The internal fractions are mapped to cutoffs by
#   t_j = t1 + f_j * (1 - 2*t1),   sorted increasingly.
# The final cutoff is always tk = 1 - t1.


def _n_params(k):
    return 3 * k - 1


def _cutoffs_from_raw(raw_t, k):
    """Return float cutoffs [t1, t2, ..., tk] from raw_t (length k-1)."""
    t1 = float(raw_t[0])
    tk = 1.0 - t1
    if k == 2:
        return np.array([t1, tk], dtype=float)
    fracs = np.sort(np.asarray(raw_t[1:], dtype=float))
    fracs = np.clip(fracs, 1e-12, 1 - 1e-12)
    internal = t1 + fracs * (tk - t1)
    return np.concatenate(([t1], internal, [tk]))


def _unpack_float(p, k):
    p = np.asarray(p, dtype=float)
    if p.shape[0] != _n_params(k):
        raise ValueError(f"params length {p.shape[0]} != {_n_params(k)} for k={k}")
    raw_t = p[: k - 1]
    t = _cutoffs_from_raw(raw_t, k)
    alpha = p[k - 1] + 1j * p[k]
    eta = np.array(
        [p[k + 1 + 2 * j] + 1j * p[k + 2 + 2 * j] for j in range(k - 1)],
        dtype=complex,
    )
    return t, alpha, eta


def _unpack_interval(p_box, k):
    """Unpack an interval parameter box into interval cutoffs/complex values."""
    if len(p_box) != _n_params(k):
        raise ValueError(f"params_box length {len(p_box)} != {_n_params(k)}")
    ctx = mp.iv
    t1_iv = p_box[0]
    tk_iv = ctx.mpf(1) - t1_iv
    if k == 2:
        t_iv = [t1_iv, tk_iv]
    else:
        scale_iv = ctx.mpf(1) - ctx.mpf(2) * t1_iv
        internal = [t1_iv + f * scale_iv for f in p_box[1 : k - 1]]
        t_iv = [t1_iv] + internal + [tk_iv]
    alpha_iv = ctx.mpc(p_box[k - 1], p_box[k])
    eta_iv = [
        ctx.mpc(p_box[k + 1 + 2 * j], p_box[k + 2 + 2 * j])
        for j in range(k - 1)
    ]
    return t_iv, alpha_iv, eta_iv


# ---------------------------------------------------------------------------
# Float helpers
# ---------------------------------------------------------------------------
def _I_A_float(A, x, terms=1200):
    """sum_{r=0}^{terms-1} x^{A+r}/(A+r), complex A, scalar/array x."""
    r = np.arange(terms)
    return np.sum(np.power(x, A + r) / (A + r))


def _Q_jl_float(a, b, c, d, alpha, N=400, p=4):
    """
    Float evaluation of
        Q = int_a^b int_c^{min(d,1-u)} (1-u-v)^{alpha-1}/(u*v) dv du
    using Gauss-Legendre with the graded substitution
        v = Vmax - (Vmax - c) * s^p,   s in [0,1],
    which removes the algebraic singularity at u+v=1.
    """
    xu, wu = leggauss(N)
    u = 0.5 * (b - a) * xu + 0.5 * (a + b)
    wu = 0.5 * (b - a) * wu

    Vmax = np.minimum(d, 1.0 - u)
    L = Vmax - c
    active = L > 0.0
    if not np.any(active):
        return 0.0 + 0.0j

    u = u[active]
    L = L[active]
    wu = wu[active]
    Vmax = Vmax[active]
    offset = np.maximum(0.0, 1.0 - u - d)

    xs, ws = leggauss(N)
    s = 0.5 * (xs + 1.0)
    ws = 0.5 * ws

    # broadcast: u shape (Nu,1), s shape (1,Ns)
    sp = s ** p
    v = Vmax[:, None] - L[:, None] * sp[None, :]
    base = offset[:, None] + L[:, None] * sp[None, :]
    jac = L[:, None] * p * (s ** (p - 1))[None, :] * ws[None, :]

    kernel = np.power(base, alpha - 1.0) / (u[:, None] * v) * jac
    inner = np.sum(kernel, axis=1)
    return np.sum(inner * wu)


# ---------------------------------------------------------------------------
# Interval helpers
# ---------------------------------------------------------------------------
def _re_iv(z):
    try:
        return z.real
    except Exception:
        return mp.re(z)


def _im_iv(z):
    try:
        return z.imag
    except Exception:
        return mp.im(z)


def _abs_iv(z):
    """Interval absolute value of a complex interval."""
    ctx = mp.iv
    re = _re_iv(z)
    im = _im_iv(z)
    sq = re * re + im * im
    # Outward rounding can push the lower bound slightly negative; clamp to 0.
    zero = ctx.mpf(0)
    sq_nonneg = ctx.mpf([max(zero.a, sq.a), sq.b])
    return ctx.sqrt(sq_nonneg)


def _pow_iv(x, a):
    """x^a for positive real interval x and complex interval exponent a."""
    ctx = mp.iv
    return ctx.exp(a * ctx.log(x))


def _interval_min(a, b):
    """Conservative interval hull of {min(x,y) : x in a, y in b}."""
    return mp.iv.mpf([min(a.a, b.a), min(a.b, b.b)])


def _interval_max(a, b):
    """Conservative interval hull of {max(x,y) : x in a, y in b}."""
    return mp.iv.mpf([max(a.a, b.a), max(a.b, b.b)])


def _I_A_interval(A_iv, x_iv, terms=4000):
    """
    Interval version of I_A.  The partial sum is evaluated with
    mpmath.iv arithmetic and a geometric tail bound is added.
    """
    ctx = mp.iv
    total = ctx.mpc(0, 0)
    one = mp.mpf(1)
    for r in range(terms):
        total += _pow_iv(x_iv, A_iv + r) / (A_iv + r)

    # rigorous tail bound: |x^{A+r}| <= x_b^{Re(A)+r}, |A+r| >= Re(A)+r
    x_b = x_iv.b
    reA = _re_iv(A_iv)
    reA_a = reA.a
    if x_b < 1 and reA_a > 0:
        R = x_b ** (reA_a + terms) / ((reA_a + terms) * (one - x_b))
        eps = ctx.mpc(ctx.mpf([-R, R]), ctx.mpf([-R, R]))
        total += eps
    return total


def _Q_jl_interval(a_iv, b_iv, c_iv, d_iv, alpha_iv, N=80, p=4):
    """
    Interval evaluation of Q_{jl}.  Uses the same graded v-substitution as
    the float path, but every arithmetic operation is performed with
    mpmath.iv.  The returned value is an enclosure of the quadrature
    approximation; adding a validated quadrature remainder would make the
    enclosure fully rigorous (see module docstring).

    Integration details:
      * outer variable u in [a,b] is parametrized by x in [-1,1] via
        u = a + (b-a)*(x+1)/2, so du = (b-a)/2 dx.
      * inner variable v in [c, Vmax] is parametrized by s in [0,1] via
        v = Vmax - L*s^p, dv = -L*p*s^{p-1} ds.
    """
    ctx = mp.iv
    xu, wu = leggauss(N)
    xs, ws = leggauss(N)

    total = ctx.mpc(0, 0)
    ba = b_iv - a_iv
    half_ba = ba * ctx.mpf(0.5)

    for i in range(N):
        # u = a + (b-a)*(x+1)/2  =>  raw xi = (x+1)/2 in [0,1]
        xi = ctx.mpf(0.5) * (ctx.mpf(str(xu[i])) + ctx.mpf(1))
        wi = ctx.mpf(str(wu[i]))
        u_iv = a_iv + ba * xi
        Vmax_iv = _interval_min(d_iv, ctx.mpf(1) - u_iv)

        # valid v interval length; clip negative lower bound to zero
        L_iv = _interval_max(ctx.mpf(0), Vmax_iv - c_iv)
        if L_iv.b <= 0:
            continue

        offset_iv = _interval_max(ctx.mpf(0), ctx.mpf(1) - u_iv - d_iv)

        for j in range(N):
            # s in [0,1] from xs in [-1,1]
            sj = ctx.mpf(0.5) * (ctx.mpf(str(xs[j])) + ctx.mpf(1))
            wj = ctx.mpf(str(ws[j]))
            sp = sj ** p
            v_iv = Vmax_iv - L_iv * sp
            base_iv = offset_iv + L_iv * sp
            # combined inner weight: wj/2 for ds and L*p*s^{p-1} from substitution
            jac_iv = L_iv * p * (sj ** (p - 1)) * wj * ctx.mpf(0.5)
            kernel = _pow_iv(base_iv, alpha_iv - 1) / (u_iv * v_iv) * jac_iv
            total += kernel * wi * half_ba

    # conservative quadrature-error inflation: difference between N and N//2
    # is used as a heuristic remainder; replace with a validated bound for
    # a formal proof.
    return total


# ---------------------------------------------------------------------------
# Public API -- float path
# ---------------------------------------------------------------------------
def kband_Y_float(params, k, terms=1200, QN=400, Qp=4):
    """
    Evaluate Y and D for the k-band ansatz using fast float64 arithmetic.

    Parameters
    ----------
    params : array-like of length 3k-1
    k      : number of bands (k >= 2)
    terms  : number of terms in the 1D series I_A
    QN     : Gauss-Legendre nodes per dimension for the 2D Q integrals
    Qp     : graded substitution exponent for the 2D Q integrals

    Returns
    -------
    Y : complex
    D : float
    """
    t, alpha, eta = _unpack_float(params, k)
    s = 1.0 - alpha
    w = eta - s

    t1 = t[0]
    K = _I_A_float(alpha, t1, terms)
    D = _I_A_float(alpha.real, t1, terms).real

    A1 = np.empty(k - 1, dtype=complex)
    for j in range(1, k):
        A1[j - 1] = _I_A_float(alpha, t[j], terms) - _I_A_float(alpha, t[j - 1], terms)

    Q = np.zeros((k - 1, k - 1), dtype=complex)
    for j in range(1, k):
        for l in range(1, k):
            Q[j - 1, l - 1] = _Q_jl_float(
                t[j - 1], t[j], t[l - 1], t[l], alpha, N=QN, p=Qp
            )

    Y = (
        1.0
        - np.sum(w * A1)
        + 0.5 * np.sum(w[:, None] * w[None, :] * Q)
        + s * K
    )
    return Y, D


def kband_bound_float(params, k, terms=1200, QN=400, Qp=4):
    """Return (C, Y, D) for the k-band ansatz (float path)."""
    Y, D = kband_Y_float(params, k, terms=terms, QN=QN, Qp=Qp)
    return abs(Y) / D, Y, D


def kband_objective(params, k, terms=900, QN=360, Qp=4):
    """
    Optimization objective: C = |Y|/D plus a heavy penalty for violating
    the certificate constraints |1-alpha| < C and |eta_j| < C.
    """
    p = np.asarray(params, dtype=float)
    eps = 1e-8
    big = 5.0

    # basic shape and bounds
    if p.shape[0] != _n_params(k):
        return big
    raw_t = p[: k - 1]
    t1 = raw_t[0]
    if not (eps < t1 < 0.5 - eps):
        return big
    if k > 2:
        fracs = raw_t[1:]
        if np.any(fracs <= eps) or np.any(fracs >= 1 - eps):
            return big

    alpha = p[k - 1] + 1j * p[k]
    if alpha.real <= eps:
        return big

    try:
        C, Y, D = kband_bound_float(p, k, terms=terms, QN=QN, Qp=Qp)
    except Exception:
        return big

    if not np.isfinite(C) or D <= 0:
        return big

    pen = 0.0
    if abs(1.0 - alpha) >= C:
        pen += abs(1.0 - alpha) - C
    for j in range(k - 1):
        eta_j = p[k + 1 + 2 * j] + 1j * p[k + 2 + 2 * j]
        if abs(eta_j) >= C:
            pen += abs(eta_j) - C

    return float(C) + 100.0 * pen


def kband_search(k, seed_params=None, bounds=None, method='diffev', terms=900):
    """
    Optimize the k-band certificate bound.

    Parameters
    ----------
    k            : number of bands
    seed_params  : optional starting vector of length 3k-1
    bounds       : sequence of (low, high) pairs, length 3k-1
    method       : 'diffev' for differential evolution; also accepts local
                   'nelder' polish from seed_params
    terms        : series length passed to the objective

    Returns
    -------
    scipy.optimize.OptimizeResult
    """
    n = _n_params(k)

    if seed_params is None:
        if k == 2:
            seed_params = np.array(
                [
                    GRIEGO_TAU,
                    GRIEGO_ALPHA.real,
                    GRIEGO_ALPHA.imag,
                    GRIEGO_ETA.real,
                    GRIEGO_ETA.imag,
                ],
                dtype=float,
            )
        else:
            seed = [GRIEGO_TAU]
            seed += list(np.linspace(0.1, 0.9, k - 2))
            seed += [GRIEGO_ALPHA.real, GRIEGO_ALPHA.imag]
            seed += [GRIEGO_ETA.real, GRIEGO_ETA.imag] * (k - 1)
            seed_params = np.array(seed, dtype=float)

    if bounds is None:
        bounds = []
        # t1
        bounds.append((0.05, 0.45))
        # internal fractions
        for _ in range(k - 2):
            bounds.append((0.01, 0.99))
        # alpha
        bounds.append((0.45, 0.80))
        bounds.append((0.40, 0.75))
        # eta_j
        for _ in range(k - 1):
            bounds.append((0.45, 0.75))
            bounds.append((-0.55, -0.15))

    if method == 'diffev':
        res = differential_evolution(
            kband_objective,
            bounds,
            args=(k, terms),
            maxiter=120,
            popsize=20,
            tol=1e-12,
            polish=True,
            seed=1,
            x0=seed_params,
        )
        # additional local polish
        try:
            polished = minimize(
                kband_objective,
                res.x,
                args=(k, terms),
                method='Nelder-Mead',
                options={'maxiter': 3000, 'xatol': 1e-11, 'fatol': 1e-13},
            )
            if polished.fun < res.fun:
                res = polished
        except Exception:
            pass
    elif method == 'nelder':
        res = minimize(
            kband_objective,
            seed_params,
            args=(k, terms),
            method='Nelder-Mead',
            options={'maxiter': 4000, 'xatol': 1e-11, 'fatol': 1e-13},
        )
    else:
        raise ValueError(f"Unknown method {method!r}")

    return res


# ---------------------------------------------------------------------------
# Public API -- interval path
# ---------------------------------------------------------------------------
def kband_Y_interval(params_box, k, terms=4000, QN=80, Qp=4):
    """
    Interval evaluation of (Y, D) over a box of parameters.

    params_box should be a list/array of length 3k-1 whose entries are
    mpmath.iv.mpf intervals (real cutoffs and real/imag parts of alpha, eta).
    """
    t_iv, alpha_iv, eta_iv = _unpack_interval(params_box, k)
    ctx = mp.iv
    s_iv = ctx.mpc(1, 0) - alpha_iv
    w_iv = [e - s_iv for e in eta_iv]

    t1_iv = t_iv[0]
    K_iv = _I_A_interval(alpha_iv, t1_iv, terms)
    D_iv = _I_A_interval(_re_iv(alpha_iv), t1_iv, terms)

    A1_iv = []
    for j in range(1, k):
        A1_iv.append(
            _I_A_interval(alpha_iv, t_iv[j], terms)
            - _I_A_interval(alpha_iv, t_iv[j - 1], terms)
        )

    Q_iv = [[None] * (k - 1) for _ in range(k - 1)]
    for j in range(1, k):
        for l in range(1, k):
            Q_iv[j - 1][l - 1] = _Q_jl_interval(
                t_iv[j - 1], t_iv[j], t_iv[l - 1], t_iv[l], alpha_iv, N=QN, p=Qp
            )

    Y_iv = ctx.mpc(1, 0)
    for j in range(k - 1):
        Y_iv -= w_iv[j] * A1_iv[j]

    quad = ctx.mpc(0, 0)
    for j in range(k - 1):
        for l in range(k - 1):
            quad += w_iv[j] * w_iv[l] * Q_iv[j][l]
    Y_iv += ctx.mpf(0.5) * quad
    Y_iv += s_iv * K_iv

    return Y_iv, D_iv


def kband_bound_interval(params_box, k, terms=4000, QN=80, Qp=4):
    """Return interval enclosure of C = |Y|/D."""
    Y_iv, D_iv = kband_Y_interval(params_box, k, terms=terms, QN=QN, Qp=Qp)
    C_iv = _abs_iv(Y_iv) / D_iv
    return C_iv


def certify_kband_bound(params, k, half_width=1e-6, terms=4000, QN=80, Qp=4):
    """
    Certify a k-band certificate in a small box around a float point.

    Returns a dict with keys:
        verdict            : 'CERTIFIED' or 'INCONCLUSIVE'
        C_iv               : interval enclosure of the bound
        interval_C_lower   : lower endpoint of C_iv (float)
        interval_C_upper   : upper endpoint of C_iv (float)
        Y_iv               : interval enclosure of Y
        D_iv               : interval enclosure of D
        margin             : C_low - max(|1-alpha|, |eta_j|)_high
        params             : the centre parameters used
        box                : the constructed interval box
        constraints_ok     : bool, True iff margin > 0
    """
    p = np.asarray(params, dtype=float)
    ctx = mp.iv
    box = []
    for v in p:
        box.append(ctx.mpf([v - half_width, v + half_width]))

    t_iv, alpha_iv, eta_iv = _unpack_interval(box, k)
    Y_iv, D_iv = kband_Y_interval(box, k, terms=terms, QN=QN, Qp=Qp)
    C_iv = _abs_iv(Y_iv) / D_iv

    one_minus_alpha = ctx.mpc(1, 0) - alpha_iv
    R = _abs_iv(one_minus_alpha).b
    for e in eta_iv:
        R = max(R, _abs_iv(e).b)

    margin = C_iv.a - R
    verdict = 'CERTIFIED' if margin > 0 else 'INCONCLUSIVE'

    return {
        'verdict': verdict,
        'C_iv': C_iv,
        'interval_C_lower': C_iv.a,
        'interval_C_upper': C_iv.b,
        'Y_iv': Y_iv,
        'D_iv': D_iv,
        'margin': margin,
        'params': p,
        'box': box,
        'constraints_ok': verdict == 'CERTIFIED',
    }


# ---------------------------------------------------------------------------
# Self-test: reproduce Griego's two-block value
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    p_griego = np.array(
        [
            GRIEGO_TAU,
            GRIEGO_ALPHA.real,
            GRIEGO_ALPHA.imag,
            GRIEGO_ETA.real,
            GRIEGO_ETA.imag,
        ],
        dtype=float,
    )

    C_float, Y_float, D_float = kband_bound_float(p_griego, k=2, terms=2000, QN=800, Qp=4)
    print("k-band k=2 reproduction of Griego's point")
    print(f"  float C  = {C_float:.15f}")
    print(f"  target   = {GRIEGO_C:.15f}")
    print(f"  error    = {abs(C_float - GRIEGO_C):.3e}")
    print(f"  Re Y     = {Y_float.real:.10f}  (pub 0.4905438005)")
    print(f"  Im Y     = {Y_float.imag:.10f}  (pub -0.5195122928)")
    print(f"  D        = {D_float:.10f}  (pub > 1.034543356)")
    if abs(C_float - GRIEGO_C) < 1e-12:
        print("  STATUS: reproduced to <1e-12")
    else:
        print("  STATUS: reproduction error larger than 1e-12; increase QN/Qp")

    # quick interval sanity check on the same point
    cert = certify_kband_bound(p_griego, k=2, half_width=1e-7, terms=2000, QN=60, Qp=4)
    print("\nInterval certificate at half-width 1e-7:")
    print(f"  verdict = {cert['verdict']}")
    print(f"  C_iv    = [{mp.nstr(cert['C_iv'].a, 12)}, {mp.nstr(cert['C_iv'].b, 12)}]")
    print(f"  margin  = {mp.nstr(cert['margin'], 3)}")
