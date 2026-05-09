class TranslateJob < ApplicationJob
  queue_as :default

  def perform(article_id)
    article = Article.find(article_id)
    service = GroqTranslator.new
    article.update!(
      translated_title: service.translate(article.title),
      translated_content: service.translate(article.content),
      summary: service.summarize(article.content)
    )
  end
end
