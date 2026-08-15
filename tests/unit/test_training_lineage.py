from ml_platform.training.train import get_git_sha


def test_git_sha_can_be_supplied_without_git(monkeypatch) -> None:
    monkeypatch.setenv("GIT_SHA", "abc123")
    monkeypatch.setattr("ml_platform.training.train.shutil.which", lambda _: None)
    assert get_git_sha() == "abc123"


def test_git_sha_is_unavailable_when_git_is_missing(monkeypatch) -> None:
    monkeypatch.delenv("GIT_SHA", raising=False)
    monkeypatch.setattr("ml_platform.training.train.shutil.which", lambda _: None)
    assert get_git_sha() == "unavailable"
