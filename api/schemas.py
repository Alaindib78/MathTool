from pydantic import BaseModel, Field


class ExecuteRequest(BaseModel):
    source: str
    source_path: str | None = None
    allow_commands: bool = False
    allow_script_commands: bool = True
    include_workspace: bool = True
    include_plots: bool = True


class CommandRequest(BaseModel):
    source: str
    include_workspace: bool = True
    include_plots: bool = True


class PathRequest(BaseModel):
    path: str


class SearchPathsRequest(BaseModel):
    paths: list[str] = Field(default_factory=list)
