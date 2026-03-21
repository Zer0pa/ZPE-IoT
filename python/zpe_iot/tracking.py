"""Benchmark telemetry adapters with explicit local fallback semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Any, Mapping


DEFAULT_WORKSPACE = "zer0pa"
DEFAULT_CLASSIC_PROJECT = "zpe-iot-performance"
DEFAULT_OPIK_PROJECT = "zpe-iot-performance"
DEFAULT_OPIK_URL = "https://www.comet.com/opik/api"
DEFAULT_THREAD_ID = "zpe-iot-benchmark-phase9"


@dataclass(frozen=True)
class ProjectCheck:
    target: str
    status: str
    resolved_name: str | None = None
    resolved_id: str | None = None
    resolved_slug: str | None = None
    url: str | None = None
    handshake_error: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)


def _project_identity(payload: Any) -> dict[str, str]:
    candidates: dict[str, str] = {}
    if isinstance(payload, dict):
        for out_key, keys in (
            ("name", ("name", "projectName", "project_name")),
            ("id", ("id", "projectId", "project_id")),
            ("slug", ("slug", "projectSlug", "project_slug")),
            ("url", ("url", "projectUrl", "project_url")),
        ):
            for key in keys:
                value = payload.get(key)
                if value not in (None, ""):
                    candidates[out_key] = str(value)
                    break
        return candidates

    for out_key, attr_name in (("name", "name"), ("id", "id"), ("slug", "slug"), ("url", "url")):
        value = getattr(payload, attr_name, None)
        if value not in (None, ""):
            candidates[out_key] = str(value)
    return candidates


def _opik_api_key() -> str:
    return (os.environ.get("OPIK_API_KEY") or "").strip()


def verify_classic_comet_project(*, workspace: str, expected_name: str) -> ProjectCheck:
    if not os.environ.get("COMET_API_KEY"):
        return ProjectCheck(target="classic_comet", status="HOLD", handshake_error="COMET_API_KEY missing")
    try:
        from comet_ml.api import API  # type: ignore
    except Exception as exc:
        return ProjectCheck(target="classic_comet", status="HOLD", handshake_error=f"comet_ml unavailable: {exc}")

    try:
        api = API(api_key=os.environ.get("COMET_API_KEY") or None)
        project = api.get_project(workspace, expected_name)
        if project is None:
            api.create_project(workspace, expected_name)
            project = api.get_project(workspace, expected_name)
            if project is None:
                return ProjectCheck(
                    target="classic_comet",
                    status="HOLD",
                    handshake_error=f"project create returned no project for {expected_name}",
                )
            identity = _project_identity(project)
            return ProjectCheck(
                target="classic_comet",
                status="CREATED",
                resolved_name=identity.get("name", expected_name),
                resolved_id=identity.get("id"),
                resolved_slug=identity.get("slug"),
                url=identity.get("url"),
                detail=identity,
            )
        identity = _project_identity(project)
        return ProjectCheck(
            target="classic_comet",
            status="EXISTS",
            resolved_name=identity.get("name", expected_name),
            resolved_id=identity.get("id"),
            resolved_slug=identity.get("slug"),
            url=identity.get("url"),
            detail=identity,
        )
    except Exception as exc:
        return ProjectCheck(target="classic_comet", status="HOLD", handshake_error=f"{type(exc).__name__}: {exc}")


def verify_opik_project(*, workspace: str, expected_name: str, host: str) -> ProjectCheck:
    if not _opik_api_key():
        return ProjectCheck(target="opik", status="HOLD", handshake_error="OPIK_API_KEY missing")
    try:
        from opik import Opik  # type: ignore
        from opik.rest_api.core.api_error import ApiError  # type: ignore
    except Exception as exc:
        return ProjectCheck(target="opik", status="HOLD", handshake_error=f"opik unavailable: {exc}")

    client = None
    try:
        client = Opik(
            project_name=expected_name,
            workspace=workspace,
            host=host,
            api_key=_opik_api_key() or None,
            _use_batching=True,
            _show_misconfiguration_message=False,
        )
        client.auth_check()
        try:
            project = client.rest_client.projects.retrieve_project(name=expected_name)
            url = client.get_project_url(expected_name)
            return ProjectCheck(
                target="opik",
                status="EXISTS",
                resolved_name=getattr(project, "name", expected_name),
                resolved_id=getattr(project, "id", None),
                url=url,
            )
        except ApiError as exc:
            if getattr(exc, "status_code", None) != 404:
                raise
            client.rest_client.projects.create_project(name=expected_name)
            project = client.rest_client.projects.retrieve_project(name=expected_name)
            url = client.get_project_url(expected_name)
            return ProjectCheck(
                target="opik",
                status="CREATED",
                resolved_name=getattr(project, "name", expected_name),
                resolved_id=getattr(project, "id", None),
                url=url,
            )
    except Exception as exc:
        return ProjectCheck(target="opik", status="HOLD", handshake_error=f"{type(exc).__name__}: {exc}")
    finally:
        if client is not None:
            try:
                client.end()
            except Exception:
                pass


def _flatten_items(payload: Any, prefix: str = "") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            items.extend(_flatten_items(value, next_prefix))
        return items
    if isinstance(payload, list):
        for idx, value in enumerate(payload):
            next_prefix = f"{prefix}[{idx}]"
            items.extend(_flatten_items(value, next_prefix))
        return items
    items.append((prefix, payload))
    return items


def flatten_numeric_mapping(payload: Mapping[str, Any], prefix: str = "") -> dict[str, float]:
    metrics: dict[str, float] = {}
    for key, value in _flatten_items(payload, prefix):
        if isinstance(value, bool):
            metrics[key] = 1.0 if value else 0.0
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            metrics[key] = float(value)
    return metrics


def flatten_string_mapping(payload: Mapping[str, Any], prefix: str = "") -> dict[str, Any]:
    others: dict[str, Any] = {}
    for key, value in _flatten_items(payload, prefix):
        if isinstance(value, (dict, list, tuple)):
            continue
        if isinstance(value, (int, float, bool)) or value is None:
            continue
        others[key] = value
    return others


class ClassicCometAdapter:
    def __init__(self, experiment: Any | None, notes: list[str]) -> None:
        self.experiment = experiment
        self.notes = notes

    @property
    def enabled(self) -> bool:
        return self.experiment is not None

    @classmethod
    def create(
        cls,
        *,
        project_check: ProjectCheck,
        workspace: str,
        run_name: str,
        disabled: bool = False,
    ) -> "ClassicCometAdapter":
        notes: list[str] = []
        if disabled:
            notes.append("classic Comet adapter disabled by missing credential")
            return cls(None, notes)
        if project_check.status not in {"EXISTS", "CREATED"}:
            notes.append(f"classic Comet adapter inactive: {project_check.handshake_error or 'project check did not pass'}")
            return cls(None, notes)

        try:
            from comet_ml import Experiment  # type: ignore
        except Exception as exc:
            notes.append(f"classic Comet adapter unavailable: {exc}")
            return cls(None, notes)

        try:
            experiment = Experiment(
                api_key=os.environ.get("COMET_API_KEY") or None,
                workspace=workspace,
                project_name=project_check.resolved_name or DEFAULT_CLASSIC_PROJECT,
                log_code=False,
                log_graph=False,
                auto_param_logging=False,
                auto_metric_logging=False,
                parse_args=False,
                auto_output_logging=None,
                log_env_details=False,
                log_git_metadata=False,
                log_git_patch=False,
                disabled=False,
                log_env_gpu=False,
                log_env_host=False,
                display_summary=False,
                log_env_cpu=False,
                log_env_network=False,
                log_env_disk=False,
                auto_log_co2=False,
            )
            experiment.set_name(run_name)
            notes.append("classic Comet metrics logging enabled")
            return cls(experiment, notes)
        except Exception as exc:
            notes.append(f"classic Comet adapter failed to initialize: {type(exc).__name__}: {exc}")
            return cls(None, notes)

    def log_parameters(self, parameters: dict[str, Any]) -> None:
        if self.experiment is None:
            return
        for key, value in parameters.items():
            self.experiment.log_parameter(key, value)

    def log_metrics(self, metrics: dict[str, int | float]) -> None:
        if self.experiment is None:
            return
        if metrics:
            self.experiment.log_metrics(metrics)

    def log_others(self, payload: dict[str, Any]) -> None:
        if self.experiment is None or not payload:
            return
        try:
            self.experiment.log_others(payload)
        except Exception as exc:
            self.notes.append(f"classic Comet others log skipped: {type(exc).__name__}: {exc}")

    def log_asset(self, path: str) -> None:
        if self.experiment is None:
            return
        try:
            self.experiment.log_asset(path)
        except Exception as exc:
            self.notes.append(f"classic Comet asset log skipped for {path}: {type(exc).__name__}: {exc}")

    def log_text(self, text: str) -> None:
        if self.experiment is None:
            return
        try:
            self.experiment.log_text(text)
        except Exception as exc:
            self.notes.append(f"classic Comet text log skipped: {type(exc).__name__}: {exc}")

    def finish(self) -> dict[str, str]:
        experiment_key = ""
        experiment_url = ""
        if self.experiment is None:
            return {"experiment_key": experiment_key, "experiment_url": experiment_url}
        try:
            experiment_key = str(self.experiment.get_key() or "")
        except Exception:
            pass
        try:
            experiment_url = str(getattr(self.experiment, "url", "") or "")
        except Exception:
            pass
        try:
            self.experiment.end()
        except Exception:
            pass
        return {"experiment_key": experiment_key, "experiment_url": experiment_url}


class OpikAdapter:
    def __init__(self, client: Any | None, notes: list[str]) -> None:
        self.client = client
        self.notes = notes

    @property
    def enabled(self) -> bool:
        return self.client is not None

    @classmethod
    def create(
        cls,
        *,
        project_check: ProjectCheck,
        workspace: str,
        disabled: bool = False,
    ) -> "OpikAdapter":
        notes: list[str] = []
        if disabled:
            notes.append("Opik adapter disabled by missing credential")
            return cls(None, notes)
        if project_check.status not in {"EXISTS", "CREATED"}:
            notes.append(f"Opik adapter inactive: {project_check.handshake_error or 'project check did not pass'}")
            return cls(None, notes)

        try:
            from opik import Opik  # type: ignore
        except Exception as exc:
            notes.append(f"Opik adapter unavailable: {exc}")
            return cls(None, notes)

        try:
            client = Opik(
                project_name=project_check.resolved_name or DEFAULT_OPIK_PROJECT,
                workspace=workspace,
                host=os.environ.get("OPIK_URL_OVERRIDE", DEFAULT_OPIK_URL),
                api_key=_opik_api_key() or None,
                _use_batching=True,
                _show_misconfiguration_message=False,
            )
            notes.append("Opik trace logging enabled")
            return cls(client, notes)
        except Exception as exc:
            notes.append(f"Opik adapter failed to initialize: {type(exc).__name__}: {exc}")
            return cls(None, notes)

    def start_trace(self, *, name: str, metadata: dict[str, Any], input_payload: dict[str, Any]) -> Any | None:
        if self.client is None:
            return None
        try:
            return self.client.trace(
                name=name,
                project_name=self.client.project_name,
                metadata=metadata,
                input=input_payload,
                thread_id=DEFAULT_THREAD_ID,
            )
        except Exception as exc:
            self.notes.append(f"Opik trace start skipped: {type(exc).__name__}: {exc}")
            return None

    def log_metadata(self, trace: Any | None, metadata: dict[str, Any]) -> None:
        if trace is None:
            return
        try:
            update = getattr(trace, "log_metadata", None)
            if callable(update):
                update(metadata)
        except Exception as exc:
            self.notes.append(f"Opik metadata log skipped: {type(exc).__name__}: {exc}")

    def finish_trace(self, trace: Any | None, *, output_payload: dict[str, Any]) -> tuple[str, str]:
        trace_id = ""
        trace_url = ""
        if trace is None:
            return trace_id, trace_url
        try:
            trace_id = str(getattr(trace, "id", "") or getattr(trace, "trace_id", "") or "")
        except Exception:
            pass
        try:
            end = getattr(trace, "end", None)
            if callable(end):
                end(output=output_payload)
        except Exception as exc:
            self.notes.append(f"Opik trace end skipped: {type(exc).__name__}: {exc}")
        trace_url = self.get_trace_url(trace_id)
        return trace_id, trace_url

    def get_trace_url(self, trace_id: str) -> str:
        if self.client is None or not trace_id:
            return ""
        try:
            from opik.api_objects import opik_client  # type: ignore

            return str(
                opik_client.url_helpers.get_project_url_by_trace_id(  # type: ignore[attr-defined]
                    trace_id=trace_id,
                    url_override=self.client._config.url_override,
                )
            )
        except Exception as exc:
            self.notes.append(f"Opik trace URL resolution unavailable: {type(exc).__name__}: {exc}")
            return ""

    def finish(self) -> None:
        if self.client is None:
            return
        try:
            self.client.flush()
        except Exception:
            pass
        try:
            self.client.end()
        except Exception:
            pass


@dataclass
class TrackingBundle:
    workspace: str
    classic_project: str
    opik_project: str
    opik_host: str
    classic_check: ProjectCheck
    opik_check: ProjectCheck
    comet: ClassicCometAdapter
    opik: OpikAdapter
    opik_trace: Any | None

    def log_payload(self, prefix: str, payload: Mapping[str, Any]) -> None:
        self.comet.log_metrics(flatten_numeric_mapping(payload, prefix))
        self.comet.log_others(flatten_string_mapping(payload, prefix))
        self.opik.log_metadata(self.opik_trace, {prefix: dict(payload)})

    def finish(self, *, artifact_paths: list[str], output_payload: dict[str, Any]) -> dict[str, Any]:
        for path in artifact_paths:
            self.comet.log_asset(path)
        self.comet.log_text("\n".join(self.comet.notes + self.opik.notes))
        comet_identity = self.comet.finish()
        opik_trace_id, opik_trace_url = self.opik.finish_trace(self.opik_trace, output_payload=output_payload)
        self.opik.finish()
        return {
            "workspace": self.workspace,
            "classic_project": self.classic_project,
            "classic_status": self.classic_check.status,
            "classic_project_url": self.classic_check.url or "",
            "classic_experiment_key": comet_identity["experiment_key"],
            "classic_experiment_url": comet_identity["experiment_url"],
            "opik_project": self.opik_project,
            "opik_status": self.opik_check.status,
            "opik_project_url": self.opik_check.url or "",
            "opik_trace_id": opik_trace_id,
            "opik_trace_url": opik_trace_url,
            "opik_host": self.opik_host,
            "notes": self.comet.notes + self.opik.notes,
        }


def create_tracking_bundle(*, run_name: str, input_payload: dict[str, Any], metadata: dict[str, Any]) -> TrackingBundle:
    workspace = os.environ.get("COMET_WORKSPACE") or os.environ.get("OPIK_WORKSPACE") or DEFAULT_WORKSPACE
    classic_project = os.environ.get("COMET_PROJECT_NAME") or DEFAULT_CLASSIC_PROJECT
    opik_project = os.environ.get("OPIK_PROJECT_NAME") or DEFAULT_OPIK_PROJECT
    opik_host = os.environ.get("OPIK_URL_OVERRIDE") or DEFAULT_OPIK_URL

    classic_check = verify_classic_comet_project(workspace=workspace, expected_name=classic_project)
    opik_check = verify_opik_project(workspace=workspace, expected_name=opik_project, host=opik_host)
    comet = ClassicCometAdapter.create(
        project_check=classic_check,
        workspace=workspace,
        run_name=run_name,
        disabled=not bool(os.environ.get("COMET_API_KEY")),
    )
    opik = OpikAdapter.create(
        project_check=opik_check,
        workspace=workspace,
        disabled=not bool(_opik_api_key()),
    )
    opik_trace = opik.start_trace(name=run_name, metadata=metadata, input_payload=input_payload)
    return TrackingBundle(
        workspace=workspace,
        classic_project=classic_project,
        opik_project=opik_project,
        opik_host=opik_host,
        classic_check=classic_check,
        opik_check=opik_check,
        comet=comet,
        opik=opik,
        opik_trace=opik_trace,
    )
