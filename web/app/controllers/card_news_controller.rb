class CardNewsController < ApplicationController
  def new
    @articles = Article.where.not(translated_title: [nil, ""]).recent.limit(100)
    @article = if params[:article_id]
                 Article.find(params[:article_id])
               else
                 @articles.first
               end
    # pipeline으로 온 기사가 리스트에 없으면 추가
    if @article && !@articles.exists?(id: @article.id)
      @articles = Article.where(id: @articles.select(:id)).or(Article.where(id: @article.id)).recent
    end
    @generated_image = latest_image_for(@article) if @article
    @from_pipeline = params[:from_pipeline].present?
  end

  def create
    @article = Article.find(params[:article_id])
    @article.update!(
      translated_title: params[:translated_title],
      translated_content: params[:translated_content],
      summary: params[:summary]
    )
    redirect_to new_card_news_path(article_id: @article.id), notice: "카드뉴스 내용이 저장되었습니다."
  end

  def generate_image
    @article = Article.find(params[:article_id])
    service = CardNewsImageService.new
    path = service.generate(@article)
    redirect_to new_card_news_path(article_id: @article.id), notice: "카드뉴스 이미지가 생성되었습니다."
  rescue => e
    redirect_to new_card_news_path(article_id: @article&.id), alert: "이미지 생성 실패: #{e.message}"
  end

  def serve_image
    @article = Article.find(params[:article_id])
    path = latest_image_for(@article)
    if path && File.exist?(path)
      send_file path, type: "image/png", disposition: "inline"
    else
      head :not_found
    end
  end

  def download_image
    @article = Article.find(params[:article_id])
    path = latest_image_for(@article)
    if path && File.exist?(path)
      send_file path, type: "image/png", filename: "card_news_#{@article.id}.png"
    else
      redirect_to new_card_news_path(article_id: @article.id), alert: "이미지를 먼저 생성해주세요."
    end
  end

  private

  def latest_image_for(article)
    return nil unless article
    dir = Rails.root.join("storage", "card_news")
    return nil unless Dir.exist?(dir)
    files = Dir.glob(dir.join("card_#{article.id}_*.png")).sort
    files.last
  end
end
