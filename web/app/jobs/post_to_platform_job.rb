class PostToPlatformJob < ApplicationJob
  queue_as :default

  def perform(article_id, platform)
    article = Article.find(article_id)
    service = PythonRunner.new
    result = service.post(article, platform)

    if result[:success]
      article.update!("posted_to_#{platform}" => true)
    else
      Rails.logger.error("PostToPlatformJob failed: #{result[:error]}")
    end
  end
end
