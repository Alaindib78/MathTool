---
id: plotting-guide
title: Plotting Guide
category: Plotting
summary: Create figures, plot vectors, label axes, and organize plotting workflows.
keywords: plot, plotting, figure, graph, chart, subplot, axes, title, xlabel, ylabel
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

Related: [plot](topic:plot), [figure](topic:figure), [title](topic:title), [xlabel](topic:xlabel), [ylabel](topic:ylabel).
