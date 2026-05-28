# plot/comparison_modes.py
# A/B comparison and Oreo visualisation modes

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO

from plot.core_helpers import (
    generate_ghost_horn_mesh, project_to_surface_batch, project_to_surface,
)
from utils import deterministic_uniform_array

# ---------------------------------------------------------------------------
_DARK_SCENE = dict(
    xaxis=dict(visible=False, showbackground=False),
    yaxis=dict(visible=False, showbackground=False),
    zaxis=dict(visible=False, showbackground=False),
    bgcolor='#050510',
    dragmode='orbit',
)
_DARK_LAYOUT = dict(
    paper_bgcolor='#050510',
    margin=dict(l=0, r=0, t=40, b=0),
    height=900,
    legend=dict(font=dict(color='#b0b0b0')),
)


def _empty_fig():
    fig = go.Figure()
    fig.update_layout(**_DARK_LAYOUT, scene=_DARK_SCENE)
    return fig


# ---------------------------------------------------------------------------
#  Dual Horn (A/B side-by-side)
# ---------------------------------------------------------------------------

def build_dual_horn(df, a_name, b_name):
    if df.empty or a_name == "None" or b_name == "None":
        return _empty_fig()

    df = df.copy()
    df['theta'] = deterministic_uniform_array(df['name'], 0, 2 * np.pi)
    t_min, t_max = df['time'].min(), df['time'].max()
    X, Y, Z_plot, density, R_grid, z_vals, theta_vals, t_min, t_max = generate_ghost_horn_mesh(t_min, t_max, df)
    if X.size == 0:
        return _empty_fig()

    df_show = df if len(df) <= 6000 else df.sample(6000, random_state=42)
    norm_t = (df_show['time'].values - t_min) / (t_max - t_min + 1e-6)
    norm_th = df_show['theta'].values / (2 * np.pi)
    r_pts = project_to_surface_batch(norm_t, norm_th, R_grid, z_vals, theta_vals)
    px = r_pts * np.cos(df_show['theta'].values)
    py = r_pts * np.sin(df_show['theta'].values)
    pz = norm_t * 1.5
    sizes = np.clip(df_show['mass'].values * 1.5 + 4, 4, 18)

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scene'}, {'type': 'scene'}]],
        subplot_titles=(f"A: {a_name}", f"B: {b_name}"),
        horizontal_spacing=0.02,
    )

    for col in (1, 2):
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z_plot, surfacecolor=density, colorscale='Plasma_r',
            opacity=0.6, showscale=False,
            contours=dict(z=dict(show=True, color="#00FF7F")),
        ), row=1, col=col)
        fig.add_trace(go.Scatter3d(
            x=px, y=py, z=pz, mode='markers',
            marker=dict(size=sizes, color=df_show['time'], colorscale='Turbo', opacity=0.9),
        ), row=1, col=col)

    def _add_highlight(name, col, color):
        sel = df[df['name'] == name]
        if sel.empty:
            return
        row = sel.iloc[0]
        nt = (row['time'] - t_min) / (t_max - t_min + 1e-6)
        nth = row['theta'] / (2 * np.pi)
        r_h = project_to_surface(nt, nth, R_grid, z_vals, theta_vals)
        fig.add_trace(go.Scatter3d(
            x=[r_h * np.cos(row['theta'])], y=[r_h * np.sin(row['theta'])], z=[nt * 1.5],
            mode='markers',
            marker=dict(size=14, color=color, symbol='circle-open', line=dict(width=6, color=color)),
            name=name,
        ), row=1, col=col)

    if a_name != "None":
        _add_highlight(a_name, 1, '#FF4B4B')
    if b_name != "None":
        _add_highlight(b_name, 2, '#4BA3FF')

    cam = dict(eye=dict(x=1.3, y=1.3, z=0.8))
    fig.update_layout(**_DARK_LAYOUT, scene=dict(**_DARK_SCENE, camera=cam), scene2=dict(**_DARK_SCENE, camera=cam))
    return fig


# ---------------------------------------------------------------------------
#  ΔHORN Differential Map
# ---------------------------------------------------------------------------

