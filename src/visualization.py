"""Padrão visual e funções de gráfico reaproveitadas nos notebooks.

Regras seguidas em todos os gráficos:
- o título diz a conclusão ("O que o gráfico mostra"), o subtítulo diz o que foi medido;
- vermelho, amarelo e verde são reservados para detrator, neutro e promotor;
- cinza = contexto, vermelho = onde está o problema;
- números em formato brasileiro (vírgula decimal).
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, to_rgb
from matplotlib.ticker import FuncFormatter

from src import config

# --------------------------------------------------------------------------------------
# Paleta
# --------------------------------------------------------------------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

HIGHLIGHT = "#2a78d6"  # azul: destaque neutro (ex.: modelo escolhido)
CONTEXT = "#c3c2b7"  # cinza: barras de contexto
PROBLEM = "#d03b3b"  # vermelho: onde está o problema

CATEGORY_COLORS = {"detrator": "#d03b3b", "neutro": "#fab219", "promotor": "#0ca30c"}
CATEGORY_LABELS = {
    "detrator": "Detratores (< 7)",
    "neutro": "Neutros (7 a < 9)",
    "promotor": "Promotores (>= 9)",
}
RISK_TIER_COLORS = {
    "Crítico": "#d03b3b",
    "Alto": "#ec835a",
    "Atenção": "#fab219",
    "Potencial promotor": "#0ca30c",
}
NEGATIVE_COLOR = "#e34948"
POSITIVE_COLOR = "#2a78d6"
DIVERGING_CMAP = LinearSegmentedColormap.from_list(
    "nps_diverging", [NEGATIVE_COLOR, "#f0efec", POSITIVE_COLOR]
)


def apply_style() -> None:
    """Aplica o padrão visual do projeto em todos os gráficos seguintes."""
    mpl.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "figure.dpi": 110,
            "savefig.dpi": 160,
            "savefig.bbox": "tight",
            "font.family": "sans-serif",
            "font.sans-serif": ["Segoe UI", "Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 10,
            "text.color": INK,
            "axes.labelcolor": INK_SECONDARY,
            "axes.edgecolor": AXIS,
            "axes.titlesize": 13,
            "axes.titleweight": "semibold",
            "axes.titlelocation": "left",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "axes.axisbelow": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelcolor": INK_SECONDARY,
            "ytick.labelcolor": INK_SECONDARY,
            "ytick.left": False,
            "legend.frameon": False,
        }
    )


# --------------------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------------------
def fmt_number(value: float, decimals: int = 1) -> str:
    """Formata número no padrão brasileiro (1.234,5)."""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".")


def fmt_percent(value: float, decimals: int = 0) -> str:
    """Formata percentual no padrão numérico brasileiro."""
    return f"{fmt_number(value, decimals)}%"


percent_axis = FuncFormatter(lambda value, _: fmt_percent(value))
decimal_axis = FuncFormatter(lambda value, _: fmt_number(value, 1))


def text_color_for(fill_color: str) -> str:
    """Branco ou preto, o que tiver mais contraste com a cor de fundo do rótulo."""
    channels = np.array(to_rgb(fill_color))
    linear = np.where(
        channels <= 0.03928, channels / 12.92, ((channels + 0.055) / 1.055) ** 2.4
    )
    luminance = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    return "white" if luminance < 0.2 else INK


def set_titles(
    ax, title: str, subtitle: str | None = None, legend_row: bool = False
) -> None:
    """Título (a conclusão) + subtítulo (o que foi medido), alinhados à esquerda.

    Com legend_row=True sobra uma linha entre o subtítulo e o gráfico para a legenda
    (ver add_top_legend). As distâncias são em pontos, então não dependem do tamanho da figura.
    """
    legend_space = 20 if legend_row else 0
    subtitle_space = 18 if subtitle else 0
    ax.set_title(title, loc="left", pad=8 + legend_space + subtitle_space)
    if subtitle:
        ax.annotate(
            subtitle,
            xy=(0, 1),
            xycoords="axes fraction",
            xytext=(0, 6 + legend_space),
            textcoords="offset points",
            va="bottom",
            color=INK_SECONDARY,
            fontsize=9.5,
        )


def add_top_legend(ax, handles=None, ncols: int = 3) -> None:
    """Legenda em uma linha logo acima da área do gráfico, alinhada à esquerda."""
    kwargs = {"handles": handles} if handles is not None else {}
    ax.legend(
        loc="lower left",
        bbox_to_anchor=(0, 1.0),
        ncols=ncols,
        fontsize=9,
        borderaxespad=0.2,
        handlelength=1.2,
        columnspacing=1.6,
        **kwargs,
    )


def save_figure(fig, filename: str) -> None:
    """Salva o gráfico em reports/figures para uso nos slides."""
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.FIGURES_DIR / filename)


def group_labels_with_count(counts: pd.Series) -> list[str]:
    """Rótulo do eixo com o tamanho do grupo, para o leitor saber o peso de cada barra."""
    return [f"{label}\n({fmt_number(count, 0)})" for label, count in counts.items()]


# --------------------------------------------------------------------------------------
# Gráficos da análise exploratória
# --------------------------------------------------------------------------------------
def plot_nps_scale(df: pd.DataFrame, title: str, subtitle: str):
    """Régua horizontal com a divisão detratores / neutros / promotores."""
    shares = (
        df["nps_category"]
        .value_counts(normalize=True)
        .reindex(config.NPS_CATEGORY_ORDER)
        * 100
    )
    fig, ax = plt.subplots(figsize=(10, 2.3))
    left = 0.0
    for category, share in shares.items():
        color = CATEGORY_COLORS[category]
        ax.barh(
            0,
            share,
            left=left,
            color=color,
            height=0.55,
            edgecolor=SURFACE,
            linewidth=2,
        )
        label = f"{CATEGORY_LABELS[category]}\n{fmt_percent(share, 1)}"
        if share >= 12:
            ax.text(
                left + share / 2,
                0,
                label,
                ha="center",
                va="center",
                color=text_color_for(color),
                fontsize=10,
            )
        else:
            center = left + share / 2
            ax.annotate(
                label,
                xy=(center, -0.3),
                xytext=(center, -0.75),
                ha="right" if center < 95 else "left",
                va="top",
                fontsize=9,
                color=INK_SECONDARY,
                arrowprops={"arrowstyle": "-", "color": MUTED, "linewidth": 0.8},
            )
        left += share
    ax.set_xlim(0, 100)
    ax.set_ylim(-1.2, 0.5)
    ax.axis("off")
    set_titles(ax, title, subtitle)
    return fig


def plot_score_distribution(df: pd.DataFrame, title: str, subtitle: str):
    """Histograma das notas, com as barras pintadas pela zona do NPS."""
    bin_edges = np.arange(0, 10.5, 0.5)
    counts, _ = np.histogram(df[config.TARGET_COLUMN], bins=bin_edges)
    fig, ax = plt.subplots(figsize=(10, 4))
    for left_edge, count in zip(bin_edges[:-1], counts):
        if left_edge >= config.PROMOTER_LIMIT:
            color = CATEGORY_COLORS["promotor"]
        elif left_edge >= config.DETRACTOR_LIMIT:
            color = CATEGORY_COLORS["neutro"]
        else:
            color = CATEGORY_COLORS["detrator"]
        ax.bar(
            left_edge,
            count,
            width=0.5,
            align="edge",
            color=color,
            edgecolor=SURFACE,
            linewidth=1.5,
        )
    mean_score = df[config.TARGET_COLUMN].mean()
    ax.set_ylim(0, counts.max() * 1.15)
    ax.axvline(mean_score, ymax=1 / 1.15 * 1.08, color=INK_SECONDARY, linewidth=1)
    ax.text(
        mean_score,
        counts.max() * 1.09,
        f"média {fmt_number(mean_score)}",
        ha="center",
        va="bottom",
        color=INK_SECONDARY,
        fontsize=9,
    )
    ax.set_xticks(range(0, 11))
    ax.set_xlabel("Nota de NPS")
    ax.set_ylabel("Pedidos")
    handles = [
        mpl.patches.Patch(color=CATEGORY_COLORS[c], label=CATEGORY_LABELS[c])
        for c in config.NPS_CATEGORY_ORDER
    ]
    add_top_legend(ax, handles)
    set_titles(ax, title, subtitle, legend_row=True)
    return fig


def plot_correlation_bars(
    correlations: pd.Series, title: str, subtitle: str, weak_limit: float = 0.1
):
    """Barras horizontais com a correlação de cada variável com a nota."""
    ordered = correlations.sort_values()
    labels = [
        f"{config.FEATURE_LABELS.get(c, c)}  ·  {config.FEATURE_AREAS.get(c, '')}"
        for c in ordered.index
    ]
    colors = [
        (
            CONTEXT
            if abs(value) < weak_limit
            else (NEGATIVE_COLOR if value < 0 else POSITIVE_COLOR)
        )
        for value in ordered.values
    ]
    fig, ax = plt.subplots(figsize=(10, 0.38 * len(ordered) + 1.4))
    ax.barh(labels, ordered.values, color=colors, height=0.6)
    for position, value in enumerate(ordered.values):
        offset = 0.012 if value >= 0 else -0.012
        ax.text(
            value + offset,
            position,
            fmt_number(value, 2),
            va="center",
            ha="left" if value >= 0 else "right",
            fontsize=8.5,
            color=INK_SECONDARY,
        )
    ax.axvline(0, color=AXIS, linewidth=1)
    ax.set_xlim(-0.75, 0.75)
    ax.xaxis.set_major_formatter(decimal_axis)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Correlação de Spearman com a nota (-1 a +1)")
    set_titles(ax, title, subtitle)
    return fig


def detractor_rate_table(df: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Por grupo: pedidos, nota média, % detratores, % promotores e NPS."""
    grouped = df.groupby(group_column, observed=True)[config.TARGET_COLUMN]
    table = pd.DataFrame(
        {
            "pedidos": grouped.size(),
            "nota_media": grouped.mean(),
            "pct_detratores": grouped.apply(
                lambda s: (s < config.DETRACTOR_LIMIT).mean() * 100
            ),
            "pct_promotores": grouped.apply(
                lambda s: (s >= config.PROMOTER_LIMIT).mean() * 100
            ),
        }
    )
    table["nps"] = table["pct_promotores"] - table["pct_detratores"]
    return table.round(1)


