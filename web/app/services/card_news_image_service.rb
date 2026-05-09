require "open3"

class CardNewsImageService
  def generate(article)
    output_dir = Rails.root.join("storage", "card_news")
    FileUtils.mkdir_p(output_dir)

    output_path = output_dir.join("card_#{article.id}_#{Time.current.to_i}.png").to_s

    data = {
      title: article.translated_title || article.title,
      summary: article.summary || article.translated_content&.truncate(200) || "",
      output_path: output_path,
      source: "ContentFlow",
      date: Date.today.strftime("%Y.%m.%d")
    }

    python = File.join(project_root, "venv", "bin", "python")
    script = File.join(project_root, "card_news_generator.py")

    raise "Python 환경을 찾을 수 없습니다." unless File.exist?(python)
    raise "card_news_generator.py를 찾을 수 없습니다." unless File.exist?(script)

    stdout, stderr, status = Open3.capture3(
      python, script, data.to_json,
      chdir: project_root
    )

    unless status.success?
      raise "이미지 생성 실패: #{stderr.presence || stdout}"
    end

    result = JSON.parse(stdout)
    raise "이미지 생성 실패: #{result['error']}" unless result["success"]

    output_path
  end

  private

  def project_root
    Rails.root.join("..").to_s
  end
end
