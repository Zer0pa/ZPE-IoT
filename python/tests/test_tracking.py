from __future__ import annotations

import sys
import types
from pathlib import Path

import zpe_iot.tracking as tracking
from zpe_iot.tracking import (
    ClassicCometAdapter,
    DEFAULT_CLASSIC_PROJECT,
    DEFAULT_OPIK_PROJECT,
    DEFAULT_OPIK_URL,
    DEFAULT_WORKSPACE,
    OpikAdapter,
    ProjectCheck,
    create_tracking_bundle,
)


def _install_fake_comet(monkeypatch):
    comet_module = types.ModuleType("comet_ml")
    api_module = types.ModuleType("comet_ml.api")

    class FakeExperiment:
        instances: list["FakeExperiment"] = []

        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.name = ""
            self.parameters: list[tuple[str, object]] = []
            self.metrics: list[dict[str, float]] = []
            self.others: list[dict[str, object]] = []
            self.assets: list[str] = []
            self.texts: list[str] = []
            self.url = "https://classic.example/experiment"
            self.ended = False
            FakeExperiment.instances.append(self)

        def set_name(self, name: str) -> None:
            self.name = name

        def log_parameter(self, key: str, value: object) -> None:
            self.parameters.append((key, value))

        def log_metrics(self, metrics: dict[str, float]) -> None:
            self.metrics.append(metrics)

        def log_others(self, payload: dict[str, object]) -> None:
            self.others.append(payload)

        def log_asset(self, path: str) -> None:
            self.assets.append(path)

        def log_text(self, text: str) -> None:
            self.texts.append(text)

        def get_key(self) -> str:
            return "classic-exp-key"

        def end(self) -> None:
            self.ended = True

    class FakeAPI:
        projects: dict[tuple[str, str], dict[str, str]] = {}
        created: list[tuple[str, str]] = []

        def __init__(self, api_key: str | None = None) -> None:
            self.api_key = api_key

        def get_project(self, workspace: str, name: str):
            return self.projects.get((workspace, name))

        def create_project(self, workspace: str, name: str) -> None:
            self.created.append((workspace, name))
            self.projects[(workspace, name)] = {
                "name": name,
                "id": f"{workspace}-{name}-id",
                "slug": f"{workspace}/{name}",
                "url": f"https://classic.example/{workspace}/{name}",
            }

    comet_module.Experiment = FakeExperiment
    api_module.API = FakeAPI
    monkeypatch.setitem(sys.modules, "comet_ml", comet_module)
    monkeypatch.setitem(sys.modules, "comet_ml.api", api_module)
    return FakeAPI, FakeExperiment


def _install_fake_opik(monkeypatch):
    opik_module = types.ModuleType("opik")
    api_error_module = types.ModuleType("opik.rest_api.core.api_error")
    api_objects_module = types.ModuleType("opik.api_objects")
    opik_client_module = types.ModuleType("opik.api_objects.opik_client")

    class FakeApiError(Exception):
        def __init__(self, status_code: int, message: str = "api error") -> None:
            super().__init__(message)
            self.status_code = status_code

    class FakeTrace:
        def __init__(self) -> None:
            self.id = "trace-123"
            self.metadata_updates: list[dict[str, object]] = []
            self.output: dict[str, object] | None = None

        def log_metadata(self, metadata: dict[str, object]) -> None:
            self.metadata_updates.append(metadata)

        def end(self, *, output: dict[str, object]) -> None:
            self.output = output

    class FakeProjects:
        def __init__(self, store: dict[str, object]) -> None:
            self.store = store
            self.create_calls: list[str] = []

        def retrieve_project(self, name: str):
            if name not in self.store:
                raise FakeApiError(404, "missing")
            return self.store[name]

        def create_project(self, name: str) -> None:
            self.create_calls.append(name)
            self.store[name] = types.SimpleNamespace(name=name, id=f"{name}-id")

    class FakeOpik:
        store: dict[str, object] = {}
        instances: list["FakeOpik"] = []

        def __init__(
            self,
            *,
            project_name: str,
            workspace: str,
            host: str,
            api_key: str | None,
            _use_batching: bool,
            _show_misconfiguration_message: bool,
        ) -> None:
            self.project_name = project_name
            self.workspace = workspace
            self.host = host
            self.api_key = api_key
            self._config = types.SimpleNamespace(url_override=host)
            self.rest_client = types.SimpleNamespace(projects=FakeProjects(type(self).store))
            self.trace_calls: list[tuple[str, dict[str, object], dict[str, object]]] = []
            self.flushed = False
            self.ended = False
            FakeOpik.instances.append(self)

        def auth_check(self) -> None:
            return None

        def get_project_url(self, name: str) -> str:
            return f"{self.host.rstrip('/')}/{self.workspace}/{name}"

        def trace(self, *, name: str, project_name: str, metadata: dict[str, object], input: dict[str, object], thread_id: str):
            self.trace_calls.append((name, metadata, input))
            return FakeTrace()

        def flush(self) -> None:
            self.flushed = True

        def end(self) -> None:
            self.ended = True

    class FakeUrlHelpers:
        @staticmethod
        def get_project_url_by_trace_id(*, trace_id: str, url_override: str) -> str:
            return f"{url_override.rstrip('/')}/traces/{trace_id}"

    opik_module.Opik = FakeOpik
    api_error_module.ApiError = FakeApiError
    opik_client_module.url_helpers = FakeUrlHelpers
    api_objects_module.opik_client = opik_client_module

    monkeypatch.setitem(sys.modules, "opik", opik_module)
    monkeypatch.setitem(sys.modules, "opik.rest_api.core.api_error", api_error_module)
    monkeypatch.setitem(sys.modules, "opik.api_objects", api_objects_module)
    monkeypatch.setitem(sys.modules, "opik.api_objects.opik_client", opik_client_module)
    return FakeOpik, FakeApiError


