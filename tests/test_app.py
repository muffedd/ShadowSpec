from streamlit.testing.v1 import AppTest


def test_judge_ui_loads_and_runs_narrow_candidate():
    app = AppTest.from_file("app.py").run(timeout=10)
    assert not app.exception
    assert "ShadowSpec" in app.title[0].value
    assert app.radio[0].value == "Narrow candidate"
    app.button[0].click().run(timeout=10)
    assert not app.exception
    assert any("ACCEPTED" in item.value for item in app.success)

