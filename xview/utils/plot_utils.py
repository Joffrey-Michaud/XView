"""Helper functions to draw monitoring lines (min/max/mean/median) on plots."""

import numpy as np
import matplotlib.pyplot as plt


def plot_max_line(ax, x, y, color, ls="--", alpha=0.5, x_max_range=None):
    """Annotate the maximum value with a horizontal line and label."""
    # x_max_range est le maximum du x-axis qui apparait sur le plot. il peut etre plus bas que le x le plus grand à plotter
    y_max = np.max(y)
    idx_max = np.argmax(y)
    x_max = x[idx_max]

    ax.hlines(
        y=y_max,
        xmin=x_max,
        xmax=x[-1],
        color=color,
        linestyle=ls,
        alpha=alpha,
    )

    # texte au dessus de la ligne
    dy = (np.max(y) - np.min(y)) or 1.0
    offset = 0.02 * dy

    # position à l'extrémit droite de la ligne
    if x_max_range is None:
        x_max_range = x[-1]
    dx = x_max_range - x[0]
    x_text = x_max_range - 0.01 * dx

    ax.text(
        x=x_text,
        y=y_max + offset,
        s=f"Max: {y_max:.3f}",
        color=color,
        fontsize=10,
        ha="right",
        va="bottom",
        alpha=alpha
    )


def plot_min_line(ax, x, y, color, ls="--", alpha=0.5, x_max_range=None):
    """Annotate the minimum value with a horizontal line and label."""
    y_min = np.min(y)
    idx_min = np.argmin(y)
    x_min = x[idx_min]

    ax.hlines(
        y=y_min,
        xmin=x_min,
        xmax=x[-1],
        color=color,
        linestyle=ls,
        alpha=alpha,
    )

    # texte au dessous de la ligne
    dy = (np.max(y) - np.min(y)) or 1.0
    offset = 0.04 * dy

    # position à l'extrémit droite de la ligne
    if x_max_range is None:
        x_max_range = x[-1]
    dx = x_max_range - x[0]
    x_text = x_max_range - 0.01 * dx

    ax.text(
        x=x_text,
        y=y_min - offset,
        s=f"Min: {y_min:.3f}",
        color=color,
        fontsize=10,
        ha="right",
        va="bottom",
        alpha=alpha
    )


def plot_med_line(ax, x, y, color, ls="--", alpha=0.5, x_max_range=None):
    """Annotate the median value with a horizontal line and label."""
    y_med = np.median(y)

    ax.hlines(
        y=y_med,
        xmin=x[0],
        xmax=x[-1],
        color=color,
        linestyle=ls,
        alpha=alpha,
    )

    # texte au dessous de la ligne
    dy = (np.max(y) - np.min(y)) or 1.0
    offset = 0.04 * dy

    # position à l'extrémit droite de la ligne
    if x_max_range is None:
        x_max_range = x[-1]
    dx = x_max_range - x[0]
    x_text = x_max_range - 0.01 * dx

    ax.text(
        x=x_text,
        y=y_med - offset,
        s=f"Med: {y_med:.3f}",
        color=color,
        fontsize=10,
        ha="right",
        va="bottom",
        alpha=alpha
    )


def plot_mean_line(ax, x, y, color, ls="--", alpha=0.5, x_max_range=None):
    """Annotate the mean value with a horizontal line and label."""
    y_mean = np.mean(y)

    ax.hlines(
        y=y_mean,
        xmin=x[0],
        xmax=x[-1],
        color=color,
        linestyle=ls,
        alpha=alpha,
    )

    # texte au dessous de la ligne
    dy = (np.max(y) - np.min(y)) or 1.0
    offset = 0.04 * dy

    # position à l'extrémit droite de la ligne
    if x_max_range is None:
        x_max_range = x[-1]
    dx = x_max_range - x[0]
    x_text = x_max_range - 0.01 * dx

    ax.text(
        x=x_text,
        y=y_mean - offset,
        s=f"Mean: {y_mean:.3f}",
        color=color,
        fontsize=10,
        ha="right",
        va="bottom",
        alpha=alpha
    )


def plot_monitoring_lines(ax, x, y, color, ls="--", monitoring_flags="", alpha=0.5, x_max_range=None):
    """Draw selected monitoring lines based on a comma-separated flag string."""
    monitoring_modes = monitoring_flags.split(",")
    if "max" in monitoring_modes:
        plot_max_line(ax, x, y, color, ls=ls, alpha=alpha, x_max_range=x_max_range)
    if "min" in monitoring_modes:
        plot_min_line(ax, x, y, color, ls=ls, alpha=alpha, x_max_range=x_max_range)
    if "mean" in monitoring_modes:
        plot_mean_line(ax, x, y, color, ls=ls, alpha=alpha, x_max_range=x_max_range)
    if "med" in monitoring_modes:
        plot_med_line(ax, x, y, color, ls=ls, alpha=alpha, x_max_range=x_max_range)