def plot_detractor_rate(
    df: pd.DataFrame,
    group_column: str,
    title: str,
    subtitle: str,
    xlabel: str,
    highlight: list | None = None,
    highlight_above: float | None = None,
    ax=None,
):
    """Barras com a % de detratores por grupo.

    Ficam em vermelho os grupos listados em `highlight` e os que têm `highlight_above`%
    ou mais de detratores; o resto fica em cinza.
    """
    table = detractor_rate_table(df, group_column)
    highlight = set(highlight or [])
    if highlight_above is not None:
        highlight |= set(table.index[table["pct_detratores"] >= highlight_above])
    colors = [PROBLEM if label in highlight else CONTEXT for label in table.index]
    created_figure = ax is None
    if created_figure:
        fig, ax = plt.subplots(figsize=(9, 4.2))
    positions = np.arange(len(table))
    ax.bar(positions, table["pct_detratores"], color=colors, width=0.6)
    for position, value in zip(positions, table["pct_detratores"]):
        ax.text(
            position,
            value + 1.5,
            fmt_percent(value),
            ha="center",
            va="bottom",
            fontsize=9.5,
            color=INK,
        )
    ax.set_xticks(positions, group_labels_with_count(table["pedidos"]))
    ax.set_ylim(0, 110)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.yaxis.set_major_formatter(percent_axis)
    ax.set_xlabel(xlabel)
    set_titles(ax, title, subtitle)
    return ax.figure if created_figure else ax


