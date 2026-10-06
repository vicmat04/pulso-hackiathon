import pytest

from pulso import config, manifest, pipeline


@pytest.fixture(scope="session")
def snap(tmp_path_factory):
    config.REVIEW_LOG = tmp_path_factory.mktemp("rev") / "review_log.jsonl"
    manifest.build()
    s = pipeline.build()
    pipeline.write_outputs(s)
    return s
