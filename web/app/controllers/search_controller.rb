class SearchController < ApplicationController
  def index
    @keyword = params[:keyword]
    @results = []

    if @keyword.present?
      service = GoogleNewsService.new
      @results = service.search(@keyword)
      urls = @results.map { |r| r[:url] }
      @existing_articles = Article.where(url: urls).index_by(&:url)
    else
      @existing_articles = {}
    end
  end

  # 1단계: 기사 가져오기만 (본문 스크래핑)
  def import
    url = params[:url]
    article = Article.find_or_initialize_by(url: url)

    if article.persisted?
      redirect_to search_path(keyword: params[:keyword]), notice: "이미 저장된 기사입니다."
      return
    end

    # 본문 스크래핑
    scraper = ContentScraper.new
    data = scraper.scrape(url)

    article.assign_attributes(
      title: data[:title] || params[:title],
      content: data[:content],
      image_url: data[:image_url],
      crawl_datetime: Time.current
    )
    article.save!

    redirect_to search_path(keyword: params[:keyword]), notice: "\"#{article.title.truncate(40)}\" 저장 완료."
  rescue => e
    redirect_to search_path(keyword: params[:keyword]), alert: "가져오기 실패: #{e.message}"
  end

  # 풀 파이프라인: 스크래핑 + 번역 + 카드뉴스 이동
  def pipeline
    url = params[:url]
    article = Article.find_by(url: url)

    unless article
      # 1. 본문 스크래핑
      scraper = ContentScraper.new
      data = scraper.scrape(url)

      article = Article.create!(
        title: data[:title] || params[:title],
        url: url,
        content: data[:content],
        image_url: data[:image_url],
        crawl_datetime: Time.current
      )
    end

    # 2. 번역 (아직 안 된 경우)
    unless article.translated?
      translator = GroqTranslator.new
      article.update!(
        translated_title: translator.translate(article.title),
        translated_content: translator.translate(article.content),
        summary: translator.summarize(article.content)
      )
    end

    # 3. 카드뉴스 페이지로 이동
    redirect_to new_card_news_path(article_id: article.id, from_pipeline: true)
  rescue => e
    redirect_to search_path(keyword: params[:keyword]), alert: "처리 실패: #{e.message}"
  end
end
