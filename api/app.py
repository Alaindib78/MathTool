from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.schemas import (
    CommandRequest,
    ExecuteRequest,
    PathRequest,
    SearchPathsRequest,
)
from core.documentation.formatter import format_function_help
from core.documentation.html import (
    function_help_to_html,
    help_home_to_html,
)
from api.session_store import SessionStore
from core.serialization import (
    serialize_execution_result,
    serialize_workspace,
)


WEB_ROOT = Path(__file__).resolve().parent.parent / "web"


def create_app(session_store=None):
    store = session_store or SessionStore()

    app = FastAPI(
        title="MathTool API",
        version="0.1.0",
    )

    app.state.session_store = store

    if WEB_ROOT.exists():
        app.mount(
            "/assets",
            StaticFiles(directory=str(WEB_ROOT)),
            name="assets",
        )

        @app.get("/", include_in_schema=False)
        def web_hmi():
            return FileResponse(
                WEB_ROOT / "index.html"
            )

    @app.get("/health")
    def health():
        return {
            "status": "ok",
        }

    @app.post("/sessions")
    def create_session():
        stored = store.create()

        return session_metadata(stored)

    @app.get("/sessions")
    def list_sessions():
        return {
            "sessions": [
                session_metadata(stored)
                for stored in store.list()
            ],
        }

    @app.delete("/sessions/{session_id}")
    def delete_session(session_id: str):
        if not store.delete(session_id):
            raise not_found(session_id)

        return {
            "deleted": True,
        }

    @app.post("/sessions/{session_id}/execute")
    def execute(
        session_id: str,
        request: ExecuteRequest,
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                result = stored.session.execute(
                    request.source,
                    source_path=request.source_path,
                    allow_commands=request.allow_commands,
                    allow_script_commands=(
                        request.allow_script_commands
                    ),
                )
            except Exception as error:
                raise bad_request(error) from error

            return serialize_execution_result(
                result,
                context=stored.session.context,
                include_workspace=request.include_workspace,
                include_plots=request.include_plots,
            )

    @app.post("/sessions/{session_id}/command")
    def command(
        session_id: str,
        request: CommandRequest,
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                result = stored.session.execute(
                    request.source,
                    allow_commands=True,
                    allow_script_commands=True,
                )
            except Exception as error:
                raise bad_request(error) from error

            return serialize_execution_result(
                result,
                context=stored.session.context,
                include_workspace=request.include_workspace,
                include_plots=request.include_plots,
            )

    @app.get("/sessions/{session_id}/workspace")
    def workspace(session_id: str):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            return serialize_workspace(
                stored.session.context
            )

    @app.post("/sessions/{session_id}/workspace/clear")
    def clear_workspace(session_id: str):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            stored.session.context.clear()

            return serialize_workspace(
                stored.session.context
            )

    @app.get("/sessions/{session_id}/cwd")
    def get_cwd(session_id: str):
        stored = get_stored_session(
            store,
            session_id,
        )

        return {
            "path": (
                stored
                .session
                .context
                .current_working_directory
            ),
        }

    @app.put("/sessions/{session_id}/cwd")
    def set_cwd(
        session_id: str,
        request: PathRequest,
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                stored.session.context.set_current_working_directory(
                    request.path
                )
            except Exception as error:
                raise bad_request(error) from error

            return {
                "path": (
                    stored
                    .session
                    .context
                    .current_working_directory
                ),
            }

    @app.get("/sessions/{session_id}/paths")
    def get_search_paths(session_id: str):
        stored = get_stored_session(
            store,
            session_id,
        )

        return {
            "paths": list(
                stored.session.context.search_paths
            ),
        }

    @app.put("/sessions/{session_id}/paths")
    def set_search_paths(
        session_id: str,
        request: SearchPathsRequest,
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                stored.session.context.set_search_paths(
                    request.paths
                )
            except Exception as error:
                raise bad_request(error) from error

            return {
                "paths": list(
                    stored.session.context.search_paths
                ),
            }

    @app.post("/sessions/{session_id}/paths")
    def add_search_path(
        session_id: str,
        request: PathRequest,
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                stored.session.context.add_search_path(
                    request.path
                )
            except Exception as error:
                raise bad_request(error) from error

            return {
                "paths": list(
                    stored.session.context.search_paths
                ),
            }

    @app.delete("/sessions/{session_id}/paths")
    def remove_search_path(
        session_id: str,
        path: str = Query(...),
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                stored.session.context.remove_search_path(
                    path
                )
            except Exception as error:
                raise bad_request(error) from error

            return {
                "paths": list(
                    stored.session.context.search_paths
                ),
            }

    @app.get("/sessions/{session_id}/help")
    def help_overview(
        session_id: str,
        topic: str | None = None,
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        try:
            text = stored.session.context.help_database.format_help(
                topic
            )
        except Exception as error:
            raise bad_request(error) from error

        return {
            "topic": topic,
            "text": text,
        }

    @app.get("/sessions/{session_id}/help/home")
    def help_home(session_id: str):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            help_database = (
                stored.session.context.help_database
            )

            try:
                help_database.refresh()
                return {
                    "title": "Help Home",
                    "html": help_home_to_html(
                        help_database
                    ),
                    "popular": [
                        serialize_help_topic(
                            entry,
                            include_text=False,
                        )
                        for entry in help_database.popular_entries()
                    ],
                    "categories": [
                        {
                            "category": category,
                            "count": len(entries),
                        }
                        for category, entries in (
                            help_database
                            .entries_by_category()
                            .items()
                        )
                    ],
                }
            except Exception as error:
                raise bad_request(error) from error

    @app.get("/sessions/{session_id}/help/topics")
    def help_topics(
        session_id: str,
        include_text: bool = False,
        include_html: bool = False,
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                entries = (
                    stored
                    .session
                    .context
                    .help_database
                    .all_entries()
                )
            except Exception as error:
                raise bad_request(error) from error

            return {
                "count": len(entries),
                "topics": [
                    serialize_help_topic(
                        entry,
                        include_text=include_text,
                        include_html=include_html,
                    )
                    for entry in entries
                ],
            }

    @app.get("/sessions/{session_id}/help/search")
    def help_search(
        session_id: str,
        q: str = Query(""),
        limit: int = Query(50, ge=1, le=250),
        include_text: bool = False,
        include_html: bool = False,
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                results = (
                    stored
                    .session
                    .context
                    .help_database
                    .search(q)
                )[:limit]
            except Exception as error:
                raise bad_request(error) from error

            return {
                "query": q,
                "count": len(results),
                "results": [
                    serialize_help_topic(
                        entry,
                        include_text=include_text,
                        include_html=include_html,
                    )
                    for entry in results
                ],
            }

    @app.get("/sessions/{session_id}/help/index")
    def help_index(session_id: str):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                letters = (
                    stored
                    .session
                    .context
                    .help_database
                    .entries_by_letter()
                )
            except Exception as error:
                raise bad_request(error) from error

            return {
                "letters": [
                    {
                        "letter": letter,
                        "topics": [
                            serialize_help_topic(
                                entry,
                                include_text=False,
                            )
                            for entry in entries
                        ],
                    }
                    for letter, entries in letters.items()
                ],
            }

    @app.get("/sessions/{session_id}/help/categories")
    def help_categories(session_id: str):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                categories = (
                    stored
                    .session
                    .context
                    .help_database
                    .entries_by_category()
                )
            except Exception as error:
                raise bad_request(error) from error

            return {
                "categories": [
                    {
                        "category": category,
                        "count": len(entries),
                        "topics": [
                            serialize_help_topic(
                                entry,
                                include_text=False,
                            )
                            for entry in entries
                        ],
                    }
                    for category, entries in categories.items()
                ],
            }

    @app.get("/sessions/{session_id}/help/examples")
    def help_examples(session_id: str):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                entries = [
                    entry
                    for entry in (
                        stored
                        .session
                        .context
                        .help_database
                        .all_entries()
                    )
                    if entry.examples
                ]
            except Exception as error:
                raise bad_request(error) from error

            return {
                "count": len(entries),
                "examples": [
                    {
                        "topic": serialize_help_topic(
                            entry,
                            include_text=False,
                        ),
                        "items": list(entry.examples),
                    }
                    for entry in entries
                ],
            }

    @app.get("/sessions/{session_id}/help/topic/{topic}")
    def structured_help_topic(
        session_id: str,
        topic: str,
        include_text: bool = True,
        include_html: bool = True,
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        with stored.lock:
            try:
                entry = (
                    stored
                    .session
                    .context
                    .help_database
                    .get(topic)
                )
            except Exception as error:
                raise bad_request(error) from error

            if entry is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Help topic not found: {topic}",
                )

            return serialize_help_topic(
                entry,
                include_text=include_text,
                include_html=include_html,
            )

    @app.get("/sessions/{session_id}/help/{topic}")
    def help_topic(
        session_id: str,
        topic: str,
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        try:
            text = stored.session.context.help_database.format_help(
                topic
            )
        except Exception as error:
            raise bad_request(error) from error

        return {
            "topic": topic,
            "text": text,
        }

    @app.get("/sessions/{session_id}/lookfor")
    def lookfor(
        session_id: str,
        q: str = Query(...),
    ):
        stored = get_stored_session(
            store,
            session_id,
        )

        return {
            "query": q,
            "text": (
                stored
                .session
                .context
                .help_database
                .format_lookfor(q)
            ),
        }

    return app


def get_stored_session(store, session_id):
    try:
        return store.get(session_id)
    except KeyError as error:
        raise not_found(session_id) from error


def session_metadata(stored):
    return {
        "id": stored.id,
        "created_at": stored.created_at.isoformat(),
        "updated_at": stored.updated_at.isoformat(),
        "cwd": (
            stored
            .session
            .context
            .current_working_directory
        ),
    }


def not_found(session_id):
    return HTTPException(
        status_code=404,
        detail=f"Session not found: {session_id}",
    )


def bad_request(error):
    return HTTPException(
        status_code=400,
        detail=str(error),
    )


def serialize_help_topic(
    entry,
    *,
    include_text=False,
    include_html=False,
):
    payload = {
        "id": entry.functionName,
        "name": entry.functionName,
        "title": entry.display_name,
        "category": entry.category,
        "kind": entry.kind,
        "summary": entry.h1Line,
        "signature": entry.signature,
        "keywords": list(entry.keywords),
        "aliases": list(entry.aliases),
        "related": list(entry.seeAlso),
        "examples": list(entry.examples),
        "source_path": entry.sourcePath,
        "is_builtin": entry.isBuiltin,
    }

    if include_text:
        payload["text"] = format_function_help(entry)

    if include_html:
        payload["html"] = function_help_to_html(entry)

    return payload


app = create_app()