def build_delta_horn(df, a_name, b_name):
    if df.empty or a_name == "None" or b_name == "None":
        return _empty_fig()

    df = df.copy()
    df['theta'] = deterministic_uniform_array(df['name'], 0, 2 * np.pi)
    t_min, t_max = df['time'].min(), df['time'].max()
    X_full, Y_full, Z_full, _, R_full, z_vals, theta_vals, t_min, t_max = generate_ghost_horn_mesh(t_min, t_max, df)
    if X_full.size == 0:
        return _empty_fig()

    df_a = df.copy()
    if a_name in df_a['name'].values:
        df_a.loc[df_a['name'] == a_name, 'mass'] *= 3.0
    _, _, _, _, R_a, _, _, _, _ = generate_ghost_horn_mesh(t_min, t_max, df_a)

    df_b = df.copy()
    if b_name in df_b['name'].values:
        df_b.loc[df_b['name'] == b_name, 'mass'] *= 3.0
    _, _, _, _, R_b, _, _, _, _ = generate_ghost_horn_mesh(t_min, t_max, df_b)

    R_delta = R_a - R_b
    threshold = 0.05
    color_map = np.where(np.abs(R_delta) < threshold, 0.5, np.where(R_delta > 0, 1.0, 0.0))

    THETA_full = np.outer(np.ones(len(z_vals)), theta_vals)
    X = R_full * np.cos(THETA_full)
    Y = R_full * np.sin(THETA_full)
    Z_plot = np.outer((z_vals - t_min) / (t_max - t_min + 1e-6) * 1.5, np.ones(len(theta_vals)))

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z_plot, surfacecolor=color_map,
        colorscale=[[0.0, '#4BA3FF'], [0.5, '#404040'], [1.0, '#FF4B4B']],
        opacity=0.7, showscale=False,
    ))
    fig.update_layout(**_DARK_LAYOUT, scene=dict(**_DARK_SCENE, camera=dict(eye=dict(x=1.3, y=1.3, z=0.8))))
    return fig


# ---------------------------------------------------------------------------
#  Flattened Wrinkle Cloud (shared helper for Oreo)
# ---------------------------------------------------------------------------

def build_flattened_wrinkle_cloud(df, keywords_data, z_offset=0.0, params=None):
    params = params or {}
    if df.empty or 'time' not in df.columns:
        t_min, t_max = 2000.0, 2025.0
    else:
        t_min, t_max = df['time'].min(), df['time'].max()

    kw_df = pd.DataFrame(keywords_data) if keywords_data else pd.DataFrame()
    n_kw = len(kw_df)
    spread = 24
    time_res, theta_res = 160, 260
    time_v = np.linspace(t_min, t_max, time_res)
    theta = np.linspace(0, 2 * np.pi, theta_res)
    TIME_g, THETA_g = np.meshgrid(time_v, theta, indexing='ij')
    norm_time = (TIME_g - t_min) / (t_max - t_min + 1e-6)

    if n_kw == 0:
        X = THETA_g / (2 * np.pi) * spread - spread / 2
        Y = norm_time * spread - spread / 2
        Z = np.full_like(X, z_offset)
        return X, Y, Z, np.zeros_like(X), np.array([]), np.array([]), np.array([]), kw_df

    kw_times = np.linspace(t_min + 0.1 * (t_max - t_min), t_max - 0.1 * (t_max - t_min), n_kw)
    kw_thetas = deterministic_uniform_array([f"oreo_{w}" for w in kw_df['kw']], 0, 2 * np.pi)
    kw_df = kw_df.copy()
    kw_df['time'] = kw_times
    kw_df['theta'] = kw_thetas
    kw_df['mass'] = kw_df['score'] * 35

    sigma_t = (t_max - t_min) / 6.0 if (t_max - t_min) > 0 else 1.0
    sigma_th = np.pi / 2.5
    max_m = kw_df['mass'].max() + 1e-6

    kt = kw_times[:, None, None]
    kth = kw_thetas[:, None, None]
    km = kw_df['mass'].values[:, None, None]
    dt = TIME_g[None] - kt
    dth_raw = np.abs(THETA_g[None] - kth)
    dth = np.minimum(dth_raw, 2 * np.pi - dth_raw)
    gauss = np.exp(-(dt ** 2 / (2 * sigma_t ** 2)) - (dth ** 2 / (2 * sigma_th ** 2)))
    distortion = np.sum(gauss * (km / max_m), axis=0)

    norm_theta = THETA_g / (2 * np.pi)
    wrinkle_base = distortion * params.get("wrinkle_strength", 2.2)
    wrinkle = (np.sin(8 * np.pi * norm_theta) * np.cos(4 * np.pi * norm_time) * 0.8
               + np.sin(16 * np.pi * norm_theta + np.pi / 3) * np.cos(8 * np.pi * norm_time) * 0.4
               + np.sin(24 * np.pi * norm_theta) * np.cos(12 * np.pi * norm_time) * 0.2)
    Z_base = (wrinkle_base + wrinkle) * params.get("z_compression", 0.05)

    X = THETA_g / (2 * np.pi) * spread - spread / 2
    Y = norm_time * spread - spread / 2
    Z = Z_base + z_offset
    color = (distortion + np.abs(wrinkle)) / (np.max(distortion + np.abs(wrinkle)) + 1e-6)

    t_idx = np.argmin(np.abs(time_v[:, None] - kw_times), axis=0)
    th_raw = np.abs(theta[None, :] - kw_thetas[:, None])
    th_idx = np.argmin(np.minimum(th_raw, 2 * np.pi - th_raw), axis=1)
    kw_z = Z_base[t_idx, th_idx] + 0.3 + z_offset
    kw_x = kw_thetas / (2 * np.pi) * spread - spread / 2
    kw_y = (kw_times - t_min) / (t_max - t_min + 1e-6) * spread - spread / 2
    return X, Y, Z, color, kw_x, kw_y, kw_z, kw_df


