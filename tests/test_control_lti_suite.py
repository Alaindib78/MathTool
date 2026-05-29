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

    assert serialized["variables"][0]["preview"] == "zpk model, continuous-time"
    assert serialized["variables"][0]["value"]["type"] == "lti"


def test_extended_lti_analysis_interconnection_and_synthesis():
    session = MathToolSession()

    session.execute(
        """
s = tf("s");
G = 1 / (s^2 + 2*s + 1);
closed_loop = feedback(G, 1);
simple = minreal((s + 1) / (s + 1));
stable = isstable(G);
gain = dcgain(G);
info = stepinfo(G);
controller = pid(1, 0.5, 0.1);
"""
    )

    assert session.context.variables["stable"] is True
    assert session.context.variables["gain"] == 1.0
    np.testing.assert_allclose(
        session.context.variables["closed_loop"].denominator,
        np.array([1.0, 2.0, 2.0]),
    )
    np.testing.assert_allclose(
        session.context.variables["simple"].denominator,
        np.array([1.0]),
    )
    assert "RiseTime" in session.context.variables["info"]
    np.testing.assert_allclose(
        session.context.variables["controller"].numerator,
        np.array([0.1, 1.0, 0.5]),
    )


def test_extended_lti_state_space_tools_and_lqr():
    session = MathToolSession()

    session.execute(
        """
A = [0 1; -2 -3];
B = [0; 1];
C = [1 0];
D = [0];
sys = ss(A, B, C, D);
Co = ctrb(sys);
Ob = obsv(sys);
X = lyap([-1], [1]);
result = lqr(A, B, [1 0; 0 1], [1]);
sysd = c2d(sys, 0.1);
"""
    )

    np.testing.assert_allclose(
        session.context.variables["Co"],
        np.array([[0.0, 1.0], [1.0, -3.0]]),
    )
    np.testing.assert_allclose(
        session.context.variables["Ob"],
        np.array([[1.0, 0.0], [0.0, 1.0]]),
    )
    np.testing.assert_allclose(session.context.variables["X"], np.array([[0.5]]))
    assert set(session.context.variables["result"].keys()) == {"K", "S", "P"}
    assert session.context.variables["sysd"].is_discrete is True


def test_extended_lti_frequency_plots_margin_and_root_locus():
    session = MathToolSession(plot_engine=RecordingPlotEngine())

    session.execute(
        """
s = tf("s");
G = 10 / (s * (s + 1) * (s + 5));
m = margin(G);
r = rlocus(G, 0:1:10);
bodemag(G);
nyquist(G);
nichols(G);
sigma(G);
"""
    )

    assert "GainMargin" in session.context.variables["m"]
    assert "roots" in session.context.variables["r"]
    assert len(session.context.plot_engine.serialize_plots()) >= 6


def test_frd_and_transfer_variable_z():
    session = MathToolSession()

    session.execute(
        """
H = frd([1 0.5], [1 10]);
z = tf("z", 0.01);
Gd = 1 / (z - 0.8);
dt = isdt(Gd);
ct = isct(Gd);
"""
    )

    assert session.context.variables["H"].model_type == "frd"
    assert session.context.variables["dt"] is True
    assert session.context.variables["ct"] is False
