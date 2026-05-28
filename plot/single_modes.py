# plot/single_modes.py
# Single-figure visualisation modes

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from plot.core_helpers import (
    generate_ghost_horn_mesh, project_to_surface_batch, add_highlight_ring,
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
    margin=dict(l=0, r=0, t=0, b=0),
    height=900,
    legend=dict(font=dict(color='#b0b0b0')),
)


def _empty_fig():
    fig = go.Figure()
    fig.update_layout(**_DARK_LAYOUT, scene=_DARK_SCENE)
    return fig


# ---------------------------------------------------------------------------
#  Single Horn
# ---------------------------------------------------------------------------

def build_single_horn(df, highlight_year=None):
    if df.empty:
        return _empty_fig()

    df = df.copy()
    df['theta'] = deterministic_uniform_array(df['name'], 0, 2 * np.pi)
    t_min_raw, t_max_raw = df['time'].min(), df['time'].max()

    X, Y, Z_plot, density, R_grid, z_vals, theta_vals, t_min, t_max = generate_ghost_horn_mesh(t_min_raw, t_max_raw, df)
    if X.size == 0:
        return _empty_fig()

    df_show = df if len(df) <= 6000 else df.sample(6000, random_state=42)
    norm_t = (df_show['time'].values - t_min) / (t_max - t_min + 1e-9)
    norm_th = df_show['theta'].values / (2 * np.pi)
    r_pts = project_to_surface_batch(norm_t, norm_th, R_grid, z_vals, theta_vals)
    px = r_pts * np.cos(df_show['theta'].values)
    py = r_pts * np.sin(df_show['theta'].values)
    pz = norm_t * 1.5

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z_plot, surfacecolor=density,
        colorscale='Plasma_r', opacity=0.6,
        showscale=True, colorbar=dict(title=dict(text="Density", font=dict(color='#aaa')), tickfont=dict(color='#aaa')),
        contours=dict(z=dict(show=True, color="#00FF7F")),
    ))

    sizes = np.clip(df_show['mass'].values * 1.5 + 4, 4, 18)
    fig.add_trace(go.Scatter3d(
        x=px, y=py, z=pz, mode='markers',
        marker=dict(size=sizes, color=df_show['time'], colorscale='Turbo', opacity=0.9,
                    line=dict(width=0)),
        text=df_show['name'],
        hovertemplate="<b>%{text}</b><br>t = %{marker.color:.2f}<extra></extra>",
        name='Papers',
    ))

    add_highlight_ring(fig, highlight_year, t_min, t_max, R_grid, z_vals, theta_vals)

    fig.update_layout(
        **_DARK_LAYOUT,
        scene=dict(**_DARK_SCENE, camera=dict(eye=dict(x=1.3, y=1.3, z=0.8))),
    )
    return fig


# ---------------------------------------------------------------------------
#  Starfield Horn
# ---------------------------------------------------------------------------

def build_starfield_horn(df, keywords_data, highlight_year=None):
    if df.empty:
        return _empty_fig()

    df_s = df.copy()
    df_s['theta'] = deterministic_uniform_array(df_s['name'], 0, 2 * np.pi)
    t_min_raw, t_max_raw = df_s['time'].min(), df_s['time'].max()

    X, Y, Z_plot, density, R_grid, z_vals, theta_vals, t_min, t_max = generate_ghost_horn_mesh(t_min_raw, t_max_raw, df_s)
    if X.size == 0:
        return _empty_fig()

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z_plot, surfacecolor=density,
        colorscale='Plasma_r', opacity=0.6, showscale=True,
        colorbar=dict(title=dict(text="Density", font=dict(color='#aaa')), tickfont=dict(color='#aaa')),
        contours=dict(z=dict(show=True, color="#00FF7F")),
    ))

    if keywords_data:
        kw_df = pd.DataFrame(keywords_data)
        n_kw = len(kw_df)
        if n_kw > 0:
            kw_df['time'] = np.linspace(t_min + 0.1 * (t_max - t_min),
                                        t_max - 0.1 * (t_max - t_min), n_kw)
            kw_df['theta'] = deterministic_uniform_array(
                [f"kw_{w}" for w in kw_df['kw']], 0, 2 * np.pi)
            norm_kw_t = (kw_df['time'].values - t_min) / (t_max - t_min + 1e-6)
            norm_kw_th = kw_df['theta'].values / (2 * np.pi)
            kw_r = project_to_surface_batch(norm_kw_t, norm_kw_th, R_grid, z_vals, theta_vals)
            kw_px = kw_r * np.cos(kw_df['theta'].values)
            kw_py = kw_r * np.sin(kw_df['theta'].values)
            kw_pz = norm_kw_t * 1.5
            kw_sizes = np.clip(kw_df['score'].values * 4 + 8, 8, 14)
            fig.add_trace(go.Scatter3d(
                x=kw_px, y=kw_py, z=kw_pz, mode='markers+text',
                marker=dict(size=kw_sizes, color='#FFD700', opacity=0.95,
                            symbol='diamond', line=dict(width=1, color='#FFA500')),
                text=kw_df['kw'], textposition="top center",
                textfont=dict(color='#FFD700', size=10), name='Keywords',
            ))

    add_highlight_ring(fig, highlight_year, t_min, t_max, R_grid, z_vals, theta_vals)

    fig.update_layout(
        **_DARK_LAYOUT,
        scene=dict(**_DARK_SCENE, camera=dict(eye=dict(x=1.3, y=1.3, z=0.8))),
    )
    return fig