def test_tracking_bundle_defaults_to_local_hold_without_credentials(monkeypatch) -> None:
    for key in (
        "COMET_API_KEY",
        "COMET_PROJECT_NAME",
        "COMET_WORKSPACE",
        "OPIK_API_KEY",
        "OPIK_PROJECT_NAME",
        "OPIK_WORKSPACE",
        "OPIK_URL_OVERRIDE",
    ):
        monkeypatch.delenv(key, raising=False)

    bundle = create_tracking_bundle(
        run_name="unit-test-benchmark",
        input_payload={"mode": "local"},
        metadata={"lane": "zpe-iot"},
    )

    assert bundle.workspace == DEFAULT_WORKSPACE
    assert bundle.classic_project == DEFAULT_CLASSIC_PROJECT
    assert bundle.opik_project == DEFAULT_OPIK_PROJECT
    assert bundle.opik_host == DEFAULT_OPIK_URL
    assert bundle.classic_check.status == "HOLD"
    assert bundle.opik_check.status == "HOLD"
    assert bundle.classic_check.handshake_error == "COMET_API_KEY missing"
    assert bundle.opik_check.handshake_error == "OPIK_API_KEY missing"
    assert not bundle.comet.enabled
    assert not bundle.opik.enabled

    finished = bundle.finish(artifact_paths=[], output_payload={"status": "local_only"})
    assert finished["classic_status"] == "HOLD"
    assert finished["opik_status"] == "HOLD"
    assert finished["classic_experiment_key"] == ""
    assert finished["opik_trace_id"] == ""


def test_project_identity_and_flatten_helpers_cover_nested_payloads() -> None:
    class ProjectObject:
        name = "project-a"
        id = "project-id"
        slug = "workspace/project-a"
        url = "https://example.invalid/project-a"

    assert tracking._project_identity({"projectName": "project-b", "projectId": "b-id"}) == {
        "name": "project-b",
        "id": "b-id",
    }
    assert tracking._project_identity(ProjectObject()) == {
        "name": "project-a",
        "id": "project-id",
        "slug": "workspace/project-a",
        "url": "https://example.invalid/project-a",
    }

    nested = {
        "summary": {"mean_cr": 6.5, "winner": "zpe-iot", "passed": True},
        "datasets": [{"name": "DS-01", "cr": 7.0}, {"name": "DS-02", "cr": 6.2}],
    }
    assert tracking.flatten_numeric_mapping(nested, prefix="bench") == {
        "bench.summary.mean_cr": 6.5,
        "bench.summary.passed": 1.0,
        "bench.datasets[0].cr": 7.0,
        "bench.datasets[1].cr": 6.2,
    }
    assert tracking.flatten_string_mapping(nested, prefix="bench") == {
        "bench.summary.winner": "zpe-iot",
        "bench.datasets[0].name": "DS-01",
        "bench.datasets[1].name": "DS-02",
    }


