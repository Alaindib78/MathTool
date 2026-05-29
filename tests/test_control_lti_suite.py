import numpy as np

from core.engine import MathToolSession
from core.plotting.recording import RecordingPlotEngine
from core.runtime.context import RuntimeContext
from core.serialization import serialize_workspace


def test_lti_transfer_function_constructor_display_and_properties():
    session = MathToolSession()

    session.execute(
        """
sys = tf(1.5, [1 14 40.02]);
p = pole(sys);
z = zero(sys);
props = get(sys);
kind = class(sys);
"""
    )

    sys = session.context.variables["sys"]
    props = session.context.variables["props"]

    assert sys.model_type == "tf"
    assert session.context.variables["kind"] == "tf"
    np.testing.assert_allclose(props["Numerator"], np.array([1.5]))
    np.testing.assert_allclose(props["Denominator"], np.array([1.0, 14.0, 40.02]))
    np.testing.assert_allclose(
        np.sort(session.context.variables["p"]),
        np.sort(np.roots([1.0, 14.0, 40.02])),
    )
    assert session.context.variables["z"].size == 0
    assert "Transfer function" in str(sys)


def test_lti_state_space_conversion_and_dot_access():
    session = MathToolSession()

    session.execute(
        """
R = 2.0;
L = 0.5;
Km = 0.015;
Kb = 0.015;
Kf = 0.2;
J = 0.02;
A = [-R/L -Kb/L; Km/J -Kf/J];
B = [1/L; 0];
C = [0 1];
D = [0];
sys_dc = ss(A, B, C, D);
sys_tf = tf(sys_dc);
sys_zpk = zpk(sys_dc);
Aprop = sys_dc.A;
Ts = sys_dc.Ts;
"""
    )

    np.testing.assert_allclose(
        session.context.variables["Aprop"],
        np.array([[-4.0, -0.03], [0.75, -10.0]]),
    )
    assert session.context.variables["Ts"] == 0.0
    assert session.context.variables["sys_tf"].model_type == "tf"
    assert session.context.variables["sys_zpk"].model_type == "zpk"


def test_lti_transfer_variable_arithmetic():
    session = MathToolSession()

    session.execute(
        """
s = tf('s');
G = 1.5 / (s^2 + 14*s + 40.02);
"""
    )

    G = session.context.variables["G"]
    np.testing.assert_allclose(G.numerator, np.array([1.5]))
    np.testing.assert_allclose(G.denominator, np.array([1.0, 14.0, 40.02]))


def test_lti_step_impulse_and_bode_record_embedded_plots():
    session = MathToolSession(plot_engine=RecordingPlotEngine())

    session.execute(
        """
sys = tf(1.5, [1 14 40.02]);
step(sys);
impulse(sys);
bode(sys);
"""
    )

    titles = [
        plot["layout"]["title"]["text"]
        for plot in session.context.plot_engine.serialize_plots()
    ]

    assert titles == [
        "Step Response",
        "Impulse Response",
        "Bode Diagram - Magnitude",
        "Bode Diagram - Phase",
    ]


def test_lti_workspace_serialization_uses_short_preview():
    context = RuntimeContext()
    sys = context.functions.get("zpk")(context, np.array([]), np.array([-1.0]), 2.0)
    context.set_variable("sys", sys)

    serialized = serialize_workspace(context)

    assert serialized["variables"][0]["preview"] == "zpk model"
    assert serialized["variables"][0]["value"]["type"] == "lti"