def plot_category_mix(
    df: pd.DataFrame, group_column: str, title: str, subtitle: str, xlabel: str
):
    """Colunas 100% empilhadas: como detratores, neutros e promotores se dividem em cada grupo."""
    shares = (
        pd.crosstab(df[group_column], df["nps_category"], normalize="index").reindex(
            columns=config.NPS_CATEGORY_ORDER, fill_value=0
        )
        * 100
    )
    counts = df[group_column].value_counts().reindex(shares.index)
    fig, ax = plt.subplots(figsize=(10, 4.4))
    positions = np.arange(len(shares))
    bottom = np.zeros(len(shares))
    for category in config.NPS_CATEGORY_ORDER:
        values = shares[category].to_numpy()
        color = CATEGORY_COLORS[category]
        ax.bar(
            positions,
            values,
            bottom=bottom,
            color=color,
            width=0.62,
            edgecolor=SURFACE,
            linewidth=2,
            label=CATEGORY_LABELS[category],
        )
        for position, value, base in zip(positions, values, bottom):
            if value >= 9:
                ax.text(
                    position,
                    base + value / 2,
                    fmt_percent(value),
                    ha="center",
                    va="center",
                    fontsize=8.5,
                    color=text_color_for(color),
                )
        bottom += values
    ax.set_xticks(positions, group_labels_with_count(counts))
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(percent_axis)
    ax.set_xlabel(xlabel)
    add_top_legend(ax)
    set_titles(ax, title, subtitle, legend_row=True)
    return fig


