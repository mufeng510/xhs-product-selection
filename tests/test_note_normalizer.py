from app.adapters.xhs.normalizer import normalize_note, unwrap_cli


def test_note_card_and_interact():
    raw = {"note_card": {"note_id": "n1", "title": "t", "user": {"user_id": "u1", "nickname": "a"}, "interact_info": {"liked_count": "3"}}}
    data = normalize_note(raw)
    assert data["source_note_id"] == "n1"
    assert data["author_id"] == "u1"
    assert data["like_count"] == 3


def test_unwrap_cli_tuple():
    assert unwrap_cli([True, "ok", {"id": 1}]) == {"id": 1}
