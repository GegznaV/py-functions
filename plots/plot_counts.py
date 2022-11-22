import pandas as pd

def counts_to_percentages(x, name="percent"):
    """Express counts as percentages.

    The sum of count values is treated as 100%.

    Args:
        x (int, float): Counts data as pandas.Series.
        name (str, optional): The name for output pandas.Series with percentage
             values. Defaults to "percent".

    Returns:
        str: pandas.Series object with `x` values expressed as percentages
             and rounded to 1 decimal place, e.g., "0.2%".
             Values equal to 0 are formatted as "0%", values between
             0 and 0.1 are formatted as "<0.1%", values between 99.9 and 100
             are formatted as ">99.9%".

    Examples:
    >>> import pandas as pd
    >>> counts_to_percentages(pd.Series([1, 0, 1000, 2000, 1000, 5000, 1000]))
    >>> counts_to_percentages(pd.Series([1, 0, 10000]))
    
    Author: Vilmantas Gėgžna
    """
    x_sum = x.sum()
    return (
        pd.Series(
            [
                "0%"
                if i == 0
                else "<0.1%"
                if i < 0.1
                else ">99.9%"
                if 99.9 < i < 100
                else f"{i:.1f}%"
                for i in (x / x_sum * 100)
            ],
            index=x.index,
        )
        .replace("0.0%", "<0.1%")
        .rename(name)
    )

def calc_counts_and_percentages(
    group, data, sort=True, weight=None, n_label="n", perc_label="percent"
):
    """Create frequency table that contains counts and percentages.

    Args:
        group (str): Variable that defines the groups. Column name from `data`.
        data (pandas.DataFrame): data frame.
        sort (bool or "index", optional): Way to sort values:
             - True - sort by count descending.
             - "index" - sort by index ascending.        
             Defaults to True.
        weight (str, optional): Frequency weights. Column name from `data`.
                Defaults to None: no weights are used.
        n_label (str, optional): Name for output column with counts.
        perc_label (str, optional): Name for output column with percentage.

    Return: pandas.DataFrame with 3 columns:
            - column with unique values of `x`,
            - column `n_label` (defaults to "n") with counts as int, and
            - column `perc_label` (defaults to "percent") with percentage
              values formatted as str.
              
    Author: Vilmantas Gėgžna
    """

    vsort = (sort == True)

    if weight is None:
        counts = data[group].value_counts(sort=vsort)
        if sort == "index":
            counts = counts.sort_index()
    else:
        counts = data.groupby(group)[weight].sum()

    percent = counts_to_percentages(counts)

    return (
        pd.concat([counts.rename(n_label), percent.rename(perc_label)], axis=1)
        .rename_axis(group)
        .reset_index()
    )
    
# Plot counts ---------------------------------------------------------------
def plot_counts_with_labels(
    counts,
    title="",
    x=None,
    y="n",
    xlabel=None,
    ylabel="Count",
    label="percent",
    label_rotation=0,
    title_fontsize=13,
    legend=False,
    ec="black",
    y_lim_max=None,
    ax=None,
    **kwargs,
):
    """Plot count data as barplots with labels.

    Args:
        counts (pandas.DataFrame): Data frame with counts data.
        title (str, optional): Figure title. Defaults to "".
        x (str, optional): Column name from `counts` to plot on x axis.
                Defaults to None: first column.
        y (str, optional): Column name from `counts` to plot on y axis.
                Defaults to "n".
        xlabel (str, optional): X axis label. 
              Defaults to value of `x` with capitalized first letter.
        ylabel (str, optional): Y axis label. Defaults to "Count".
        label (str, optional): Column name from `counts` for value labels.
                Defaults to "percent".
        label_rotation (int, optional): Angle of label rotation. Defaults to 0.
        legend (bool, optional): Should legend be shown?. Defaults to False.
        ec (str, optional): Edge color. Defaults to "black".
        y_lim_max (float, optional): Upper limit for Y axis.
                Defaults to None: do not change.
        ax (matplotlib.axes.Axes, optional): Axes object. Defaults to None.
        **kwargs: further arguments to pandas.DataFrame.plot.bar()

    Returns:
        matplotlib.axes.Axes: Axes object of the generate plot.
    
    Author: Vilmantas Gėgžna
    """
    if x is None:
        x = counts.columns[0]
        
    if xlabel is None:
        xlabel = x.capitalize()

    if y_lim_max is None:
        y_lim_max = counts[y].max() * 1.15

    ax = counts.plot.bar(x=x, y=y, legend=legend, ax=ax, ec=ec, **kwargs)
    ax.set_title(title, fontsize=title_fontsize)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax_add_value_labels_ab(ax, labels=counts[label], rotation=label_rotation)
    ax.set_ylim(0, y_lim_max)

    return ax


