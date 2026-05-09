class DashboardController < ApplicationController
  def index
    @total = Article.count
    @posted = Article.where(posted_to_instagram: true).or(Article.where(posted_to_telegram: true)).or(Article.where(posted_to_x: true)).count
    @pending = Article.where(posted_to_telegram: false, posted_to_instagram: false, posted_to_x: false).count
    @recent_articles = Article.recent.limit(10)
  end
end
