import pytest
from sqlalchemy import event


def _count_list_queries(client, db_session) -> int:
    # 세션 캐시를 비워서 태그를 실제로 DB에서 다시 읽게 합니다.
    db_session.expunge_all()

    count = 0

    def _count(*_):
        nonlocal count
        count += 1

    engine = db_session.get_bind()
    event.listen(engine, "before_cursor_execute", _count)
    try:
        res = client.get("/tasks")
    finally:
        event.remove(engine, "before_cursor_execute", _count)

    assert res.status_code == 200
    return count


@pytest.mark.parametrize("n_tasks", [1, 10])
def test_list_tasks_query_count_is_constant(client, db_session, n_tasks):
    # 할 일 개수와 상관없이 할 일 1회 + 태그 IN 1회로 끝나야 합니다(N+1 회귀 방지).
    for i in range(n_tasks):
        client.post("/tasks", json={"title": f"t{i}", "tags": ["a", "b"]})

    assert _count_list_queries(client, db_session) == 2