def plot_detractor_panels(
    df: pd.DataFrame,
    panels: list[tuple[str, str]],
    title: str,
    subtitle: str,
    highlight: dict | None = None,
    highlight_above: float | None = None,
    ncols: int | None = None,
):
    """Vários gráficos de % de detratores lado a lado, com o mesmo eixo (comparação justa)."""
    highlight = highlight or {}
    ncols = ncols or len(panels)
    nrows = int(np.ceil(len(panels) / ncols))
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(4.6 * ncols, 3.9 * nrows), sharey=True, squeeze=False
    )
    for ax, (group_column, panel_title) in zip(axes.flat, panels):
        plot_detractor_rate(
            df,
            group_column,
            title="",
            subtitle=None,
            xlabel="",
            highlight=highlight.get(group_column),
            highlight_above=highlight_above,
            ax=ax,
        )
        ax.set_title(panel_title, fontsize=11, pad=8)
        ax.tick_params(axis="x", labelsize=8.5)
    for ax in list(axes.flat)[len(panels) :]:
        ax.set_visible(False)
    # Cabeçalho com medidas em polegadas: título, subtítulo e só então os painéis
    figure_height = fig.get_figheight()
    fig.text(
        0.01,
        1 - 0.10 / figure_height,
        title,
        ha="left",
        va="top",
        fontsize=13,
        fontweight="semibold",
        color=INK,
    )
    fig.text(
        0.01,
        1 - 0.40 / figure_height,
        subtitle,
        ha="left",
        va="top",
        fontsize=9.5,
        color=INK_SECONDARY,
    )
    fig.tight_layout(rect=(0, 0, 1, 1 - 0.70 / figure_height))
    return fig


def plot_heatmap(
    table: pd.DataFrame,
    title: str,
    subtitle: str,
    xlabel: str,
    ylabel: str,
    center: float = 5.0,
    value_decimals: int = 1,
    vmin: float = 0,
    vmax: float = 10,
):
    """Mapa de calor com escala divergente: vermelho = nota baixa, azul = nota alta."""
    fig, ax = plt.subplots(figsize=(8, 4.6))
    norm = TwoSlopeNorm(vmin=vmin, vcenter=center, vmax=vmax)
    image = ax.imshow(
        table.to_numpy(dtype=float), cmap=DIVERGING_CMAP, norm=norm, aspect="auto"
    )
    for (row, column), value in np.ndenumerate(table.to_numpy(dtype=float)):
        fill = DIVERGING_CMAP(norm(value))
        ax.text(
            column,
            row,
            fmt_number(value, value_decimals),
            ha="center",
            va="center",
            fontsize=11,
            color=text_color_for(mpl.colors.to_hex(fill)),
        )
    ax.set_xticks(range(table.shape[1]), table.columns)
    ax.set_yticks(range(table.shape[0]), table.index)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.04, pad=0.02)
    colorbar.outline.set_visible(False)
    colorbar.ax.tick_params(colors=MUTED, labelcolor=INK_SECONDARY)
    set_titles(ax, title, subtitle)
    return fig


# --------------------------------------------------------------------------------------
# Gráficos do modelo
# --------------------------------------------------------------------------------------
def plot_ranked_bars(
    values: pd.Series,
    title: str,
    subtitle: str,
    xlabel: str,
    highlight: list | None = None,
    decimals: int = 2,
):
    """Barras horizontais na ordem recebida; itens em `highlight` ficam em azul, o resto em cinza."""
    highlight = set(highlight or [])
    colors = [HIGHLIGHT if label in highlight else CONTEXT for label in values.index]
    fig, ax = plt.subplots(figsize=(9, 0.55 * len(values) + 1.5))
    ax.barh(list(values.index), values.to_numpy(), color=colors, height=0.55)
    for position, value in enumerate(values.to_numpy()):
        ax.text(
            value,
            position,
            f"  {fmt_number(value, decimals)}",
            va="center",
            fontsize=9.5,
            color=INK,
        )
    ax.invert_yaxis()
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, values.max() * 1.18)
    ax.xaxis.set_major_formatter(decimal_axis)
    ax.set_xlabel(xlabel)
    set_titles(ax, title, subtitle)
    return fig


