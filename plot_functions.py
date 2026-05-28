# plot_functions.py
# Re-export all plot builders for convenient import

from plot.core_helpers import generate_ghost_horn_mesh, project_to_surface, add_highlight_ring
from plot.single_modes import (
    build_single_horn, build_starfield_horn,
    build_keyword_terrain, build_wrinkle_cloud,
)
from plot.comparison_modes import (
    build_dual_horn, build_delta_horn,
    build_flattened_wrinkle_cloud, build_single_oreo,
    generate_report_pdf,
)
from plot.special_modes import (
    build_chessboard, build_cao_analysis,
    build_postal_mobius_x_interaction,
)
