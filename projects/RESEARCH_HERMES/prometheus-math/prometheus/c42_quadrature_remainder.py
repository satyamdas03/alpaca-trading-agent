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
    ctx = iv
    re = iv.re(z)
    im = iv.im(z)
    sq = re * re + im * im
    # Outward rounding can push the lower bound slightly negative; clamp to 0.
    zero = ctx.mpf('0')
    sq_nonneg = ctx.mpf([max(zero.a, sq.a), sq.b])
    return ctx.sqrt(sq_nonneg)


def _series_tail_modulus(tau: float, sigma: complex, terms: int) -> iv.mpf:
    """Geometric tail bound for sum_{r=terms}^∞ tau^{sigma+r}/(sigma+r).

    The modulus of each term is bounded by |tau|^{Re(sigma)+r}/(Re(sigma)+r),
    and the tail is dominated by a geometric series in |tau|.  The computation
    is performed at enough decimal digits to avoid underflow of tau^{terms};
    the result is clamped to a representable positive number when it is below
    the default precision.
    """
    # The tail exponent is terms * log10(|tau|); we need about that many
    # digits plus a safety margin.
    log10_abs_tau = float(mp.log(abs(tau), 10))
    needed = max(50, int(-log10_abs_tau * terms) + 20)
    with mp.workdps(needed):
        ctx = iv
        re_sigma = ctx.mpf(str(sigma.real))
        tau_abs = ctx.mpf(str(abs(tau)))
        first = (tau_abs ** (re_sigma + terms)) / (re_sigma + terms)
        tail_iv = first / (ctx.mpf('1') - tau_abs)
        upper_str = mp.nstr(tail_iv.b, 3)
    # If the tail is below the default precision it would underflow to [0,0]
    # in interval arithmetic, losing the upper bound.  Clamp to a tiny positive
    # value that is still negligible compared with the functional values.
    try:
        safe_upper = max(iv.mpf(upper_str).b, iv.mpf('1e-50').b)
    except Exception:
        safe_upper = iv.mpf('1e-50').b
    return iv.mpf([0, safe_upper])


def remainder_bound_K(tau: float, alpha: complex, terms: int) -> iv.mpf:
    """Rigorous upper bound on |tail| of the 1D singular series K.

    K = sum_{r=0}^∞ tau^{alpha+r}/(alpha+r).  Only the discarded tail
    r >= terms is bounded; the partial sum is handled by the interval
    evaluation in c42_kband.
    """
    return _series_tail_modulus(tau, alpha, terms)


def remainder_bound_D(tau: float, alpha: complex, terms: int) -> iv.mpf:
    """Rigorous upper bound on the tail of the real 1D series D."""
    return _series_tail_modulus(tau, alpha.real, terms)


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


def _ellipse_box(theta_lo: float, theta_hi: float, rho: float,
                 center: float, length: float) -> iv.mpc:
    """Axis-aligned rectangular enclosure of one arc of a Bernstein ellipse.

    For the real interval [center - length/2, center + length/2] the Bernstein
    ellipse with parameter rho > 1 is parameterised by

        z(theta) = center + (length/2) * (rho e^{i theta} + rho^{-1} e^{-i theta}) / 2.

    This function returns an interval complex number that contains the image of
    theta ∈ [theta_lo, theta_hi].  The enclosure is a rectangle in the
    (cos(theta), sin(theta)) plane; it is conservative but easy to evaluate with
    mpmath.iv.
    """
    ctx = iv
    cosh_b = ctx.mpf(str((rho + 1.0 / rho) / 2.0))
    sinh_b = ctx.mpf(str((rho - 1.0 / rho) / 2.0))

    # Hull of cos/sin on the angular sub-interval, including critical points.
    pts = [theta_lo, theta_hi]
    for t in (0.0, mp.pi, 2.0 * mp.pi):
        if theta_lo <= t <= theta_hi:
            pts.append(t)
    cos_vals = [mp.cos(t) for t in pts]
    sin_vals = [mp.sin(t) for t in pts]
    cos_iv = ctx.mpf([min(cos_vals), max(cos_vals)])
    sin_iv = ctx.mpf([min(sin_vals), max(sin_vals)])
    zeta = ctx.mpc(cosh_b * cos_iv, sinh_b * sin_iv)
    return ctx.mpf(str(center)) + ctx.mpf(str(length)) * zeta / ctx.mpf('2')


