require "test_helper"

class ArticleTest < ActiveSupport::TestCase
  # -- Validations --

  test "valid article with all required attributes" do
    article = Article.new(url: "https://example.com/unique-article")
    assert article.valid?
  end

  test "invalid without url" do
    article = Article.new(url: nil)
    assert_not article.valid?
    assert_includes article.errors[:url], "can't be blank"
  end

  test "invalid with duplicate url" do
    existing = articles(:pending_article)
    duplicate = Article.new(url: existing.url)
    assert_not duplicate.valid?
    assert_includes duplicate.errors[:url], "has already been taken"
  end

  # -- #status --

  test "status returns :pending when nothing is posted" do
    article = articles(:pending_article)
    assert_equal :pending, article.status
  end

  test "status returns :partial when some platforms are posted" do
    article = articles(:partial_article)
    assert_equal :partial, article.status
  end

  test "status returns :completed when all platforms are posted" do
    article = articles(:completed_article)
    assert_equal :completed, article.status
  end

  # -- #status_label --

  test "status_label returns Korean label for pending" do
    assert_equal "대기중", articles(:pending_article).status_label
  end

  test "status_label returns Korean label for partial" do
    assert_equal "진행중", articles(:partial_article).status_label
  end

  test "status_label returns Korean label for completed" do
    assert_equal "완료", articles(:completed_article).status_label
  end

  # -- #translated? --

  test "translated? returns false when translated_title is blank" do
    article = articles(:pending_article)
    assert_not article.translated?
  end

  test "translated? returns false when translated_content is blank" do
    article = Article.new(url: "https://example.com/half", translated_title: "제목", translated_content: nil)
    assert_not article.translated?
  end

  test "translated? returns true when both translated_title and translated_content are present" do
    article = articles(:completed_article)
    assert article.translated?
  end

  # -- #all_posted? --

  test "all_posted? returns false when not all platforms are posted" do
    assert_not articles(:pending_article).all_posted?
    assert_not articles(:partial_article).all_posted?
  end

  test "all_posted? returns true when all platforms are posted" do
    assert articles(:completed_article).all_posted?
  end

  # -- #any_posted? --

  test "any_posted? returns false when no platform is posted" do
    assert_not articles(:pending_article).any_posted?
  end

  test "any_posted? returns true when at least one platform is posted" do
    assert articles(:partial_article).any_posted?
    assert articles(:completed_article).any_posted?
  end

  # -- .recent scope --

  test "recent scope orders articles by created_at desc" do
    articles = Article.recent.to_a

    articles.each_cons(2) do |newer, older|
      assert newer.created_at >= older.created_at,
        "Expected #{newer.title} (#{newer.created_at}) to be newer than #{older.title} (#{older.created_at})"
    end
  end

  test "recent scope returns all articles" do
    assert_equal Article.count, Article.recent.count
  end
end
