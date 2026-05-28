# plot/core_helpers.py
# Core geometric helpers for Kalim Ghost Horn mesh generation

import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
#  Ghost Horn mesh
# ---------------------------------------------------------------------------

def generate_ghost_horn_mesh(t_min, t_max, df_points, z_stretch=1.5,
                              z_res=80, theta_res=240):
    """Generate the 3-D Ghost Horn mesh and density field.

    The horn opens from narrow (early time → small Z) to wide (late time → large Z).
    Paper "mass" creates **multiplicative** gravitational dents that are visible
    at every scale of the horn.

    Returns
    -------
    X, Y, Z_plot, density_color, R, z_vals, theta_vals, t_min_eff, t_max_eff
        All numpy arrays + effective t_min/t_max (may be padded).
    """
    EMPTY = np.array([])
    n = len(df_points)
    if n == 0:
        return EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, t_min, t_max

    # ── Ensure minimum time span ──
    if t_max - t_min < 1.0:
        mid = (t_min + t_max) / 2.0
        t_min = mid - 0.5
        t_max = mid + 0.5

    z_vals = np.linspace(t_min, t_max, z_res)
    theta_vals = np.linspace(0, 2 * np.pi, theta_res)
    Z_grid, THETA_grid = np.meshgrid(z_vals, theta_vals, indexing='ij')

    span = t_max - t_min
    norm_grid = (Z_grid - t_min) / (span + 1e-9)

    # ── Horn profile: tamed exponential ──
    #    narrow end (norm=0) → R≈1.3,  wide end (norm=1) → R≈5.6
    #    ratio ~4.3× — visually balanced
    R_base = 0.8 + 1.5 * np.exp(1.4 * norm_grid)

    # ── Gravitational distortion (multiplicative → visible at all scales) ──
    times  = df_points['time'].values
    thetas = df_points['theta'].values
    masses = df_points['mass'].values
    max_mass = masses.max() + 1e-6

    sigma_z = max(span / 8.0, 0.5)
    sigma_theta = np.pi / 3.5

    dz = Z_grid[None, :, :] - times[:, None, None]
    dtheta_raw = np.abs(THETA_grid[None, :, :] - thetas[:, None, None])
    dtheta = np.minimum(dtheta_raw, 2 * np.pi - dtheta_raw)

    gauss = np.exp(-(dz ** 2 / (2 * sigma_z ** 2))
                   - (dtheta ** 2 / (2 * sigma_theta ** 2)))
    weight = (masses / max_mass)[:, None, None]
    distortion = np.sum(gauss * weight, axis=0)               # (z_res, theta_res)

    # Normalise to [0, 1]
    d_max = distortion.max()
    norm_dist = distortion / (d_max + 1e-9) if d_max > 0 else distortion

    # Multiplicative: max 35% radius shrinkage at heaviest point
    gravity_strength = 0.35
    R = R_base * (1.0 - gravity_strength * norm_dist)
    R = np.maximum(0.25, R)

    X = np.nan_to_num(R * np.cos(THETA_grid), nan=0.0)
    Y = np.nan_to_num(R * np.sin(THETA_grid), nan=0.0)
    Z_plot = np.nan_to_num(norm_grid * z_stretch, nan=0.0)

    density_color = np.nan_to_num(norm_dist ** 0.7, nan=0.0)

    return X, Y, Z_plot, density_color, R, z_vals, theta_vals, t_min, t_max


# ---------------------------------------------------------------------------
#  Surface projection (bi-linear interpolation)
# ---------------------------------------------------------------------------

def project_to_surface(norm_t, norm_th, R_grid, z_vals, theta_vals):
    """Interpolate radius on the horn surface for a single point."""
    if len(z_vals) < 2:
        return 1.0
    norm_t = np.clip(norm_t, 0, 1)
    norm_th = np.clip(norm_th, 0, 1)
    iz = min(int(norm_t * (len(z_vals) - 1)), len(z_vals) - 2)
    ith = min(int(norm_th * (len(theta_vals) - 1)), len(theta_vals) - 2)
    wz = norm_t * (len(z_vals) - 1) - iz
    wth = norm_th * (len(theta_vals) - 1) - ith
    r = ((1 - wz) * (1 - wth) * R_grid[iz, ith]
         + (1 - wz) * wth * R_grid[iz, ith + 1]
         + wz * (1 - wth) * R_grid[iz + 1, ith]
         + wz * wth * R_grid[iz + 1, ith + 1])
    return float(r)


def project_to_surface_batch(norm_ts, norm_ths, R_grid, z_vals, theta_vals):
    """Vectorised version — projects arrays of normalised (t, theta)."""
    if len(z_vals) < 2:
        return np.ones_like(norm_ts)

    norm_ts = np.clip(norm_ts, 0.0, 1.0)
    norm_ths = np.clip(norm_ths, 0.0, 1.0)

    nz = len(z_vals) - 1
    nth = len(theta_vals) - 1

    iz = np.clip((norm_ts * nz).astype(int), 0, nz - 1)
    ith = np.clip((norm_ths * nth).astype(int), 0, nth - 1)
    wz = np.clip(norm_ts * nz - iz, 0, 1)
    wth = np.clip(norm_ths * nth - ith, 0, 1)

    r = ((1 - wz) * (1 - wth) * R_grid[iz, ith]
         + (1 - wz) * wth * R_grid[iz, ith + 1]
         + wz * (1 - wth) * R_grid[iz + 1, ith]
         + wz * wth * R_grid[iz + 1, ith + 1])
    return np.nan_to_num(r, nan=1.0)


# ---------------------------------------------------------------------------
#  Highlight ring
# ---------------------------------------------------------------------------

def add_highlight_ring(fig, highlight_year, t_min, t_max,
                       R_grid, z_vals, theta_vals, z_stretch=1.5):
    """Add a red section ring at *highlight_year*."""
    if highlight_year is None:
        return
    span = t_max - t_min + 1e-9
    norm_t = (highlight_year - t_min) / span
    if norm_t < 0 or norm_t > 1:
        return

    iz = min(int(norm_t * (len(z_vals) - 1)), len(z_vals) - 2)
    r_row = R_grid[iz]
    x_ring = r_row * np.cos(theta_vals)
    y_ring = r_row * np.sin(theta_vals)
    z_ring = np.full_like(theta_vals, norm_t * z_stretch)

    fig.add_trace(go.Scatter3d(
        x=x_ring, y=y_ring, z=z_ring,
        mode='lines',
        line=dict(color='#FF3333', width=10),
        name=f"Year {highlight_year:.1f}",
        hovertemplate=f"Section: {highlight_year:.1f}<extra></extra>",
        showlegend=True,
    ))
