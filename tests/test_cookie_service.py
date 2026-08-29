import asyncio
import json
from pathlib import Path

import pytest

from app.services import cookie_service, settings_store


@pytest.fixture()
def store_db(tmp_path, monkeypatch):
    db_path = tmp_path / "settings-test.db"
    url = f"sqlite:///{db_path}"
    settings_store.reset_test_state()
    monkeypatch.setattr(settings_store, "_db_url", lambda: url)
    yield url
    settings_store.reset_test_state()


def test_mask_hides_long_cookie():
    cookie = "a" * 10 + "b" * 100 + "xyz9"
    masked = cookie_service.mask(cookie)
    assert masked.startswith("aaaaaaaaaa…")
    assert masked.endswith("xyz9（114 字符）")
    assert "b" * 100 not in masked


def test_mask_short_and_none():
    assert cookie_service.mask("short-cookie") == "已配置"
    assert cookie_service.mask(None) is None


def test_resolve_prefers_db_over_env(store_db, monkeypatch):
    monkeypatch.setattr(settings_store, "get_value", lambda key: "db-cookie-value" if key == "xhs_pc_cookie" else None)
    info = cookie_service.resolve("pc")
    assert info.value == "db-cookie-value"
    assert info.source == "db"


def test_resolve_falls_back_to_env_chain(store_db, monkeypatch):
    from app.core import config

    fake = config.Settings(
        xhs_pc_cookie=None,
        aione_xhs_pc_cookies="legacy-aione-cookie",
        xhs_cookie="legacy-xhs-cookie",
        aione_xhs_qianfan_cookies="legacy-qianfan",
    )
    # _env_cookie 在调用时才 import get_settings，patch 模块属性即可生效
    monkeypatch.setattr(config, "get_settings", lambda: fake)

    pc = cookie_service.resolve("pc")
    assert pc.value == "legacy-aione-cookie"
    assert pc.source == "env:AIONE_XHS_PC_COOKIES"

    qf = cookie_service.resolve("qianfan")
    assert qf.value == "legacy-qianfan"
    assert qf.source == "env:AIONE_XHS_QIANFAN_COOKIES"


def test_resolve_new_env_name_wins_over_legacy(store_db, monkeypatch):
    from app.core import config

    fake = config.Settings(xhs_pc_cookie="new-name-cookie", xhs_cookie="legacy-alias")
    monkeypatch.setattr(config, "get_settings", lambda: fake)
    info = cookie_service.resolve("pc")
    assert info.value == "new-name-cookie"
    assert info.source == "env:XHS_PC_COOKIE"


def test_resolve_none_when_unconfigured(store_db, monkeypatch):
    from app.core import config

    monkeypatch.setattr(config, "get_settings", lambda: config.Settings())
    info = cookie_service.resolve("pc")
    assert info.value is None
    assert info.source == "none"


def test_save_and_status_roundtrip(store_db):
    result = cookie_service.save("pc", "x" * 40)
    assert result["configured"] is True
    assert result["source"] == "db"
    assert result["masked"] == cookie_service.mask("x" * 40)

    cleared = cookie_service.save("pc", "")
    assert cleared["configured"] is False
    assert cleared["source"] == "none"


def test_interpret_cli_wrapper_failure_and_success():
    assert cookie_service._interpret([False, "cookie 过期", None]) == ("invalid", "cookie 过期")
    ok_payload = [True, "", {"items": [{"id": 1}]}]
    assert cookie_service._interpret(ok_payload) == ("ok", "")


def test_interpret_xhs_error_codes():
    assert cookie_service._interpret({"success": False, "msg": "登录已过期"})[0] == "invalid"
    assert cookie_service._interpret({"code": -100, "msg": "未登录"})[0] == "invalid"
    assert cookie_service._interpret({"code": 0, "data": {"items": []}})[0] == "ok"
    assert cookie_service._interpret([{"id": 1}])[0] == "ok"


def test_validate_records_check_result(store_db, monkeypatch):
    async def fake_run(resource, action, args, *, profile):
        return [True, "", {"items": []}]

    result = asyncio.run(cookie_service.validate("pc", run_cli=fake_run))
    assert result["check_status"] == "ok"
    assert result["checked_at"] is not None

    async def failing_run(resource, action, args, *, profile):
        from app.adapters.xhs.cli import CLIError

        raise CLIError("aione exit=2", endpoint="note.search")

    result = asyncio.run(cookie_service.validate("qianfan", run_cli=failing_run))
    assert result["check_status"] == "error"
    assert "CLI 调用失败" in result["check_message"]

    stored = json.loads(settings_store.get_value("xhs_qianfan_cookie_check"))
    assert stored["status"] == "error"