# ---------------------------------------------------------------------------
#  Keyword Square Terrain (3-D unfold)
# ---------------------------------------------------------------------------

def _build_terrain_base(kw_df, t_min, t_max, spread=20, time_res=140, theta_res=220):
    n_kw = len(kw_df)
    kw_df = kw_df.copy()
    kw_df['time'] = np.linspace(t_min + 0.1 * (t_max - t_min),
                                t_max - 0.1 * (t_max - t_min), max(n_kw, 1))
    kw_df['theta'] = deterministic_uniform_array(
        [f"terrain_{w}" for w in kw_df['kw']], 0, 2 * np.pi)
    kw_df['mass'] = kw_df['score'] * 30

    time_v = np.linspace(t_min, t_max, time_res)
    theta = np.linspace(0, 2 * np.pi, theta_res)
    TIME_g, THETA_g = np.meshgrid(time_v, theta, indexing='ij')

    sigma_t = (t_max - t_min) / 7.0 if (t_max - t_min) > 0 else 1.0
    sigma_th = np.pi / 2.8
    max_m = kw_df['mass'].max() + 1e-6

    kw_times = kw_df['time'].values[:, None, None]
    kw_thetas = kw_df['theta'].values[:, None, None]
    kw_masses = kw_df['mass'].values[:, None, None]
    dt = TIME_g[None] - kw_times
    dth_raw = np.abs(THETA_g[None] - kw_thetas)
    dth = np.minimum(dth_raw, 2 * np.pi - dth_raw)
    gauss = np.exp(-(dt ** 2 / (2 * sigma_t ** 2)) - (dth ** 2 / (2 * sigma_th ** 2)))
    distortion = np.sum(gauss * (kw_masses / max_m), axis=0)

    Z = distortion * 2.8
    X = THETA_g / (2 * np.pi) * spread - spread / 2
    Y = (TIME_g - t_min) / (t_max - t_min + 1e-6) * spread - spread / 2
    color = distortion / (distortion.max() + 1e-6)

    t_idx = np.argmin(np.abs(time_v[:, None] - kw_df['time'].values), axis=0)
    th_raw = np.abs(theta[None, :] - kw_df['theta'].values[:, None])
    th_idx = np.argmin(np.minimum(th_raw, 2 * np.pi - th_raw), axis=1)
    kw_z = Z[t_idx, th_idx] + 0.25
    kw_x = kw_df['theta'].values / (2 * np.pi) * spread - spread / 2
    kw_y = (kw_df['time'].values - t_min) / (t_max - t_min + 1e-6) * spread - spread / 2
    return X, Y, Z, color, kw_x, kw_y, kw_z, kw_df


def build_keyword_terrain(df, keywords_data):
    if df.empty or not keywords_data:
        fig = _empty_fig()
        fig.add_annotation(text="No data or keywords", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=20, color="#00FF7F"))
        return fig

    t_min, t_max = df['time'].min(), df['time'].max()
    kw_df = pd.DataFrame(keywords_data)
    X, Y, Z, color, kw_x, kw_y, kw_z, kw_df = _build_terrain_base(kw_df, t_min, t_max)

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z, surfacecolor=color, colorscale='Plasma_r', opacity=0.85, showscale=True,
        colorbar=dict(title=dict(text="Density", font=dict(color='#aaa')), tickfont=dict(color='#aaa')),
    ))
    kw_sizes = np.clip(kw_df['score'].values * 4 + 8, 8, 14)
    fig.add_trace(go.Scatter3d(
        x=kw_x, y=kw_y, z=kw_z, mode='markers+text',
        marker=dict(size=kw_sizes, color='#FFD700', opacity=0.9,
                    symbol='diamond', line=dict(width=1, color='#FFA500')),
        text=kw_df['kw'], textposition="top center",
        textfont=dict(color='#FFD700', size=10), name='Keywords',
    ))
    fig.update_layout(**_DARK_LAYOUT, scene=dict(**_DARK_SCENE, camera=dict(eye=dict(x=2.2, y=2.2, z=1.6))))
    return fig


