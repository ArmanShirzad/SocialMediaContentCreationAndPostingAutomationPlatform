class ArticlesController < ApplicationController
  def index
    scope = Article.recent
    if params[:q].present?
      q = "%#{Article.sanitize_sql_like(params[:q])}%"
      scope = scope.where("title LIKE ? OR translated_title LIKE ?", q, q)
    end
    @pagy, @articles = pagy(scope)
  end

  def show
    @article = Article.find(params[:id])
  end

  def translate
    @article = Article.find(params[:id])
    service = GroqTranslator.new
    @article.update!(
      translated_title: service.translate(@article.title),
      translated_content: service.translate(@article.content),
      summary: service.summarize(@article.content)
    )
    respond_to do |format|
      format.turbo_stream do
        render turbo_stream: [
          turbo_stream.replace("translation", partial: "articles/translation", locals: { article: @article }),
          turbo_stream.replace("platforms", partial: "articles/platforms", locals: { article: @article })
        ]
      end
      format.html { redirect_to @article, notice: "번역이 완료되었습니다." }
    end
  rescue => e
    respond_to do |format|
      format.turbo_stream do
        render turbo_stream: turbo_stream.update("translation",
          "<div class='px-4 py-3 rounded-md bg-error-muted text-error text-sm'>번역 실패: #{e.message}</div>")
      end
      format.html { redirect_to @article, alert: "번역 실패: #{e.message}" }
    end
  end

  def scrape
    service = ScraperService.new
    keyword = params[:keyword].presence
    count = service.run(keyword: keyword)
    msg = keyword ? "\"#{keyword}\" 관련 #{count}개의 새 기사를 스크래핑했습니다." : "#{count}개의 새 기사를 스크래핑했습니다."
    redirect_to articles_path, notice: msg
  rescue => e
    redirect_to articles_path, alert: "스크래핑 실패: #{e.message}"
  end

  def post_to_platform
    @article = Article.find(params[:id])
    platform = params[:platform]

    unless %w[telegram instagram x].include?(platform)
      redirect_to @article, alert: "알 수 없는 플랫폼: #{platform}"
      return
    end

    service = PythonRunner.new
    result = service.post(@article, platform)

    if result[:success]
      @article.update!("posted_to_#{platform}" => true)
    end

    respond_to do |format|
      format.turbo_stream do
        render turbo_stream: turbo_stream.replace("platforms", partial: "articles/platforms", locals: { article: @article })
      end
      format.html do
        if result[:success]
          redirect_to @article, notice: "#{platform.capitalize}에 포스팅 완료."
        else
          redirect_to @article, alert: "포스팅 실패: #{result[:error]}"
        end
      end
    end
  end
end
