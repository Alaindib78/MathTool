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


def test_api_exposes_structured_help_browser_data():
    client = create_client()
    session_id = create_session(client)

    search = client.get(
        f"/sessions/{session_id}/help/search",
        params={
            "q": "plo",
        },
    )
    assert search.status_code == 200
    result_ids = [
        item["id"]
        for item in search.json()["results"][:6]
    ]
    assert "plot" in result_ids
    assert "plotting-guide" in result_ids

    topic = client.get(
        f"/sessions/{session_id}/help/topic/plotting-guide",
        params={
            "include_html": True,
        },
    )
    assert topic.status_code == 200
    payload = topic.json()
    assert payload["title"] == "Plotting Guide"
    assert payload["category"] == "Plotting"
    assert "Plotting Guide" in payload["html"]

    index = client.get(
        f"/sessions/{session_id}/help/index"
    )
    assert index.status_code == 200
    assert any(
        group["letter"] == "P"
        for group in index.json()["letters"]
    )

    categories = client.get(
        f"/sessions/{session_id}/help/categories"
    )
    assert categories.status_code == 200
    assert any(
        group["category"] == "Plotting"
        for group in categories.json()["categories"]
    )

    examples = client.get(
        f"/sessions/{session_id}/help/examples"
    )
    assert examples.status_code == 200
    assert examples.json()["count"] > 0


def test_api_command_response_includes_doc_help_topic():
    client = create_client()
    session_id = create_session(client)

    response = client.post(
        f"/sessions/{session_id}/command",
        json={
            "source": "doc plot",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "doc"
    assert payload["help_topic"] == "plot"
    assert "Plot x-y data" in payload["value"]["value"]


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


def test_api_serves_web_hmi_assets():
    client = create_client()

    index = client.get("/")
    help_page = client.get("/help")
    script = client.get("/assets/app.js")
    help_script = client.get("/assets/help.js")
    styles = client.get("/assets/styles.css")

    assert index.status_code == 200
    assert "MathTool" in index.text
    assert "helpButton" in index.text
    assert help_page.status_code == 200
    assert "helpSearch" in help_page.text
    assert script.status_code == 200
    assert "createSession" in script.text
    assert "openHelpPage" in script.text
    assert help_script.status_code == 200
    assert "runHelpSearch" in help_script.text
    assert styles.status_code == 200
    assert ".workbench" in styles.text
    assert ".doc-workbench" in styles.text