def test_verify_classic_project_handles_existing_and_created_paths(monkeypatch) -> None:
    FakeAPI, _ = _install_fake_comet(monkeypatch)
    monkeypatch.setenv("COMET_API_KEY", "classic-token")

    FakeAPI.projects[("zer0pa", "zpe-iot-performance")] = {
        "name": "zpe-iot-performance",
        "id": "existing-id",
        "slug": "zer0pa/zpe-iot-performance",
        "url": "https://classic.example/zer0pa/zpe-iot-performance",
    }
    existing = tracking.verify_classic_comet_project(workspace="zer0pa", expected_name="zpe-iot-performance")
    assert existing.status == "EXISTS"
    assert existing.resolved_id == "existing-id"

    created = tracking.verify_classic_comet_project(workspace="zer0pa", expected_name="brand-new-project")
    assert created.status == "CREATED"
    assert created.resolved_name == "brand-new-project"
    assert ("zer0pa", "brand-new-project") in FakeAPI.created


def test_verify_opik_project_handles_created_path(monkeypatch) -> None:
    FakeOpik, _ = _install_fake_opik(monkeypatch)
    monkeypatch.setenv("OPIK_API_KEY", "opik-token")

    result = tracking.verify_opik_project(
        workspace="zer0pa",
        expected_name="zpe-iot-performance",
        host="https://www.comet.com/opik/api",
    )

    assert result.status == "CREATED"
    assert result.resolved_name == "zpe-iot-performance"
    assert result.resolved_id == "zpe-iot-performance-id"
    assert result.url.endswith("/zer0pa/zpe-iot-performance")
    assert FakeOpik.instances[-1].ended is True


def test_tracking_bundle_enables_fake_backends_and_logs_outputs(monkeypatch, tmp_path: Path) -> None:
    _, FakeExperiment = _install_fake_comet(monkeypatch)
    FakeOpik, _ = _install_fake_opik(monkeypatch)
    monkeypatch.setenv("COMET_API_KEY", "classic-token")
    monkeypatch.setenv("OPIK_API_KEY", "opik-token")
    monkeypatch.setenv("COMET_PROJECT_NAME", "classic-override")
    monkeypatch.setenv("OPIK_PROJECT_NAME", "opik-override")
    monkeypatch.setenv("COMET_WORKSPACE", "zer0pa")

    bundle = create_tracking_bundle(
        run_name="bench-e1",
        input_payload={"surface": "E1"},
        metadata={"lane": "iot", "wave": 2},
    )

    assert bundle.comet.enabled
    assert bundle.opik.enabled
    bundle.comet.log_parameters({"dataset_count": 11})
    bundle.comet.log_metrics({"mean_cr": 17.16})
    bundle.log_payload(
        "bench",
        {"summary": {"mean_cr": 17.16, "winner": "zpe-iot", "passed": True}},
    )

    artifact = tmp_path / "bench-summary.json"
    artifact.write_text("{}", encoding="utf-8")
    finished = bundle.finish(artifact_paths=[str(artifact)], output_payload={"status": "ok"})

    experiment = FakeExperiment.instances[-1]
    opik_client = FakeOpik.instances[-1]
    assert experiment.name == "bench-e1"
    assert ("dataset_count", 11) in experiment.parameters
    assert {"mean_cr": 17.16} in experiment.metrics
    assert {"bench.summary.winner": "zpe-iot"} in experiment.others
    assert str(artifact) in experiment.assets
    assert any("metrics logging enabled" in text for text in experiment.texts)
    assert finished["classic_status"] in {"EXISTS", "CREATED"}
    assert finished["classic_experiment_key"] == "classic-exp-key"
    assert finished["opik_status"] in {"EXISTS", "CREATED"}
    assert finished["opik_trace_id"] == "trace-123"
    assert finished["opik_trace_url"].endswith("/traces/trace-123")
    assert opik_client.trace_calls[0][0] == "bench-e1"
    assert opik_client.flushed is True
    assert opik_client.ended is True


