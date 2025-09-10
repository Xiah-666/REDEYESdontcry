from redeyes.core.exec import safe_run

def test_safe_run_echo(tmp_path):
    res = safe_run(["echo", "hello"], output_file=tmp_path / "o.txt")
    assert res.ok
    assert "hello" in res.stdout

