"""測試 OpenCC 引擎"""

import pytest


def test_opencc_singleton():
    """測試 OpenCC 單例"""
    from app.core.opencc_engine import OpenCCEngine

    engine1 = OpenCCEngine()
    engine2 = OpenCCEngine()

    assert engine1 is engine2


def test_s2t_conversion():
    """測試簡體轉繁體"""
    from app.core.opencc_engine import opencc_engine

    result = opencc_engine.s2t("简体字")
    assert result == "簡體字"


def test_t2s_conversion():
    """測試繁體轉簡體"""
    from app.core.opencc_engine import opencc_engine

    result = opencc_engine.t2s("繁體字")
    assert result == "繁体字"


def test_get_available_modes():
    """測試取得可用模式"""
    from app.core.opencc_engine import OpenCCEngine

    modes = OpenCCEngine.get_available_modes()
    assert len(modes) >= 6
    assert any(m["mode"] == "s2t" for m in modes)
    assert any(m["mode"] == "t2s" for m in modes)