def test_adapters_record_soft_failures_without_crashing(monkeypatch) -> None:
    class FailingExperiment:
        url = ""

        def log_parameter(self, key: str, value: object) -> None:
            return None

        def log_metrics(self, metrics: dict[str, float]) -> None:
            return None

        def log_others(self, payload: dict[str, object]) -> None:
            raise RuntimeError("others failed")

        def log_asset(self, path: str) -> None:
            raise RuntimeError("asset failed")

        def log_text(self, text: str) -> None:
            raise RuntimeError("text failed")

        def get_key(self) -> str:
            return ""

        def end(self) -> None:
            raise RuntimeError("end failed")

    class FailingTrace:
        id = "trace-456"

        def log_metadata(self, metadata: dict[str, object]) -> None:
            raise RuntimeError("metadata failed")

        def end(self, *, output: dict[str, object]) -> None:
            raise RuntimeError("end failed")

    class FailingClient:
        def __init__(self) -> None:
            self._config = types.SimpleNamespace(url_override="https://example.invalid/opik")

        def flush(self) -> None:
            raise RuntimeError("flush failed")

        def end(self) -> None:
            raise RuntimeError("end failed")

    comet = ClassicCometAdapter(FailingExperiment(), [])
    opik = OpikAdapter(FailingClient(), [])

    broken_api_objects = types.ModuleType("opik.api_objects")
    broken_opik_client = types.ModuleType("opik.api_objects.opik_client")

    class BrokenUrlHelpers:
        @staticmethod
        def get_project_url_by_trace_id(*, trace_id: str, url_override: str) -> str:
            raise RuntimeError("url failed")

    broken_opik_client.url_helpers = BrokenUrlHelpers
    broken_api_objects.opik_client = broken_opik_client
    monkeypatch.setitem(sys.modules, "opik.api_objects", broken_api_objects)
    monkeypatch.setitem(sys.modules, "opik.api_objects.opik_client", broken_opik_client)

    comet.log_others({"winner": "zpe-iot"})
    comet.log_asset("/tmp/noop.json")
    comet.log_text("hello")
    comet_result = comet.finish()
    assert comet_result["experiment_key"] == ""
    assert any("others log skipped" in note for note in comet.notes)
    assert any("asset log skipped" in note for note in comet.notes)
    assert any("text log skipped" in note for note in comet.notes)

    opik.log_metadata(FailingTrace(), {"mean_cr": 6.5})
    trace_id, trace_url = opik.finish_trace(FailingTrace(), output_payload={"status": "ok"})
    opik.finish()
    assert trace_id == "trace-456"
    assert trace_url == ""
    assert any("metadata log skipped" in note for note in opik.notes)
    assert any("trace end skipped" in note for note in opik.notes)
    assert any("trace URL resolution unavailable" in note for note in opik.notes)


def test_create_tracking_bundle_uses_env_overrides(monkeypatch) -> None:
    classic_check = ProjectCheck(target="classic_comet", status="EXISTS", resolved_name="classic-env")
    opik_check = ProjectCheck(target="opik", status="EXISTS", resolved_name="opik-env")

    monkeypatch.setenv("COMET_API_KEY", "classic-token")
    monkeypatch.setenv("OPIK_API_KEY", "opik-token")
    monkeypatch.setenv("COMET_WORKSPACE", "custom-workspace")
    monkeypatch.setenv("COMET_PROJECT_NAME", "classic-env")
    monkeypatch.setenv("OPIK_PROJECT_NAME", "opik-env")
    monkeypatch.setenv("OPIK_URL_OVERRIDE", "https://opik.example/api")
    monkeypatch.setattr(tracking, "verify_classic_comet_project", lambda **kwargs: classic_check)
    monkeypatch.setattr(tracking, "verify_opik_project", lambda **kwargs: opik_check)
    monkeypatch.setattr(
        ClassicCometAdapter,
        "create",
        classmethod(lambda cls, **kwargs: ClassicCometAdapter(None, ["classic disabled in unit test"])),
    )
    monkeypatch.setattr(
        OpikAdapter,
        "create",
        classmethod(lambda cls, **kwargs: OpikAdapter(None, ["opik disabled in unit test"])),
    )

    bundle = create_tracking_bundle(
        run_name="override-test",
        input_payload={"surface": "E1"},
        metadata={"lane": "iot"},
    )

    assert bundle.workspace == "custom-workspace"
    assert bundle.classic_project == "classic-env"
    assert bundle.opik_project == "opik-env"
    assert bundle.opik_host == "https://opik.example/api"
    assert bundle.classic_check is classic_check
    assert bundle.opik_check is opik_check
