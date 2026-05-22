import numpy as np
import pytest

from core.engine import MathToolSession
from core.runtime.context import RuntimeContext


def test_engineering_library_files_validate_and_are_documented():
    context = RuntimeContext()

    context.validate_function_paths()

    assert context.help_database.get("vec_norm").h1Line.startswith(
        "VEC_NORM"
    )
    assert context.help_database.get("ohms_voltage").h1Line.startswith(
        "OHMS_VOLTAGE"
    )
    assert context.help_database.get(
        "cantilever_tip_deflection"
    ).h1Line.startswith("CANTILEVER_TIP_DEFLECTION")


def test_core_math_helpers_execute_from_library():
    session = MathToolSession()

    session.execute(
        """
v = vec_norm([3 4]);
u = unit_vector([3 4]);
ma = moving_average([1 2 3 4], 2);
fd = finite_diff_central([0 1 4 9], 1);
fit = linear_fit_params([1 2 3], [3 5 7]);
rmsValue = signal_rms([3 4]);
ci = ci95_mean([1 2 3 4]);
qr = quadratic_roots_real(1, -3, 2);
rootInfo = bisection_poly([1 0 -4], 0, 3, 0.0001, 100);
"""
    )

    variables = session.context.variables

    assert variables["v"] == pytest.approx(5)
    np.testing.assert_allclose(
        variables["u"],
        np.array([0.6, 0.8]),
    )
    np.testing.assert_allclose(
        variables["ma"],
        np.array([1, 1.5, 2.5, 3.5]),
    )
    np.testing.assert_allclose(
        variables["fd"],
        np.array([1, 2, 4, 5]),
    )
    np.testing.assert_allclose(
        variables["fit"],
        np.array([2, 1]),
    )
    assert variables["rmsValue"] == pytest.approx(3.5355339)
    np.testing.assert_allclose(
        variables["qr"],
        np.array([1, 2]),
    )
    assert variables["rootInfo"][0] == pytest.approx(2, abs=1e-3)


def test_engineering_formula_helpers_execute_from_library():
    session = MathToolSession()

    session.execute(
        """
temp = celsius_to_fahrenheit(100);
dist = distance2d([0 0], [3 4]);
theta = angle_between_vectors([1 0], [0 1]);
area = polygon_area([0 0; 2 0; 2 2; 0 2]);
cent = polygon_centroid([0 0; 2 0; 2 2; 0 2]);
vout = voltage_divider(10, 1000, 1000);
db = db20(10);
stress = axial_stress(100, 2);
polar = solid_circular_polar_j(2);
g = standard_gravity();
pf = prime_factors(60);
"""
    )

    variables = session.context.variables

    assert variables["temp"] == pytest.approx(212)
    assert variables["dist"] == pytest.approx(5)
    assert variables["theta"] == pytest.approx(np.pi / 2)
    assert variables["area"] == pytest.approx(4)
    np.testing.assert_allclose(
        variables["cent"],
        np.array([1, 1]),
    )
    assert variables["vout"] == pytest.approx(5)
    assert variables["db"] == pytest.approx(20)
    assert variables["stress"] == pytest.approx(50)
    assert variables["polar"] == pytest.approx(np.pi / 2)
    assert variables["g"] == pytest.approx(9.80665)
    np.testing.assert_array_equal(
        variables["pf"],
        np.array([2, 2, 3, 5]),
    )


def test_control_ode_and_data_helpers_execute_from_library():
    session = MathToolSession()

    session.execute(
        """
ode = euler_linear_ode(-1, 1, [1 1 1 1], 0, 0.1);
rk = rk4_linear_ode(-1, 1, [1 1 1 1], 0, 0.1);
step = first_order_step_response(2, 1, [0 1]);
pid = pid_response(1, 0.5, 0.1, [0 1 1], 0.1);
scaled = minmax_scale([2 4 6], 0, 1);
idx = nearest_index([10 20 30], 24);
sat = saturate_vector([-2 0 3], -1, 1);
detrended = linear_detrend([1 2 3], [3 5 7]);
"""
    )

    variables = session.context.variables

    np.testing.assert_allclose(
        variables["ode"],
        np.array([0, 0.1, 0.19, 0.271]),
    )
    assert variables["rk"][1] == pytest.approx(0.0951625, abs=1e-6)
    np.testing.assert_allclose(
        variables["step"],
        np.array([0, 2 * (1 - np.exp(-1))]),
    )
    np.testing.assert_allclose(
        variables["pid"],
        np.array([0, 2.05, 1.1]),
    )
    np.testing.assert_allclose(
        variables["scaled"],
        np.array([0, 0.5, 1]),
    )
    assert variables["idx"] == 2
    np.testing.assert_allclose(
        variables["sat"],
        np.array([-1, 0, 1]),
    )
    np.testing.assert_allclose(
        variables["detrended"],
        np.array([0, 0, 0]),
        atol=1e-12,
    )
