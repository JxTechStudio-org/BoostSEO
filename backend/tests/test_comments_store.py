from app.services.comments_store import CommentsStore


def test_insert_comment_returns_expected_shape_without_email(tmp_path):
    store = CommentsStore(tmp_path / "test.db")

    result = store.insert_comment("Jane", "jane@example.com", "Great tool!")

    assert result["name"] == "Jane"
    assert result["body"] == "Great tool!"
    assert "email" not in result
    assert isinstance(result["id"], int)
    assert "created_at" in result


def test_list_comments_returns_newest_first_without_email(tmp_path):
    store = CommentsStore(tmp_path / "test.db")
    store.insert_comment("Alice", "alice@example.com", "First comment")
    store.insert_comment("Bob", "bob@example.com", "Second comment")

    comments = store.list_comments()

    assert [c["name"] for c in comments] == ["Bob", "Alice"]
    assert all("email" not in c for c in comments)


def test_list_comments_respects_limit(tmp_path):
    store = CommentsStore(tmp_path / "test.db")
    for i in range(5):
        store.insert_comment(f"User{i}", f"user{i}@example.com", "Comment body")

    comments = store.list_comments(limit=2)

    assert len(comments) == 2


def test_store_creates_data_directory_and_table(tmp_path):
    db_path = tmp_path / "nested" / "comments.db"

    store = CommentsStore(db_path)

    assert db_path.parent.is_dir()
    assert store.list_comments() == []