def plot_model_comparison(
    cv_table: pd.DataFrame,
    metric: str,
    title: str,
    subtitle: str,
    chosen: str,
    lower_is_better: bool = True,
):
    """Métrica de validação cruzada de cada modelo, com o modelo escolhido em destaque."""
    ordered = cv_table.sort_values(metric, ascending=lower_is_better).set_index(
        "modelo"
    )[metric]
    return plot_ranked_bars(ordered, title, subtitle, xlabel=metric, highlight=[chosen])


def plot_predicted_vs_actual(y_true, y_pred, title: str, subtitle: str):
    """Dispersão nota real x nota prevista; a diagonal é o acerto perfeito."""
    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.scatter(y_true, y_pred, s=18, color=HIGHLIGHT, alpha=0.45, edgecolors="none")
    ax.plot([0, 10], [0, 10], color=INK_SECONDARY, linewidth=1)
    ax.axhline(config.DETRACTOR_LIMIT, color=AXIS, linewidth=0.8)
    ax.axvline(config.DETRACTOR_LIMIT, color=AXIS, linewidth=0.8)
    ax.set_xlim(-0.3, 10.3)
    ax.set_ylim(-0.3, 10.3)
    ax.set_xlabel("Nota real")
    ax.set_ylabel("Nota prevista")
    ax.grid(axis="x")
    set_titles(ax, title, subtitle)
    return fig


def plot_unit_impacts(
    impacts: pd.Series, title: str, subtitle: str, top: int | None = None
):
    """Quanto a nota prevista muda quando cada fator aumenta 1 unidade."""
    ordered = impacts.reindex(impacts.abs().sort_values(ascending=False).index)
    if top:
        ordered = ordered.head(top)
    ordered = ordered.iloc[::-1]
    labels = [config.FEATURE_LABELS.get(c, c) for c in ordered.index]
    colors = [
        (
            NEGATIVE_COLOR
            if value <= -0.1
            else (POSITIVE_COLOR if value >= 0.1 else CONTEXT)
        )
        for value in ordered
    ]
    fig, ax = plt.subplots(figsize=(9, 0.42 * len(ordered) + 1.5))
    ax.barh(labels, ordered.values, color=colors, height=0.6)
    for position, value in enumerate(ordered.values):
        ax.text(
            value - 0.02 if value < 0 else value + 0.02,
            position,
            fmt_number(value, 2),
            va="center",
            ha="right" if value < 0 else "left",
            fontsize=9,
            color=INK,
        )
    ax.axvline(0, color=AXIS, linewidth=1)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(min(ordered.min() * 1.25, -0.2), max(ordered.max() * 1.25, 0.3))
    ax.xaxis.set_major_formatter(decimal_axis)
    ax.set_xlabel("Variação na nota prevista (pontos) por unidade a mais")
    set_titles(ax, title, subtitle)
    return fig


def plot_risk_tiers(tier_table: pd.DataFrame, title: str, subtitle: str):
    """% de detratores reais em cada faixa de risco prevista pelo modelo."""
    fig, ax = plt.subplots(figsize=(9, 4.2))
    positions = np.arange(len(tier_table))
    colors = [RISK_TIER_COLORS[name] for name in tier_table.index]
    ax.bar(positions, tier_table["pct_detratores_reais"], color=colors, width=0.6)
    for position, (value, orders) in enumerate(
        zip(tier_table["pct_detratores_reais"], tier_table["pedidos"])
    ):
        ax.text(
            position,
            value + 1.5,
            fmt_percent(value),
            ha="center",
            va="bottom",
            fontsize=10,
            color=INK,
        )
    labels = [
        f"{name}\n({fmt_number(n, 0)} pedidos)"
        for name, n in zip(tier_table.index, tier_table["pedidos"])
    ]
    ax.set_xticks(positions, labels)
    ax.set_ylim(0, 110)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.yaxis.set_major_formatter(percent_axis)
    ax.set_xlabel("Faixa de risco prevista pelo modelo")
    set_titles(ax, title, subtitle)
    return fig