def ax_add_value_labels_ab(
    ax, labels=None, spacing=2, size=9, weight="bold", **kwargs
):
    """Add value labels above/below each bar in a bar chart.

    Arguments:
        ax (matplotlib.Axes): Plot (axes) to annotate.
        label (str or similar): Values to be used as labels.
        spacing (int): Number of points between bar and label.
        size (int): font size.
        weight (str): font weight.
        **kwargs: further arguments to axis.annotate.

    Source:
        This function is based on https://stackoverflow.com/a/48372659/4783029
    """

    # For each bar: Place a label
    for rect, label in zip(ax.patches, labels):
        # Get X and Y placement of label from rect.
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2

        space = spacing

        # Vertical alignment for positive values
        va = "bottom"

        # If the value of a bar is negative: Place label below the bar
        if y_value < 0:
            # Invert space to place label below
            space *= -1
            # Vertical alignment
            va = "top"

        # Use Y value as label and format number with one decimal place
        if labels is None:
            label = "{:.1f}".format(y_value)

        # Create annotation
        ax.annotate(
            label,
            (x_value, y_value),
            xytext=(0, space),
            textcoords="offset points",
            ha="center",
            va=va,
            fontsize=size,
            fontweight=weight,
            **kwargs,
        )
        
def plot_crosstab_as_barplot(
    data: pd.DataFrame,
    x: str = None,
    y: str = None,
    title: str = None,
    xlabel=None,
    ylabel=None,
    normalize=None,
    rot=0,
    **kwargs

):
    """Plot a Cross-Tabulation as Barplot

    Args:
        data (pandas.DataFrame): Either cross-tabulation or data frame with
            categorical (or discrete) data.
        x (str, optional): Column name in 'data'.
        y (str, optional): Column name in 'data'.
        title (str, optional): Title of the plot.
        xlabel: see details in pandas.DataFrame.plot.bar()
                Defaults to None.
        ylabel: see details in pandas.DataFrame.plot.bar()
                Defaults to None:
                   - "Percentage" for normalized data.
                   - "Count" for non-normalized data.
                   - "" if it is not clear (when input is a cross-tab)
        rot: see details in pandas.DataFrame.plot.bar()
              Defaults to 0
        normalize (str, 0, 1 or None, optional): way of data normalization:
           None - not normalized, show counts
           "all" - data expressed as percentages of total.
           "row", "index", "x", 0 - column heights at the same x value
                sum up to 100 %.
           "column", "columns", "color", 1 - columns heights of the same color
                sum up to 100 %.
           
        **kwargs: other args to pandas.DataFrame.plot.bar()

    Returns:
        Axes object.
        
    Author: Vilmantas Gėgžna

    """

    if (x is None) & (y is None):
        cross_t = data
    else:
        # Create cross-tabulation
        cross_t = pd.crosstab(data[x], data[y])

    # Row percentage
    if normalize == "all":
        cross_p = cross_t.div(cross_t.sum().sum()) * 100
    elif normalize in ["row", "index", "x", 0]:
        cross_p = cross_t.div(cross_t.sum(axis=1), axis=0) * 100
    elif normalize in ["column", "columns", "color", 1]:
        cross_p = cross_t.div(cross_t.sum(axis=0), axis=1) * 100
    else:
        cross_p = cross_t

    if (ylabel is None):
        if normalize is not None:
            ylabel = "Percentage"
        elif (x is not None) & (y is not None):
            ylabel = "Count"
            
    # Visualize
    ax = cross_p.plot.bar(
        ec="black",
        title=title,
        rot=rot,
        xlabel=xlabel,
        ylabel=ylabel,
        **kwargs
)
    return ax
