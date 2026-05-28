# plot/special_modes.py
# Chessboard, Cao analysis, Postal-Möbius unfold

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from plot.core_helpers import generate_ghost_horn_mesh
from utils import deterministic_uniform, deterministic_uniform_array  # FIX: both needed

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
)


def _empty_fig(msg="No data"):
    fig = go.Figure()
    fig.update_layout(**_DARK_LAYOUT, scene=_DARK_SCENE)
    fig.add_annotation(text=msg, xref="paper", yref="paper", x=0.5, y=0.5,
                       showarrow=False, font=dict(size=20, color="#00FF7F"))
    return fig


# ---------------------------------------------------------------------------
#  Chessboard + King Zone
# ---------------------------------------------------------------------------

def build_chessboard(df, keywords_data):
    if df.empty or not keywords_data:
        return _empty_fig("No keywords or data — cannot unfold chessboard")

    kw_df = pd.DataFrame(keywords_data)
    kw_df['theta'] = deterministic_uniform_array([f"chess_{w}" for w in kw_df['kw']], 0, 2 * np.pi)

    pts_x = kw_df['theta'].values / (2 * np.pi) * 2 - 1
    pts_y = deterministic_uniform_array([f"chess_y_{w}" for w in kw_df['kw']], -1, 1)

    grid_size = 8
    density = np.zeros((grid_size, grid_size))
    weight = np.zeros((grid_size, grid_size))
    for x, y, score in zip(pts_x, pts_y, kw_df['score']):
        i = int(np.clip((1 - y) / 2 * grid_size, 0, grid_size - 1))
        j = int(np.clip((x + 1) / 2 * grid_size, 0, grid_size - 1))
        density[i, j] += 1
        weight[i, j] += score

    total = density + weight * 2
    king_zones = np.argsort(total.flatten())[-3:]

    fig = go.Figure()

    for k in range(grid_size + 1):
        v = k / grid_size * 2 - 1
        fig.add_shape(type="line", x0=-1, x1=1, y0=v, y1=v, line=dict(color="#333333", width=1))
        fig.add_shape(type="line", x0=v, x1=v, y0=-1, y1=1, line=dict(color="#333333", width=1))

    for r in range(grid_size):
        for c in range(grid_size):
            if (r + c) % 2 == 0:
                x0 = c / grid_size * 2 - 1
                y0 = r / grid_size * 2 - 1
                fig.add_shape(type="rect", x0=x0, x1=x0 + 2 / grid_size,
                              y0=y0, y1=y0 + 2 / grid_size,
                              fillcolor="rgba(255,255,255,0.03)", line=dict(width=0))

    for idx in king_zones:
        i, j = divmod(idx, grid_size)
        x0 = j / grid_size * 2 - 1
        y0 = i / grid_size * 2 - 1
        fig.add_shape(type="rect", x0=x0, x1=x0 + 2 / grid_size,
                      y0=y0, y1=y0 + 2 / grid_size,
                      line=dict(color="#FF3333", width=3),
                      fillcolor="rgba(255,50,50,0.08)")

    fig.add_trace(go.Scatter(
        x=pts_x, y=pts_y, mode='markers+text',
        marker=dict(size=kw_df['score'] * 18 + 8, color='#FFD700',
                    line=dict(width=1, color='#FFA500'), opacity=0.9),
        text=kw_df['kw'], textposition="top center",
        textfont=dict(color='#FFD700', size=10),
        hovertemplate="<b>%{text}</b><br>Score: %{marker.size:.0f}<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor='#050510', plot_bgcolor='#050510', height=900,
        xaxis=dict(visible=False, range=[-1.05, 1.05]),
        yaxis=dict(visible=False, range=[-1.05, 1.05], scaleanchor='x'),
    )
    return fig


# ---------------------------------------------------------------------------
#  Cao Keyword Analysis
# ---------------------------------------------------------------------------

def build_cao_analysis(keywords_data, sub_mode_id="fusion"):
    """sub_mode_id: one of 'fusion', 'weight', 'cube_3d' (language-agnostic)."""
    if not keywords_data:
        return _empty_fig("No keyword data")

    words = [d['kw'] for d in keywords_data]
    weights = [d['score'] for d in keywords_data]
    sensitivities = [d['sensitivity'] for d in keywords_data]

    if sub_mode_id == "cube_3d":
        x_vals = list(range(len(words)))
        fig = go.Figure(go.Scatter3d(
            x=x_vals, y=weights, z=sensitivities,
            mode='markers+text', text=words,
            marker=dict(size=[w * 12 + 8 for w in weights],
                        color=sensitivities, colorscale='Plasma', opacity=0.85,
                        line=dict(width=1, color='rgba(255,255,255,0.3)')),
            textfont=dict(size=9, color='#e0e0e0'),
        ))
        fig.update_layout(
            title=dict(text="Cao 3-D Cube View", font=dict(color='#00FF7F')),
            scene=dict(
                xaxis=dict(title='Rank', gridcolor='#222'),
                yaxis=dict(title='Weight', gridcolor='#222'),
                zaxis=dict(title='Sensitivity', gridcolor='#222'),
                bgcolor='#050510', dragmode='orbit',
            ),
            paper_bgcolor='#050510', height=900,
        )
    else:
        y_pos = list(range(len(words)))
        fig = go.Figure()

        if sub_mode_id == "weight":
            fig.add_trace(go.Bar(
                y=y_pos, x=weights, orientation='h',
                marker_color=sensitivities, marker_colorscale='Plasma',
                text=words, textposition='outside', textfont=dict(color='#e0e0e0'),
            ))
            fig.update_layout(title=dict(text="Cao Weight Bar", font=dict(color='#00FF7F')))
        else:
            fig.add_trace(go.Bar(
                y=y_pos, x=weights, orientation='h',
                name="Weight", marker_color='rgba(0,255,127,0.5)',
            ))
            fig.add_trace(go.Scatter(
                y=y_pos, x=weights,
                mode='markers+text', text=words,
                marker=dict(size=[s * 40 + 12 for s in sensitivities],
                            color=sensitivities, colorscale='Viridis', opacity=0.85),
                name="Sensitivity", textposition="middle right",
                textfont=dict(color='#e0e0e0', size=10),
            ))
            fig.update_layout(title=dict(text="Cao Fusion Bar", font=dict(color='#00FF7F')))

        fig.update_layout(
            paper_bgcolor='#050510', plot_bgcolor='#050510', height=900,
            yaxis=dict(ticktext=words, tickvals=y_pos,
                       title=dict(text="Keywords", font=dict(color='#aaa')),
                       tickfont=dict(color='#b0b0b0')),
            xaxis=dict(title=dict(text="Weight", font=dict(color='#aaa')),
                       tickfont=dict(color='#b0b0b0'), gridcolor='#1a1a1a'),
            barmode='overlay',
        )

    return fig


# ---------------------------------------------------------------------------
#  Postal-Möbius Unfold (4 required args)
# ---------------------------------------------------------------------------

def build_postal_mobius_x_interaction(df_a, df_b, keywords_a, keywords_b):
    has_a = df_a is not None and not df_a.empty
    has_b = df_b is not None and not df_b.empty

    if not has_a and not has_b:
        return _empty_fig()

    times = []
    if has_a and 'time' in df_a.columns:
        times.append(df_a['time'])
    if has_b and 'time' in df_b.columns:
        times.append(df_b['time'])

    if not times:
        t_min, t_max = 2000.0, 2025.0
    else:
        t_all = pd.concat(times)
        t_min, t_max = t_all.min(), t_all.max()
        if pd.isna(t_min) or pd.isna(t_max):
            t_min, t_max = 2000.0, 2025.0

    df_all = pd.concat([d for d in [df_a, df_b] if d is not None and not d.empty]).copy()
    df_all['theta'] = deterministic_uniform_array(df_all['name'], 0, 2 * np.pi)
    _, _, _, density_color, R_grid, z_vals, theta_vals, t_min, t_max = generate_ghost_horn_mesh(t_min, t_max, df_all)

    u = np.linspace(0, 2 * np.pi, 200)
    v = np.linspace(-1, 1, 100)
    U, V = np.meshgrid(u, v)

    x_mob = (1 + 0.5 * V * np.cos(U / 2)) * np.cos(U)
    y_mob = (1 + 0.5 * V * np.cos(U / 2)) * np.sin(U)
    z_mob = 0.5 * V * np.sin(U / 2)

    norm_u = U / (2 * np.pi)
    h_dist = np.interp(norm_u.flatten(),
                       np.linspace(0, 1, len(theta_vals)),
                       density_color.mean(axis=0))
    h_dist = h_dist.reshape(U.shape) * 0.8
    z_mob += h_dist

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=x_mob, y=y_mob, z=z_mob, surfacecolor=h_dist,
        colorscale='Plasma_r', opacity=0.85, showscale=True,
        colorbar=dict(title=dict(text="Density", font=dict(color='#aaa')), tickfont=dict(color='#aaa')),
    ))

    def _embed_kw(keywords, color, suffix):
        if not keywords:
            return
        kw_df = pd.DataFrame(keywords)
        n = len(kw_df)
        if n == 0:
            return
        u_pos = deterministic_uniform_array([f"mob_{suffix}_{w}" for w in kw_df['kw']], 0, 2 * np.pi)
        v_pos = deterministic_uniform_array([f"mob_v_{suffix}_{w}" for w in kw_df['kw']], -0.8, 0.8)
        kw_x = (1 + 0.5 * v_pos * np.cos(u_pos / 2)) * np.cos(u_pos)
        kw_y = (1 + 0.5 * v_pos * np.cos(u_pos / 2)) * np.sin(u_pos)
        kw_z = 0.5 * v_pos * np.sin(u_pos / 2) + 0.15
        kw_sizes = np.clip(kw_df['score'].values * 50 + 15, 15, 80)
        fig.add_trace(go.Scatter3d(
            x=kw_x, y=kw_y, z=kw_z, mode='markers+text',
            marker=dict(size=kw_sizes, color=color, opacity=0.9,
                        symbol='diamond', line=dict(width=1, color='white')),
            text=kw_df['kw'], textposition="top center",
            textfont=dict(color=color, size=9), name=f"Keywords {suffix}",
        ))

    _embed_kw(keywords_a, '#FFA500', "A")
    _embed_kw(keywords_b, '#00BFFF', "B")

    # Co-occurrence bridges — uses deterministic_uniform (scalar)
    if has_a and has_b and keywords_a and keywords_b:
        dict_a = {d['kw']: d['score'] for d in keywords_a}
        dict_b = {d['kw']: d['score'] for d in keywords_b}
        shared = set(dict_a) & set(dict_b)
        for kw in shared:
            w = (dict_a[kw] + dict_b[kw]) / 2
            if w > 0.15:
                ub = deterministic_uniform(f"bridge_{kw}", 0, 2 * np.pi)
                va = deterministic_uniform(f"bridge_va_{kw}", -0.8, 0.8)
                vb = va + np.pi
                if vb > 1:
                    vb -= 2
                ax = (1 + 0.5 * va * np.cos(ub / 2)) * np.cos(ub)
                ay = (1 + 0.5 * va * np.cos(ub / 2)) * np.sin(ub)
                az = 0.5 * va * np.sin(ub / 2)
                bx = (1 + 0.5 * vb * np.cos(ub / 2)) * np.cos(ub)
                by_ = (1 + 0.5 * vb * np.cos(ub / 2)) * np.sin(ub)
                bz = 0.5 * vb * np.sin(ub / 2)

                fig.add_trace(go.Scatter3d(
                    x=[ax, bx], y=[ay, by_], z=[az, bz],
                    mode='lines', line=dict(color='magenta', width=int(6 + w * 15)),
                    showlegend=False,
                ))
                fig.add_trace(go.Scatter3d(
                    x=[(ax + bx) / 2], y=[(ay + by_) / 2], z=[(az + bz) / 2],
                    mode='markers+text',
                    marker=dict(size=w * 60 + 15, color='magenta', opacity=0.8),
                    text=[f"{kw}"], textposition="top center",
                    textfont=dict(color='magenta', size=9), showlegend=False,
                ))

    fig.update_layout(
        title=dict(text="Postal-Möbius Unfold", font=dict(color='#00FF7F', size=14)),
        scene=dict(
            xaxis=dict(visible=True, title='X', gridcolor='#1a1a1a', zerolinecolor='#00FF7F'),
            yaxis=dict(visible=True, title='Y', gridcolor='#1a1a1a', zerolinecolor='#00FF7F'),
            zaxis=dict(visible=True, title='Twist', gridcolor='#1a1a1a', zerolinecolor='#00FF7F'),
            bgcolor='#050510', dragmode='orbit',
            aspectratio=dict(x=1, y=1, z=1.2),
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.4)),
        ),
        paper_bgcolor='#050510', height=900, margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig
