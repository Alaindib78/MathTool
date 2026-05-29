from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np

from core.errors.errors import RuntimeError as MathToolRuntimeError
from core.runtime.symbolic import NameValueOption, is_symbolic


MAX_BINS = 65536

BIN_SPEC_OPTIONS = {
    "NumBins",
    "BinWidth",
    "BinEdges",
    "BinMethod",
}

NORMALIZATIONS = {
    "count",
    "probability",
    "percentage",
    "countdensity",
    "cumcount",
    "pdf",
    "cdf",
}

DISPLAY_STYLES = {
    "bar",
    "stairs",
}

ORIENTATIONS = {
    "vertical",
    "horizontal",
}

LINE_STYLES = {
    "-",
    "--",
    ":",
    "-.",
    "none",
}

SHORT_COLORS = {
    "r": "r",
    "g": "g",
    "b": "b",
    "c": "c",
    "m": "m",
    "y": "y",
    "k": "k",
    "w": "w",
}

COLOR_NAMES = {
    "red": "red",
    "green": "green",
    "blue": "blue",
    "cyan": "cyan",
    "magenta": "magenta",
    "yellow": "yellow",
    "black": "black",
    "white": "white",
}

OPTION_NAMES = {
    "numbins": "NumBins",
    "binwidth": "BinWidth",
    "binedges": "BinEdges",
    "binlimits": "BinLimits",
    "binmethod": "BinMethod",
    "bincounts": "BinCounts",
    "normalization": "Normalization",
    "displaystyle": "DisplayStyle",
    "orientation": "Orientation",
    "facecolor": "FaceColor",
    "edgecolor": "EdgeColor",
    "facealpha": "FaceAlpha",
    "edgealpha": "EdgeAlpha",
    "linestyle": "LineStyle",
    "linewidth": "LineWidth",
    "displayname": "DisplayName",
}


@dataclass
class HistogramOptions:
    NumBins: int | None = None
    BinWidth: float | None = None
    BinEdges: np.ndarray | None = None
    BinLimits: tuple[float, float] | None = None
    BinMethod: str = "auto"
    BinCounts: np.ndarray | None = None
    Normalization: str = "count"
    DisplayStyle: str = "bar"
    Orientation: str = "vertical"
    FaceColor: object = "auto"
    EdgeColor: object = "auto"
    FaceAlpha: float = 0.6
    EdgeAlpha: float = 1.0
    LineStyle: str = "-"
    LineWidth: float = 0.5
    DisplayName: str | None = None
    _bin_spec: tuple[str, object] | None = None


@dataclass
class HistogramData:
    Data: np.ndarray | None
    Values: np.ndarray
    BinEdges: np.ndarray
    RawCounts: np.ndarray
    TotalCount: int
    Options: HistogramOptions
    Handle: "HistogramHandle" = field(init=False)

    def __post_init__(self):
        self.Handle = HistogramHandle(self)


class HistogramHandle:
    def __init__(self, histogram_data):
        self.Data = histogram_data.Data
        self.Values = histogram_data.Values
        self.BinEdges = histogram_data.BinEdges
        self.RawCounts = histogram_data.RawCounts
        self.TotalCount = histogram_data.TotalCount
        self.NumBins = int(len(histogram_data.Values))
        widths = np.diff(histogram_data.BinEdges)
        self.BinWidth = (
            float(widths[0])
            if widths.size and np.allclose(widths, widths[0])
            else widths
        )
        self.BinLimits = (
            float(histogram_data.BinEdges[0]),
            float(histogram_data.BinEdges[-1]),
        )

        options = histogram_data.Options
        for name in [
            "Normalization",
            "DisplayStyle",
            "Orientation",
            "FaceColor",
            "EdgeColor",
            "FaceAlpha",
            "EdgeAlpha",
            "LineStyle",
            "LineWidth",
            "DisplayName",
        ]:
            setattr(self, name, getattr(options, name))

        self.matplotlib_artists = []

    @property
    def BinCounts(self):
        return self.RawCounts

    def properties(self):
        return {
            "Data": self.Data,
            "Values": self.Values,
            "BinEdges": self.BinEdges,
            "BinCounts": self.BinCounts,
            "NumBins": self.NumBins,
            "BinWidth": self.BinWidth,
            "BinLimits": self.BinLimits,
            "Normalization": self.Normalization,
            "DisplayStyle": self.DisplayStyle,
            "Orientation": self.Orientation,
            "FaceColor": self.FaceColor,
            "EdgeColor": self.EdgeColor,
            "FaceAlpha": self.FaceAlpha,
            "EdgeAlpha": self.EdgeAlpha,
            "LineStyle": self.LineStyle,
            "LineWidth": self.LineWidth,
            "DisplayName": self.DisplayName,
        }

    def get_property(self, name):
        if not hasattr(self, name):
            raise MathToolRuntimeError(
                f"Reference to non-existent property '{name}'"
            )

        return getattr(self, name)

    def __str__(self):
        values = np.array2string(self.Values, threshold=8, separator=" ")
        edges = np.array2string(self.BinEdges, threshold=8, separator=" ")
        return (
            "Histogram with properties:\n"
            f"    Values: {values}\n"
            f"    NumBins: {self.NumBins}\n"
            f"    BinEdges: {edges}\n"
            f"    BinWidth: {self.BinWidth}\n"
            f"    Normalization: {self.Normalization}"
        )

    __repr__ = __str__


def compute_histogram_from_arguments(arguments):
    data, options = parse_histogram_arguments(arguments)
    return compute_histogram(data, options)


def parse_histogram_arguments(arguments):
    if not arguments:
        raise MathToolRuntimeError(
            "histogram: expected data or BinEdges/BinCounts"
        )

    options = HistogramOptions()
    data = None
    index = 0

    if starts_name_value(arguments[0]):
        index = parse_option_sequence(arguments, 0, options)
    else:
        data = arguments[0]
        index = 1

        if index < len(arguments) and not starts_name_value(arguments[index]):
            positional_bin = arguments[index]
            if isinstance(positional_bin, str):
                raise MathToolRuntimeError(
                    f"histogram: unknown option '{positional_bin}'"
                )
            if is_scalar_numeric(positional_bin):
                set_option(options, "NumBins", positional_bin)
            else:
                set_option(options, "BinEdges", positional_bin)
            index += 1

        index = parse_option_sequence(arguments, index, options)

    if index != len(arguments):
        raise MathToolRuntimeError(
            "histogram: invalid argument list"
        )

    return data, options


def parse_option_sequence(arguments, index, options):
    while index < len(arguments):
        argument = arguments[index]

        if isinstance(argument, NameValueOption):
            set_option(options, argument.name, argument.value)
            index += 1
            continue

        if not isinstance(argument, str):
            raise MathToolRuntimeError(
                "histogram: option names must be strings"
            )

        if index + 1 >= len(arguments):
            raise MathToolRuntimeError(
                f"histogram: missing value after option '{argument}'"
            )

        set_option(options, argument, arguments[index + 1])
        index += 2

    return index


def starts_name_value(argument):
    if isinstance(argument, NameValueOption):
        return True

    if not isinstance(argument, str):
        return False

    return argument.lower() in OPTION_NAMES


def set_option(options, raw_name, value):
    canonical = OPTION_NAMES.get(str(raw_name).lower())

    if canonical is None:
        raise MathToolRuntimeError(
            f"histogram: unknown option '{raw_name}'"
        )

    normalized = normalize_option(canonical, value)
    setattr(options, canonical, normalized)

    if canonical in BIN_SPEC_OPTIONS:
        options._bin_spec = (canonical, normalized)


def normalize_option(name, value):
    if name == "NumBins":
        return positive_integer(value, "NumBins")

    if name == "BinWidth":
        return positive_scalar(value, "BinWidth")

    if name == "BinEdges":
        return validate_bin_edges(value)

    if name == "BinLimits":
        return validate_bin_limits(value)

    if name == "BinMethod":
        method = normalize_text(value, "BinMethod")
        if method not in {"auto", "sturges", "sqrt", "fd", "scott", "integers"}:
            raise MathToolRuntimeError(
                f"histogram: invalid BinMethod '{value}'"
            )
        return method

    if name == "BinCounts":
        counts = numeric_vector(value, "BinCounts")
        if np.any(counts < 0):
            raise MathToolRuntimeError(
                "histogram: BinCounts must be nonnegative"
            )
        return counts.astype(float)

    if name == "Normalization":
        normalization = normalize_text(value, "Normalization")
        if normalization not in NORMALIZATIONS:
            raise MathToolRuntimeError(
                f"histogram: invalid Normalization value '{value}'"
            )
        return normalization

    if name == "DisplayStyle":
        display_style = normalize_text(value, "DisplayStyle")
        if display_style not in DISPLAY_STYLES:
            raise MathToolRuntimeError(
                f"histogram: invalid DisplayStyle value '{value}'"
            )
        return display_style

    if name == "Orientation":
        orientation = normalize_text(value, "Orientation")
        if orientation not in ORIENTATIONS:
            raise MathToolRuntimeError(
                f"histogram: invalid Orientation value '{value}'"
            )
        return orientation

    if name in {"FaceColor", "EdgeColor"}:
        return normalize_color(value)

    if name in {"FaceAlpha", "EdgeAlpha"}:
        return alpha_value(value, name)

    if name == "LineStyle":
        line_style = str(scalar_value(value)).lower()
        if line_style not in LINE_STYLES:
            raise MathToolRuntimeError(
                f"histogram: invalid LineStyle value '{value}'"
            )
        return line_style

    if name == "LineWidth":
        return positive_scalar(value, "LineWidth")

    if name == "DisplayName":
        return str(scalar_value(value))

    return value


def compute_histogram(data, options):
    validate_histogram_options(options)

    if options.BinCounts is not None:
        if options.BinEdges is None:
            raise MathToolRuntimeError(
                "histogram: BinEdges must be specified with BinCounts"
            )

        if len(options.BinCounts) != len(options.BinEdges) - 1:
            raise MathToolRuntimeError(
                "histogram: BinCounts length must equal length(BinEdges)-1"
            )

        raw_counts = options.BinCounts.astype(float)
        total_count = int(np.sum(raw_counts))
        values = normalize_counts(
            raw_counts,
            options.BinEdges,
            options.Normalization,
            total_count,
        )
        return HistogramData(
            None,
            values,
            options.BinEdges,
            raw_counts,
            total_count,
            options,
        )

    if data is None:
        raise MathToolRuntimeError(
            "histogram: expected data or BinEdges/BinCounts"
        )

    flat_data = validate_histogram_data(data)
    total_count = int(flat_data.size)
    edges = compute_bin_edges(flat_data, options)
    binned_data = data_for_edges(flat_data, edges, options)
    raw_counts, _ = np.histogram(binned_data, bins=edges)
    raw_counts = raw_counts.astype(float)
    values = normalize_counts(
        raw_counts,
        edges,
        options.Normalization,
        total_count,
    )

    return HistogramData(
        flat_data,
        values,
        edges,
        raw_counts,
        total_count,
        options,
    )


def compute_bin_edges(data, options):
    spec_name, spec_value = options._bin_spec or ("BinMethod", options.BinMethod)

    if spec_name == "BinEdges":
        return spec_value

    finite_data = finite_data_for_limits(data, options.BinLimits)
    low, high = data_limits(finite_data, options.BinLimits)

    if spec_name == "NumBins":
        return np.linspace(low, high, int(spec_value) + 1)

    if spec_name == "BinWidth":
        return edges_from_width(low, high, float(spec_value))

    method = str(spec_value).lower()

    if method == "integers":
        return integer_edges(finite_data, options.BinLimits)

    if finite_data.size == 0:
        return np.array([0.0, 1.0])

    if finite_data.size == 1 or low == high:
        return np.array([low - 0.5, high + 0.5])

    if method in {"auto", "fd", "scott"}:
        try:
            edges = np.histogram_bin_edges(finite_data, bins=method)
        except ValueError:
            edges = np.array([low, high])
        return cap_edges(edges)

    if method == "sturges":
        count = math.ceil(math.log2(max(finite_data.size, 1)) + 1)
        return np.linspace(low, high, count + 1)

    if method == "sqrt":
        count = math.ceil(math.sqrt(finite_data.size))
        return np.linspace(low, high, count + 1)

    raise MathToolRuntimeError(
        f"histogram: invalid BinMethod '{spec_value}'"
    )


def normalize_counts(counts, edges, normalization, total_count):
    values = np.asarray(counts, dtype=float)
    widths = np.diff(np.asarray(edges, dtype=float))

    if normalization == "count":
        return values

    if normalization == "cumcount":
        return np.cumsum(values)

    if total_count <= 0:
        return np.zeros_like(values, dtype=float)

    if normalization == "probability":
        return values / total_count

    if normalization == "percentage":
        return values * 100.0 / total_count

    if normalization == "cdf":
        return np.cumsum(values) / total_count

    if normalization == "countdensity":
        return divide_by_width(values, widths)

    if normalization == "pdf":
        return divide_by_width(values / total_count, widths)

    raise MathToolRuntimeError(
        f"histogram: invalid Normalization value '{normalization}'"
    )


def validate_histogram_data(data):
    if is_symbolic(data) or isinstance(data, str):
        raise MathToolRuntimeError(
            "histogram: X data must be numeric or logical"
        )

    try:
        array = np.asarray(data)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            "histogram: X data must be numeric or logical"
        ) from error

    if not (
        np.issubdtype(array.dtype, np.number)
        or np.issubdtype(array.dtype, np.bool_)
    ):
        raise MathToolRuntimeError(
            "histogram: X data must be numeric or logical"
        )

    if np.iscomplexobj(array):
        raise MathToolRuntimeError(
            "histogram: X data must be real numeric or logical"
        )

    return np.asarray(array, dtype=float).reshape(-1)


def validate_histogram_options(options):
    if options.BinCounts is not None and options.BinEdges is None:
        raise MathToolRuntimeError(
            "histogram: BinEdges must be specified with BinCounts"
        )


def data_for_edges(data, edges, options):
    mask = ~np.isnan(data)

    if not np.isneginf(edges[0]):
        mask &= data >= edges[0]

    if not np.isposinf(edges[-1]):
        mask &= data <= edges[-1]

    if not np.isneginf(edges[0]) and not np.isposinf(edges[-1]):
        mask &= np.isfinite(data)

    if options.BinLimits is not None:
        low, high = options.BinLimits
        mask &= data >= low
        mask &= data <= high

    return data[mask]


def finite_data_for_limits(data, limits):
    mask = np.isfinite(data)

    if limits is not None:
        low, high = limits
        mask &= data >= low
        mask &= data <= high

    return data[mask]


def data_limits(finite_data, limits):
    if limits is not None:
        return limits

    if finite_data.size == 0:
        return 0.0, 1.0

    low = float(np.min(finite_data))
    high = float(np.max(finite_data))

    if low == high:
        return low - 0.5, high + 0.5

    return low, high


def edges_from_width(low, high, width):
    if high <= low:
        high = low + width

    count = int(math.ceil((high - low) / width))
    count = max(1, min(count, MAX_BINS))
    edges = low + np.arange(count + 1, dtype=float) * width

    if edges[-1] < high:
        edges = np.append(edges, high)

    return edges


def integer_edges(data, limits):
    if limits is not None:
        low, high = limits
    elif data.size == 0:
        low, high = -0.5, 0.5
    else:
        low = math.floor(float(np.min(data))) - 0.5
        high = math.ceil(float(np.max(data))) + 0.5

    count = max(1, int(math.ceil(high - low)))
    if count > MAX_BINS:
        return np.linspace(low, high, MAX_BINS + 1)

    return np.arange(low, low + count + 1, 1.0)


def cap_edges(edges):
    edges = np.asarray(edges, dtype=float)

    if edges.size <= MAX_BINS + 1:
        return edges

    return np.linspace(float(edges[0]), float(edges[-1]), MAX_BINS + 1)


def divide_by_width(values, widths):
    return np.divide(
        values,
        widths,
        out=np.zeros_like(values, dtype=float),
        where=np.isfinite(widths) & (widths > 0),
    )


