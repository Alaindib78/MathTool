---
id: plotting-guide
title: Plotting Guide
category: Plotting
summary: Create figures, plot vectors, draw histograms, label axes, and organize plotting workflows.
keywords: plot, plotting, histogram, figure, graph, chart, subplot, axes, title, xlabel, ylabel
aliases: plots, graphing, plotting
related: plot, figure, title, xlabel, ylabel, grid, close
---

# Plotting Guide

Use `plot` to visualize numeric vectors. Create or select figures with `figure`, then annotate the active plot with labels and titles.

```mathtool
x = linspace(0, 2*pi, 200);
y = sin(x);
figure
plot(x, y);
title('Sine wave');
xlabel('x');
ylabel('sin(x)');
grid(true);
```

## Histograms

Use `histogram` for numeric or logical data. Matrix and array inputs are flattened into one combined distribution.

```mathtool
x = randn(1000, 1);
histogram(x, 25);
title("Normal samples");
```

You can provide explicit bin edges, precomputed counts, or MATLAB-style name-value options.

```mathtool
edges = -4:0.5:4;
histogram(x, edges, "Normalization", "pdf");

histogram("BinEdges", [0 1 2 3], "BinCounts", [10 20 5]);
```

Supported histogram options include `NumBins`, `BinWidth`, `BinEdges`, `BinLimits`, `BinMethod`, `BinCounts`, `Normalization`, `DisplayStyle`, `Orientation`, `FaceColor`, `EdgeColor`, `FaceAlpha`, `EdgeAlpha`, `LineStyle`, `LineWidth`, and `DisplayName`.

Current limitations: categorical, datetime/duration, table/timetable data, axes-target syntax, `histcounts`, `morebins`, `fewerbins`, and editable histogram object properties are not implemented yet. Automatic binning is NumPy-based, so exact bin edges can differ from MATLAB.

## Multiple figures

```mathtool
figure(1)
plot(x, sin(x));

figure(2)
plot(x, cos(x));
```

## Clean up

```mathtool
close
close all
```

Related: [plot](topic:plot), [histogram](topic:histogram), [figure](topic:figure), [title](topic:title), [xlabel](topic:xlabel), [ylabel](topic:ylabel).
