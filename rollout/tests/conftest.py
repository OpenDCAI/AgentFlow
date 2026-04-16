import os
from pathlib import Path

import pytest


_REAL_CODE_TEST_FILES = {
    "test_code_real_smoke.py",
}


def _code_real_enabled():
    return os.environ.get("AGENTFLOW_RUN_CODE_REAL") == "1"


def pytest_ignore_collect(collection_path, config):
    del config
    if _code_real_enabled():
        return False

    path = Path(str(collection_path))
    return path.name in _REAL_CODE_TEST_FILES


def pytest_addoption(parser):
    group = parser.getgroup("agentflow-code-real")
    group.addoption(
        "--real-api-key",
        action="store",
        default=None,
        help="API key for opt-in real code rollout smoke tests.",
    )
    group.addoption(
        "--real-base-url",
        action="store",
        default=None,
        help="Base URL for opt-in real code rollout smoke tests.",
    )
    group.addoption(
        "--real-model",
        action="store",
        default=None,
        help="Model name for opt-in real code rollout smoke tests.",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "code_real: opt-in real code rollout smoke tests",
    )


def pytest_collection_modifyitems(config, items):
    if _code_real_enabled():
        return

    deselected = []
    kept = []
    for item in items:
        if item.get_closest_marker("code_real") is None:
            kept.append(item)
            continue

        if Path(str(item.fspath)).name in _REAL_CODE_TEST_FILES:
            deselected.append(item)
        else:
            kept.append(item)

    if deselected:
        items[:] = kept
        config.hook.pytest_deselected(items=deselected)


def _get_real_credentials(config):
    return {
        "api_key": config.getoption("--real-api-key"),
        "base_url": config.getoption("--real-base-url"),
        "model": config.getoption("--real-model"),
    }


def _missing_real_credential_options(config):
    credentials = _get_real_credentials(config)
    return [
        option_name
        for option_name, value in (
            ("--real-api-key", credentials["api_key"]),
            ("--real-base-url", credentials["base_url"]),
            ("--real-model", credentials["model"]),
        )
        if not value
    ]


def pytest_runtest_setup(item):
    if item.get_closest_marker("code_real") is None:
        return

    if not _code_real_enabled():
        pytest.skip("set AGENTFLOW_RUN_CODE_REAL=1 to run real code rollout smoke tests")

    missing = _missing_real_credential_options(item.config)
    if missing:
        pytest.skip(
            "code_real tests require all of "
            "--real-api-key, --real-base-url, and --real-model"
        )


@pytest.fixture
def real_llm_credentials(request):
    credentials = _get_real_credentials(request.config)
    if _missing_real_credential_options(request.config):
        pytest.skip(
            "code_real tests require all of "
            "--real-api-key, --real-base-url, and --real-model"
        )
    return credentials


@pytest.fixture
def real_api_key(real_llm_credentials):
    return real_llm_credentials["api_key"]


@pytest.fixture
def real_base_url(real_llm_credentials):
    return real_llm_credentials["base_url"]


@pytest.fixture
def real_model(real_llm_credentials):
    return real_llm_credentials["model"]
