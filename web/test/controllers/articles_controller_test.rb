require "test_helper"

class ArticlesControllerTest < ActionDispatch::IntegrationTest
  # -- #index --

  test "GET /articles returns 200" do
    get articles_path
    assert_response :success
  end

  test "GET /articles renders article list with table" do
    get articles_path
    assert_response :success
    assert_select "table", 1
    assert_select "th", text: /기사 제목/
  end

  test "GET /articles displays all articles" do
    get articles_path
    assert_response :success
    assert_select "tbody tr", count: Article.count
  end

  test "GET /articles with search query filters by title" do
    get articles_path, params: { q: "Apple" }
    assert_response :success
    assert_select "tbody tr", count: 1
  end

  test "GET /articles with search query filters by translated_title" do
    get articles_path, params: { q: "개인정보" }
    assert_response :success
    assert_select "tbody tr", count: 1
  end

  test "GET /articles with non-matching search returns no rows" do
    get articles_path, params: { q: "zzz_no_match_zzz" }
    assert_response :success
    assert_select "tbody tr", count: 0
  end

  # -- #show --

  test "GET /articles/:id returns 200" do
    article = articles(:completed_article)
    get article_path(article)
    assert_response :success
  end

  test "GET /articles/:id displays article title" do
    article = articles(:completed_article)
    get article_path(article)
    assert_response :success
    assert_select "h1", text: article.title
  end

  test "GET /articles/:id shows translated content when available" do
    article = articles(:completed_article)
    get article_path(article)
    assert_response :success
    assert_select "h3", text: article.translated_title
  end

  test "GET /articles/:id shows translate button when not translated" do
    article = articles(:pending_article)
    get article_path(article)
    assert_response :success
    assert_select "a[href=?]", translate_article_path(article), text: /번역하기/
  end

  test "GET /articles/:id for nonexistent article returns 404" do
    get article_path(id: 999_999)
    assert_response :not_found
  end
end