# ---------------------------------------------------------------------------
#  Wrinkle Cloud Map
# ---------------------------------------------------------------------------

def build_wrinkle_cloud(df, keywords_data):
    if df.empty or not keywords_data:
        fig = _empty_fig()
        fig.add_annotation(text="No data or keywords", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=20, color="#00FF7F"))
        return fig

    t_min, t_max = df['time'].min(), df['time'].max()
    kw_df_src = pd.DataFrame(keywords_data)
    n_kw = len(kw_df_src)
    kw_df = kw_df_src.copy()
    kw_df['time'] = np.linspace(t_min + 0.1 * (t_max - t_min),
                                t_max - 0.1 * (t_max - t_min), max(n_kw, 1))
    kw_df['theta'] = deterministic_uniform_array([f"wrinkle_{w}" for w in kw_df['kw']], 0, 2 * np.pi)
    kw_df['mass'] = kw_df['score'] * 35

    spread = 24
    time_res, theta_res = 160, 260
    time_v = np.linspace(t_min, t_max, time_res)
    theta = np.linspace(0, 2 * np.pi, theta_res)
    TIME_g, THETA_g = np.meshgrid(time_v, theta, indexing='ij')
    sigma_t = (t_max - t_min) / 6.0 if (t_max - t_min) > 0 else 1.0
    sigma_th = np.pi / 2.5
    max_m = kw_df['mass'].max() + 1e-6

    kw_times = kw_df['time'].values[:, None, None]
    kw_thetas = kw_df['theta'].values[:, None, None]
    kw_masses = kw_df['mass'].values[:, None, None]
    dt = TIME_g[None] - kw_times
    dth_raw = np.abs(THETA_g[None] - kw_thetas)
    dth = np.minimum(dth_raw, 2 * np.pi - dth_raw)
    gauss = np.exp(-(dt ** 2 / (2 * sigma_t ** 2)) - (dth ** 2 / (2 * sigma_th ** 2)))
    distortion = np.sum(gauss * (kw_masses / max_m), axis=0)

    norm_time = (TIME_g - t_min) / (t_max - t_min + 1e-6)
    norm_theta = THETA_g / (2 * np.pi)
    wrinkle_base = distortion * 2.2
    wrinkle = (np.sin(8 * np.pi * norm_theta) * np.cos(4 * np.pi * norm_time) * 0.8
               + np.sin(16 * np.pi * norm_theta + np.pi / 3) * np.cos(8 * np.pi * norm_time) * 0.4
               + np.sin(24 * np.pi * norm_theta) * np.cos(12 * np.pi * norm_time) * 0.2)
    Z = wrinkle_base + wrinkle
    X = THETA_g / (2 * np.pi) * spread - spread / 2
    Y = norm_time * spread - spread / 2
    color = (distortion + np.abs(wrinkle)) / (np.max(distortion + np.abs(wrinkle)) + 1e-6)

    t_idx = np.argmin(np.abs(time_v[:, None] - kw_df['time'].values), axis=0)
    th_raw = np.abs(theta[None, :] - kw_df['theta'].values[:, None])
    th_idx = np.argmin(np.minimum(th_raw, 2 * np.pi - th_raw), axis=1)
    kw_z = Z[t_idx, th_idx] + 0.3
    kw_x = kw_df['theta'].values / (2 * np.pi) * spread - spread / 2
    kw_y = (kw_df['time'].values - t_min) / (t_max - t_min + 1e-6) * spread - spread / 2

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z, surfacecolor=color, colorscale='Plasma_r', opacity=0.88, showscale=True,
        colorbar=dict(title=dict(text="Wrinkle Intensity", font=dict(color='#aaa')), tickfont=dict(color='#aaa')),
    ))
    kw_sizes = np.clip(kw_df['score'].values * 4 + 8, 8, 14)
    fig.add_trace(go.Scatter3d(
        x=kw_x, y=kw_y, z=kw_z, mode='markers+text',
        marker=dict(size=kw_sizes, color='#FFD700', opacity=0.95,
                    symbol='diamond', line=dict(width=1, color='#FFA500')),
        text=kw_df['kw'], textposition="top center",
        textfont=dict(color='#FFD700', size=10), name='Keywords',
    ))
    fig.update_layout(**_DARK_LAYOUT, scene=dict(**_DARK_SCENE, camera=dict(eye=dict(x=2.4, y=2.4, z=1.8))))
    return fig