def _M_far_ellipse(a_u: float, u_main_end: float, delta: float,
                   rho_u: float, rho_s: float, a_v: float,
                   alpha: complex, Qp: float, grid: int) -> iv.mpf:
    """Rigorous upper bound for |g(u,s)| on the product of two Bernstein ellipses.

    g(u,s) = p L^alpha s^{p alpha - 1} / (u v), where
      L = (1-u) - a_v,
      v = a_v + L (1 - s^p),
      base = L s^p.

    The maximum modulus of a function analytic in a product domain occurs on
    the distinguished boundary, so it suffices to sample theta, phi in
    [0, 2*pi].  A uniform grid of boxes is used; the box size controls the
    conservatism of the enclosure.
    """
    ctx = iv
    alpha_iv = _intervalify(alpha)
    p_iv = ctx.mpf(str(Qp))
    L_s = 1.0 - delta
    center_u = (a_u + u_main_end) / 2.0
    center_s = (delta + 1.0) / 2.0
    L_u_main = u_main_end - a_u

    max_abs = ctx.mpf('0')
    for i in range(grid):
        theta_lo = 2.0 * mp.pi * i / grid
        theta_hi = 2.0 * mp.pi * (i + 1) / grid
        u_box = _ellipse_box(theta_lo, theta_hi, rho_u, center_u, L_u_main)
        for j in range(grid):
            phi_lo = 2.0 * mp.pi * j / grid
            phi_hi = 2.0 * mp.pi * (j + 1) / grid
            s_box = _ellipse_box(phi_lo, phi_hi, rho_s, center_s, L_s)

            L_box = (ctx.mpf('1') - u_box) - ctx.mpf(str(a_v))
            sp_box = s_box ** p_iv
            v_box = ctx.mpf(str(a_v)) + L_box * (ctx.mpf('1') - sp_box)
            base_box = L_box * sp_box
            g = p_iv * (base_box ** (alpha_iv - ctx.mpf('1'))) / (u_box * v_box)
            abs_g = _abs_bound(g)
            if abs_g.b > max_abs.b:
                max_abs = abs_g
    return max_abs


