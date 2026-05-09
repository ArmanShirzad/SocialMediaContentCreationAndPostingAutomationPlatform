class DashboardController < ApplicationController
  def index
    @total = Article.count
    @posted = Article.where("posted_to_instagram = ? OR posted_to_telegram = ? OR posted_to_x = ?", true, true, true).count
    @pending = @total - @posted
    @translated = Article.where.not(translated_title: [nil, ""]).count
    @recent_articles = Article.recent.limit(10)
  end
end