# ---------------------------------------------------------------------------
#  Oreo single group
# ---------------------------------------------------------------------------

def build_single_oreo(df, keywords_data, sensitivities, params, group_name=""):
    fig = go.Figure()
    spacing = params.get("layer_spacing", 1.0)

    X_u, Y_u, Z_u, c_u, kw_x, kw_y, kw_z_u, kw_df = build_flattened_wrinkle_cloud(df, keywords_data, spacing, params)
    fig.add_trace(go.Surface(
        x=X_u, y=Y_u, z=Z_u, surfacecolor=c_u,
        colorscale=params.get("color_scheme", "Plasma_r"),
        opacity=0.88, showscale=False, name=f"{group_name} Upper",
    ))

    Z_l = Z_u - 2 * spacing
    fig.add_trace(go.Surface(
        x=X_u, y=Y_u, z=Z_l, surfacecolor=c_u,
        colorscale=params.get("color_scheme", "Plasma_r"),
        opacity=0.88, showscale=False, name=f"{group_name} Lower",
    ))
    kw_z_l = kw_z_u - 2 * spacing

    n_kw = len(kw_df)
    if n_kw > 0 and kw_x.size > 0:
        max_sens = max(sensitivities) if sensitivities else 1.0
        n_safe = min(n_kw, len(sensitivities))
        for i in range(n_safe):
            sens_norm = sensitivities[i] / max_sens if max_sens > 0 else 0
            size = float(np.clip(kw_df.iloc[i]['score'] * 4 + 8, 8, 14))
            color = "#FFD700"
            fig.add_trace(go.Scatter3d(
                x=[kw_x[i]], y=[kw_y[i]], z=[kw_z_u[i]],
                mode='markers+text',
                marker=dict(size=size, color=color, symbol='diamond'),
                text=[kw_df.iloc[i]['kw']], textposition="top center",
                textfont=dict(color='#FFD700', size=9),
                showlegend=(i == 0), name="Keywords" if i == 0 else None,
            ))
            rng = np.random.RandomState(i)
            for _ in range(params.get("fiber_count", 3)):
                jx = rng.normal(0, sens_norm * 0.15, 2)
                jy = rng.normal(0, sens_norm * 0.15, 2)
                fig.add_trace(go.Scatter3d(
                    x=[kw_x[i] + jx[0], kw_x[i] + jx[1]],
                    y=[kw_y[i] + jy[0], kw_y[i] + jy[1]],
                    z=[kw_z_u[i], kw_z_l[i]],
                    mode='lines', line=dict(color=color, width=int(3 + sens_norm * 5)),
                    showlegend=False,
                ))

    fig.update_layout(
        title=dict(text=f"{group_name} — Oreo Structure", font=dict(color='#00FF7F', size=14)),
        scene=dict(xaxis=dict(title="Angle"), yaxis=dict(title="Time"), zaxis=dict(title="Layer"),
                   bgcolor='#050510', aspectratio=dict(x=1, y=1, z=0.2),
                   camera=dict(eye=dict(x=0, y=-2.5, z=1.5))),
        paper_bgcolor='#050510', height=800,
    )
    return fig


# ---------------------------------------------------------------------------
#  PDF report
# ---------------------------------------------------------------------------

def generate_report_pdf(fig_a, fig_b, df_a, df_b, keywords_a, keywords_b):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = [Paragraph("Kalim Ghost Horn — Observation Report", styles['Title']), Spacer(1, 12)]

    for label, fig in [("Group A", fig_a), ("Group B", fig_b)]:
        if fig is not None:
            try:
                img = fig.to_image(format="png", width=1000, height=700)
                elems.append(RLImage(BytesIO(img), width=480, height=336))
            except Exception:
                elems.append(Paragraph(f"({label} figure export failed)", styles['Normal']))

    for label, kws in [("A", keywords_a), ("B", keywords_b)]:
        elems.append(Paragraph(f"Top Keywords {label}:", styles['Heading2']))
        text = ", ".join(kw['kw'] for kw in (kws or [])[:20]) or "—"
        elems.append(Paragraph(text, styles['Normal']))

    doc.build(elems)
    return buf.getvalue()