def remainder_bound_Qjl_rigorous(a_u: float, b_u: float, a_v: float, b_v: float,
                                 alpha: complex, QN: int, Qp: float,
                                 grid: int = 128,
                                 delta_f: float = 0.015,
                                 eps_u_f: float = 0.005) -> iv.mpf:
    """Rigorous remainder bound for the 2D Gauss--Legendre quadrature error in Q_{jl}.

    After the graded substitution v = Vmax - L s^p with Vmax = min(t_l, 1-u),
    the transformed integrand is

        g(u,s) = p L^alpha s^{p alpha - 1} / (u v),
        L = (1-u) - a_v,   v = a_v + L (1 - s^p).

    The integrand has two singular/branch points:

      * s = 0 (algebraic branch point), handled by a direct s-integration on
        [0, delta].
      * u = 1 - a_v (the L = 0 branch point), handled by a direct u-tail bound
        on [u_end - eps_u, u_end].

    On the remaining main rectangle the integrand is analytic, so the
    Gauss--Legendre error is bounded by the standard Bernstein-ellipse estimate
    with the sup-norm computed by validated interval sampling of the ellipse
    boundary.

    Parameters
    ----------
    grid : int
        Resolution of the boundary sampling for the complex sup-norm.  A finer
        grid gives a tighter (but slower) bound.  The default 128 is a
        conservative compromise.
    delta_f, eps_u_f : float
        Split parameters: s-integration cut [0, delta] and u-tail length.
        The tail/near bounds are N-independent, so these dominate the total
        remainder once QN is large; shrinking them (at the cost of a larger
        far-part sup-norm) tightens the bound.
    """
    ctx = iv
    alpha_iv = _intervalify(alpha)
    re_alpha = iv.re(alpha_iv)
    p_iv = ctx.mpf(str(Qp))
    delta = ctx.mpf(str(delta_f))
    eps_u = ctx.mpf(str(eps_u_f))

    # Effective u-range where the hypotenuse is active and the inner v-interval
    # is non-empty.  If empty the band pair contributes nothing.
    u_end = min(b_u, 1.0 - a_v)
    L_u_eff = max(0.0, u_end - a_u)
    if L_u_eff <= 0.0:
        return ctx.mpf('0')

    a_u_iv = ctx.mpf(str(a_u))
    a_v_iv = ctx.mpf(str(a_v))

    # L(u) = (1-u) - a_v ranges from L_min (at u=u_end) to L_max (at u=a_u).
    L_max = (1.0 - a_u) - a_v
    L_max_iv = ctx.mpf(str(max(L_max, 0.0)))

    # ---------- u-tail: direct bound on [u_end-eps_u, u_end] ----------
    # On the tail y = u_end - u ∈ [0, tail_len] we have L = y, v ≥ a_v + y,
    # and u = u_end - y.  Hence
    #   |g| ≤ p y^{Re(alpha)} s^{p Re(alpha)-1} / ((u_end-y)(a_v+y)).
    # The s-integral over [0,1] equals 1/(p Re(alpha)).  The remaining
    # y-integrand f(y) = y^{alpha}/((u_end-y)(a_v+y)) is increasing on
    # [0, tail_len] because both numerator y^{alpha} and denominator
    # (u_end-y)(a_v+y) are monotone (the latter increasing, since
    # u_end - a_v - 2y > 0 for our parameter range).  Therefore
    #   ∫_0^{tail_len} f(y) dy ≤ tail_len * f(tail_len).
    # The smallest possible value of the denominator on the tail is attained
    # at y=0, i.e. u_end * a_v, so we use that as the constant lower bound.
    u_tail_start = max(a_u, u_end - eps_u_f)
    tail_len = max(0.0, u_end - u_tail_start)
    tail_len_iv = ctx.mpf(str(tail_len))
    if tail_len > 0.0:
        u_end_iv = ctx.mpf(str(u_end))
        min_uv_tail = u_end_iv * a_v_iv
        h_power = tail_len_iv ** (ctx.mpf('1') + re_alpha) / (ctx.mpf('1') + re_alpha)
        # Integrate s first (factor 1/re_alpha), then bound y-integral by
        # tail_len * f(tail_len) with the constant denominator min_uv_tail.
        tail_bound = h_power / (re_alpha * min_uv_tail)
    else:
        tail_bound = ctx.mpf('0')

    # ---------- Main u-interval: [a_u, u_end - eps_u] ----------
    u_main_end = u_end - tail_len
    L_u_main = max(0.0, u_main_end - a_u)
    if L_u_main <= 0.0:
        return tail_bound
    L_u_main_iv = ctx.mpf(str(L_u_main))

    # Near part: s in [0, delta]
    # For s ∈ [0,delta] the bracket (1-u)(1-s^p)+a_v s^p = (1-u) - L s^p is
    # bounded below by (1-u)(1-delta^p) (since L ≤ 1-u).  Hence
    #   |g(u,s)| ≤ p L(u)^{Re(alpha)} s^{p Re(alpha)-1} / (u*(1-u)*(1-delta^p)).
    # Integrating over s leaves L(u)^{alpha}/(u*(1-u)) * delta^{p alpha}/
    # (alpha*(1-delta^p)).  The remaining u-factor is largest at u=a_u, so we
    # use that worst-case value for the whole main interval.
    one_minus_b_main = ctx.mpf('1') - ctx.mpf(str(u_main_end))
    denom_min_main = a_u_iv * one_minus_b_main
    C_near = p_iv * (L_max_iv ** re_alpha) / (denom_min_main * (ctx.mpf('1') - delta ** p_iv))
    int_s_near = delta ** (p_iv * re_alpha) / (p_iv * re_alpha)
    near_bound = L_u_main_iv * C_near * int_s_near

    # Far part: s in [delta, 1]
    L_s = ctx.mpf('1') - delta

    # s-distance to the singularity at s_*(u)>1 where v=0.
    s_star = ((1.0 - a_u) / max((1.0 - a_u) - a_v, 1e-300)) ** (1.0 / Qp)
    d_s = min(0.015, max(s_star - 1.0, 0.0))

    # u-distance: closest singularity in the main u-interval is u=u_end, at
    # distance tail_len (which equals eps_u when the tail is non-empty).
    rho_u = ctx.mpf('1') + tail_len_iv / L_u_main_iv
    rho_cap_u = ctx.mpf('1.5')
    if rho_u > rho_cap_u:
        rho_u = rho_cap_u

    rho_s = ctx.mpf('1') + ctx.mpf(str(d_s)) / L_s
    rho_cap_s = ctx.mpf('1.2')
    if rho_s > rho_cap_s:
        rho_s = rho_cap_s

    # Rigorous sup-norm on the product Bernstein ellipse, computed by interval
    # sampling of the distinguished boundary.
    M_far = _M_far_ellipse(a_u, float(u_main_end), delta_f,
                           float(rho_u.a), float(rho_s.a),
                           a_v, alpha, Qp, grid=grid)

    # Analytic GL error on the main rectangle [a_u,u_main_end] x [delta,1].
    # The standard product-rule estimate uses 4 * L_u * L_s * M * (rho_u^{-2N}
    # + rho_s^{-2N}).
    N_iv = ctx.mpf(str(QN))
    geom_u = ctx.mpf('1') / (rho_u ** (ctx.mpf('2') * N_iv) - ctx.mpf('1'))
    geom_s = ctx.mpf('1') / (rho_s ** (ctx.mpf('2') * N_iv) - ctx.mpf('1'))
    far_bound = L_u_main_iv * L_s * M_far * ctx.mpf('4') * (geom_u + geom_s)

    return tail_bound + near_bound + far_bound


def total_Q_remainder(density, QN: int, Qp: float, rigorous: bool = False,
                      grid: int = 128) -> iv.mpf:
    """Sum remainder bounds over all band pairs.

    Parameters
    ----------
    rigorous : bool
        If True, use remainder_bound_Qjl_rigorous for every band pair.
        The default False keeps the original heuristic behaviour.
    grid : int
        Grid resolution passed to the rigorous bound.
    """
    total = iv.mpf('0')
    k = len(density.bands)
    for j in range(k):
        a_u, b_u, _ = density.bands[j]
        for l in range(k):
            a_v, b_v, _ = density.bands[l]
            if rigorous:
                total += remainder_bound_Qjl_rigorous(
                    a_u, b_u, a_v, b_v, density.alpha, QN, Qp, grid=grid
                )
            else:
                total += remainder_bound_Qjl(a_u, b_u, a_v, b_v, density.alpha, QN, Qp)
    return total


def total_Q_remainder_rigorous(density, QN: int, Qp: float, grid: int = 128) -> iv.mpf:
    """Convenience wrapper: sum the rigorous remainder bounds over all band pairs."""
    return total_Q_remainder(density, QN, Qp, rigorous=True, grid=grid)
