class ScraperService
  def run(limit: 10, keyword: nil)
    python = File.join(project_root, "venv", "bin", "python")
    script = File.join(project_root, "scraper.py")

    unless File.exist?(python) && File.exist?(script)
      raise "Python 환경 또는 scraper.py를 찾을 수 없습니다."
    end

    safe_keyword = keyword.present? ? keyword.gsub(/[^a-zA-Z0-9\s\-_]/, "").truncate(100) : nil
    keyword_arg = safe_keyword ? "keyword=#{safe_keyword.to_json}" : "keyword=None"

    runner = PythonRunner.new
    output = runner.execute(<<~PYTHON)
      import sys, json
      sys.path.insert(0, '#{project_root}')
      from scraper import TechCrunchScraper

      scraper = TechCrunchScraper()
      try:
          urls = scraper.scrape_articles(limit=#{limit}, #{keyword_arg})
          articles = []
          for url in urls:
              data = scraper.extract_article_data(url)
              if data:
                  articles.append(data)
          print(json.dumps(articles))
      finally:
          scraper.quit()
    PYTHON

    articles = JSON.parse(output)
    count = 0
    articles.each do |data|
      next if Article.exists?(url: data["url"])
      Article.create!(
        title: data["title"],
        url: data["url"],
        content: data["content"],
        post_datetime: data["post_datetime"],
        image_url: data["image_url"],
        crawl_datetime: data["crawl_datetime"]
      )
      count += 1
    end
    count
  end

  private

  def project_root
    Rails.root.join("..").to_s
  end
end
