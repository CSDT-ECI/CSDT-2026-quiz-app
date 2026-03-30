"""Tests for quiz API endpoints in app/api/quiz.py."""
import json
from unittest.mock import MagicMock, patch


def _login(client, username="quizmaster"):
    """Helper: register and login a user, return the client with session."""
    client.post(
        "/api/add-account",
        data=json.dumps({
            "full_name": "Quiz Master",
            "username": username,
            "password": "secret123",
            "password_confirmation": "secret123",
            "email": f"{username}@example.com",
        }),
        content_type="application/json",
    )
    client.post(
        "/api/login",
        data=json.dumps({"username": username, "password": "secret123"}),
        content_type="application/json",
    )


def test_add_quiz_requires_login(client):
    """Adding a quiz without being logged in should redirect."""
    response = client.post(
        "/api/quiz/add-quiz",
        data=json.dumps({"quiz_title": "Test", "data": []}),
        content_type="application/json",
    )
    assert response.status_code == 302


def test_add_quiz_success(client):
    """Authenticated user should be able to create a quiz."""
    _login(client)
    response = client.post(
        "/api/quiz/add-quiz",
        data=json.dumps({
            "quiz_title": "My Quiz",
            "data": [
                {"question": "What is 1+1?", "a_option": "1", "b_option": "2", "c_option": "3", "answer": "b_option"},
            ],
        }),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"
    assert "url" in data


def test_get_question_strips_answers(client):
    """Getting quiz questions should not include answers."""
    _login(client)
    # Create a quiz
    create_resp = client.post(
        "/api/quiz/add-quiz",
        data=json.dumps({
            "quiz_title": "Answer Strip Test",
            "data": [
                {"question": "Q1?", "a_option": "A", "b_option": "B", "answer": "a_option"},
            ],
        }),
        content_type="application/json",
    )
    code = create_resp.get_json()["url"].split("/")[-1]

    # Get questions
    response = client.get(f"/api/quiz/getQuestion/{code}")
    questions = response.get_json()
    assert isinstance(questions, list)
    for q in questions:
        assert "answer" not in q


def test_get_question_nonexistent_code(client):
    """Getting questions for a nonexistent quiz should return failed."""
    response = client.get("/api/quiz/getQuestion/nonexistent")
    data = response.get_json()
    assert data["status"] == "failed"


def test_view_quiz_requires_login(client):
    """Viewing quiz details without login should redirect."""
    response = client.get("/api/quiz/view/somecode")
    assert response.status_code == 302


def test_nilai_calculates_score(client):
    """Submitting answers should calculate the score correctly."""
    _login(client, "scorer")
    # Create a quiz with known answers
    create_resp = client.post(
        "/api/quiz/add-quiz",
        data=json.dumps({
            "quiz_title": "Score Test",
            "data": [
                {"question": "Q1?", "a_option": "A", "b_option": "B", "answer": "a_option"},
                {"question": "Q2?", "a_option": "X", "b_option": "Y", "answer": "b_option"},
            ],
        }),
        content_type="application/json",
    )
    code = create_resp.get_json()["url"].split("/")[-1]

    # Submit all correct answers
    response = client.post(
        f"/api/quiz/nilai/{code}",
        data=json.dumps({"quest_0": "a_option", "quest_1": "b_option"}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"]["score"] == 100


def test_nilai_partial_score(client):
    """Submitting partially correct answers should give partial score."""
    _login(client, "partial")
    create_resp = client.post(
        "/api/quiz/add-quiz",
        data=json.dumps({
            "quiz_title": "Partial Test",
            "data": [
                {"question": "Q1?", "a_option": "A", "b_option": "B", "answer": "a_option"},
                {"question": "Q2?", "a_option": "X", "b_option": "Y", "answer": "b_option"},
            ],
        }),
        content_type="application/json",
    )
    code = create_resp.get_json()["url"].split("/")[-1]

    # Submit 1 correct, 1 wrong
    response = client.post(
        f"/api/quiz/nilai/{code}",
        data=json.dumps({"quest_0": "a_option", "quest_1": "a_option"}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"]["score"] == 50


def test_my_scores_empty(client):
    """My scores should return empty when user has no scores."""
    _login(client, "noscores")
    response = client.get("/api/quiz/my-scores")
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"] == []


def test_upload_csv_requires_login(client):
    """Uploading CSV without login should redirect."""
    response = client.post("/api/quiz/uploadCsv")
    assert response.status_code == 302


def test_get_scores_not_logged_in(client):
    """Getting scores without being logged in should fail."""
    response = client.get("/api/quiz/author/someuser/getScores")
    data = response.get_json()
    assert data["status"] == "failed" or data.get("data") == []


def test_add_quiz_invalid_data_null_json(client):
    """POST add-quiz with JSON null body should return invalid data (line 23)."""
    _login(client, "nullquizuser")
    response = client.post(
        "/api/quiz/add-quiz",
        data="null",
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "fail"
    assert "invalid data" in data.get("message", "").lower()


def test_edit_quiz_without_quiz_title_sets_default(logged_in_client, sample_quiz):
    """edit_quiz without quiz_title should default to 'Unkown title' (lines 51-53)."""
    response = logged_in_client.post(
        f"/api/quiz/edit/{sample_quiz}",
        data=json.dumps({"data": []}),
        content_type="application/json",
    )
    assert response.get_json()["status"] == "success"
    from app.db import quiz as quiz_col

    with logged_in_client.application.app_context():
        doc = quiz_col.find_one({"code": sample_quiz})
    assert doc.get("quiz_title") == "Unkown title"


def test_nilai_without_logged_in_user_skips_score_insert(app, client):
    """nilai with no session should not insert into db.score but still succeed (90->96)."""
    from app.db import db, quiz as quiz_col

    code = "nilai_anon"
    with app.app_context():
        quiz_col.insert_one({
            "code": code,
            "author": "someauthor",
            "quiz_title": "Anon",
            "data": [
                {"question": "Q?", "a_option": "A", "b_option": "B", "answer": "a_option"},
            ],
        })
        before = db.score.count_documents({})

    response = client.post(
        f"/api/quiz/nilai/{code}",
        data=json.dumps({"quest_0": "a_option"}),
        content_type="application/json",
    )
    data = response.get_json()
    assert data["status"] == "success"

    with app.app_context():
        after = db.score.count_documents({})
    assert after == before


def test_get_scores_logged_in_alias_without_session(client):
    """GET author/logged_in/getScores without session returns not logged in (line 108)."""
    response = client.get("/api/quiz/author/logged_in/getScores")
    data = response.get_json()
    assert data["status"] == "fail"
    assert "not logged in" in data.get("message", "").lower()


def test_get_scores_for_author_returns_success_with_scores(app, client):
    """get_scorest returns success when quizzes and scores exist (115-116)."""
    from app.db import db, quiz as quiz_col

    with app.app_context():
        quiz_col.insert_one({
            "code": "scorecode1",
            "author": "authorx",
            "quiz_title": "Q",
            "data": [],
        })
        db.score.insert_one({
            "quiz_code": "scorecode1",
            "score": 100,
            "done_by": "student1",
            "name": "Student",
            "quiz_title": "Q",
        })

    response = client.get("/api/quiz/author/authorx/getScores")
    data = response.get_json()
    assert data["status"] == "success"
    assert len(data.get("data", [])) >= 1


def test_get_scores_for_author_no_quizzes_returns_failed(client):
    """get_scorest returns failed with empty data when author has no quizzes (117)."""
    response = client.get("/api/quiz/author/userwithnoquizzes/getScores")
    data = response.get_json()
    assert data["status"] == "failed"
    assert data.get("data") == []


def test_quiz_search_mocked_success(client):
    """quiz_search with mocked index and find returns success URLs (129-146)."""
    fake_quiz = {"code": "findme", "quiz_title": "Searchable"}
    mock_coll = MagicMock()
    mock_coll.index_information.return_value = {}
    mock_coll.create_index.return_value = "search_text"
    mock_coll.find.return_value = [fake_quiz]

    with patch("app.api.quiz.quiz", mock_coll):
        response = client.post(
            "/api/quiz/search",
            data=json.dumps({"search": "hello"}),
            content_type="application/json",
        )
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"]
    assert "findme" in data["data"][0]


def test_quiz_search_mocked_no_results(client):
    """quiz_search with empty find result returns fail (146)."""
    mock_coll = MagicMock()
    mock_coll.index_information.return_value = {"search_text": {}}
    mock_coll.find.return_value = []

    with patch("app.api.quiz.quiz", mock_coll):
        response = client.post(
            "/api/quiz/search",
            data=json.dumps({"search": "nothing"}),
            content_type="application/json",
        )
    data = response.get_json()
    assert data["status"] == "fail"
    assert data.get("data") == []
