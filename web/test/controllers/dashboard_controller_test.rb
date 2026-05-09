require "test_helper"

class DashboardControllerTest < ActionDispatch::IntegrationTest
  test "GET / returns 200" do
    get root_path
    assert_response :success
  end

  test "displays correct total count" do
    get root_path
    assert_response :success
    assert_select "div", text: Article.count.to_s
  end

  test "displays correct posted count" do
    expected_posted = Article.where(posted_to_instagram: true)
      .or(Article.where(posted_to_telegram: true))
      .or(Article.where(posted_to_x: true))
      .count

    get root_path
    assert_response :success
    assert_select ".text-success", text: expected_posted.to_s
  end

  test "displays correct pending count" do
    expected_pending = Article.where(
      posted_to_telegram: false,
      posted_to_instagram: false,
      posted_to_x: false
    ).count

    get root_path
    assert_response :success
    assert_select ".text-warning", text: expected_pending.to_s
  end

  test "displays recent articles table" do
    get root_path
    assert_response :success
    assert_select "table", 1
    assert_select "th", text: /기사 제목/
  end

  test "displays up to 10 recent articles" do
    get root_path
    assert_response :success
    assert_select "tbody tr", count: [ Article.count, 10 ].min
  end
end
