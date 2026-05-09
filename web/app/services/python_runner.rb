require "open3"

class PythonRunner
  def execute(script)
    python = File.join(project_root, "venv", "bin", "python")
    raise "Python venv not found at #{python}" unless File.exist?(python)

    stdout, stderr, status = Open3.capture3(
      { "PYTHONPATH" => project_root },
      python, "-c", script,
      chdir: project_root
    )

    unless status.success?
      raise "Python error: #{stderr.presence || stdout}"
    end

    stdout.strip
  end

  def post(article, platform)
    script = build_post_script(article, platform)
    output = execute(script)
    { success: true, output: output }
  rescue => e
    { success: false, error: e.message }
  end

  private

  def project_root
    Rails.root.join("..").to_s
  end

  def build_post_script(article, platform)
    case platform
    when "telegram"
      <<~PYTHON
        import sys, json, asyncio
        sys.path.insert(0, '#{project_root}')
        from dotenv import load_dotenv
        load_dotenv('#{project_root}/.env')
        from telegram_poster import TelegramPoster

        async def post():
            poster = TelegramPoster()
            result = await poster.post_to_channel(
                title=#{article.translated_title.to_json},
                content=#{article.translated_content.to_json},
                image_url=#{article.image_url.to_json}
            )
            print(json.dumps({"success": result is not None}))

        asyncio.run(post())
      PYTHON
    when "instagram"
      <<~PYTHON
        import sys, json
        sys.path.insert(0, '#{project_root}')
        from dotenv import load_dotenv
        load_dotenv('#{project_root}/.env')
        print(json.dumps({"success": True, "message": "Instagram posting requires manual queue"}))
      PYTHON
    when "x"
      <<~PYTHON
        import sys, json
        sys.path.insert(0, '#{project_root}')
        from dotenv import load_dotenv
        load_dotenv('#{project_root}/.env')
        from test_x_posting import XPoster

        poster = XPoster()
        text = #{(article.translated_title.to_s + "\n\n" + (article.summary || article.translated_content.to_s).truncate(200)).to_json}
        result = poster.post_tweet_with_image(text=text, image_path=None)
        print(json.dumps({"success": result}))
      PYTHON
    end
  end
end