def validate_bin_edges(value):
    edges = numeric_vector(value, "BinEdges")

    if edges.size < 2:
        raise MathToolRuntimeError(
            "histogram: BinEdges must contain at least two values"
        )

    if np.any(np.isnan(edges)) or not np.all(np.diff(edges) > 0):
        raise MathToolRuntimeError(
            "histogram: BinEdges must be a strictly increasing numeric vector"
        )

    return edges.astype(float)


def validate_bin_limits(value):
    limits = numeric_vector(value, "BinLimits")

    if limits.size != 2:
        raise MathToolRuntimeError(
            "histogram: BinLimits must contain two values"
        )

    low, high = (float(limits[0]), float(limits[1]))

    if not math.isfinite(low) or not math.isfinite(high) or high <= low:
        raise MathToolRuntimeError(
            "histogram: BinLimits must be a finite increasing two-element vector"
        )

    return (low, high)


def numeric_vector(value, name):
    if is_symbolic(value) or isinstance(value, str):
        raise MathToolRuntimeError(
            f"histogram: {name} must be a numeric vector"
        )

    try:
        array = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            f"histogram: {name} must be a numeric vector"
        ) from error

    if np.iscomplexobj(np.asarray(value)):
        raise MathToolRuntimeError(
            f"histogram: {name} must be real numeric"
        )

    return array


def positive_integer(value, name):
    value = scalar_value(value)

    if isinstance(value, (bool, np.bool_)):
        raise MathToolRuntimeError(
            f"histogram: {name} must be a positive integer"
        )

    numeric = float(value)

    if not numeric.is_integer() or numeric < 1:
        raise MathToolRuntimeError(
            f"histogram: {name} must be a positive integer"
        )

    integer = int(numeric)

    if integer > MAX_BINS:
        raise MathToolRuntimeError(
            f"histogram: {name} must be no greater than {MAX_BINS}"
        )

    return integer


def positive_scalar(value, name):
    value = scalar_value(value)
    numeric = float(value)

    if not math.isfinite(numeric) or numeric <= 0:
        raise MathToolRuntimeError(
            f"histogram: {name} must be a positive scalar"
        )

    return numeric


def alpha_value(value, name):
    numeric = float(scalar_value(value))

    if not math.isfinite(numeric) or numeric < 0 or numeric > 1:
        raise MathToolRuntimeError(
            f"histogram: {name} must be between 0 and 1"
        )

    return numeric


def scalar_value(value):
    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, np.ndarray):
        if value.size != 1:
            raise MathToolRuntimeError(
                "histogram: expected scalar value"
            )
        return value.reshape(-1)[0].item()

    return value


def normalize_text(value, name):
    text = str(scalar_value(value)).strip().lower()

    if not text:
        raise MathToolRuntimeError(
            f"histogram: {name} must be a nonempty string"
        )

    return text


def is_scalar_numeric(value):
    if isinstance(value, (str, NameValueOption)):
        return False

    if isinstance(value, np.ndarray):
        return value.size == 1 and np.issubdtype(value.dtype, np.number)

    return isinstance(value, (int, float, np.integer, np.floating))


def normalize_color(value):
    value = scalar_value(value) if isinstance(value, np.ndarray) and value.size == 1 else value

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, str):
        lowered = value.lower()

        if lowered in {"auto", "none"}:
            return lowered

        if lowered in SHORT_COLORS:
            return SHORT_COLORS[lowered]

        if lowered in COLOR_NAMES:
            return COLOR_NAMES[lowered]

        raise MathToolRuntimeError(
            f"histogram: invalid color value '{value}'"
        )

    try:
        array = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError) as error:
        raise MathToolRuntimeError(
            "histogram: RGB color must have exactly three elements"
        ) from error

    if array.size != 3:
        raise MathToolRuntimeError(
            "histogram: RGB color must have exactly three elements"
        )

    rgb = tuple(float(component) for component in array)

    if any(component < 0 or component > 1 for component in rgb):
        raise MathToolRuntimeError(
            "histogram: RGB color components must be between 0 and 1"
        )

    return rgb
