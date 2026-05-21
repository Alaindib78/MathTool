import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from api.app import create_app


def create_client():
    return TestClient(create_app())


def create_session(client):
    response = client.post("/sessions")

    assert response.status_code == 200

    return response.json()["id"]


def test_api_executes_code_and_returns_serialized_workspace():
    client = create_client()
    session_id = create_session(client)

    response = client.post(
        f"/sessions/{session_id}/execute",
        json={
            "source": "A = [1 2; 3 4];",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["value"]["type"] == "array"
    assert payload["value"]["shape"] == [2, 2]
    assert (
        payload["workspace"]["variables"][0]["name"]
        == "A"
    )


def test_api_supports_interactive_commands():
    client = create_client()
    session_id = create_session(client)

    client.post(
        f"/sessions/{session_id}/execute",
        json={
            "source": "alpha = 1;",
        },
    )

    response = client.post(
        f"/sessions/{session_id}/command",
        json={
            "source": "who",
        },
    )

    assert response.status_code == 200
    assert response.json()["value"]["items"][0]["value"] == "alpha"


def test_api_returns_404_for_missing_session():
    client = create_client()

    response = client.get("/sessions/missing/workspace")

    assert response.status_code == 404


def test_api_sets_cwd_and_search_paths(tmp_path):
    client = create_client()
    session_id = create_session(client)
    library = tmp_path / "library"
    library.mkdir()

    response = client.put(
        f"/sessions/{session_id}/cwd",
        json={
            "path": str(tmp_path),
        },
    )
    assert response.status_code == 200
    assert response.json()["path"] == str(
        tmp_path.resolve()
    )

    response = client.post(
        f"/sessions/{session_id}/paths",
        json={
            "path": str(library),
        },
    )
    assert response.status_code == 200
    assert response.json()["paths"] == [
        str(library.resolve())
    ]


def test_api_records_plot_specs_in_execution_response():
    client = create_client()
    session_id = create_session(client)

    response = client.post(
        f"/sessions/{session_id}/execute",
        json={
            "source": """
x = [1 2 3];
y = [4 5 6];
plot(x, y);
title("Line");
xlabel("x");
ylabel("y");
grid(true);
""",
        },
    )

    assert response.status_code == 200

    plot = response.json()["plots"][0]

    assert plot["type"] == "plotly"
    assert plot["data"][0]["x"] == [1, 2, 3]
    assert plot["data"][0]["y"] == [4, 5, 6]
    assert plot["layout"]["title"]["text"] == "Line"
    assert plot["layout"]["xaxis"]["title"]["text"] == "x"
    assert plot["layout"]["yaxis"]["title"]["text"] == "y"
    assert plot["layout"]["xaxis"]["showgrid"] is True
