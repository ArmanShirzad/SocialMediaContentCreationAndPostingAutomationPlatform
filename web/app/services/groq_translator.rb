class GroqTranslator
  API_URL = "https://api.groq.com/openai/v1/chat/completions"

  def initialize
    @api_key = ENV["GROQ_API_KEY"] || load_env_key("GROQ_API_KEY")
    raise "GROQ_API_KEY is not set" if @api_key.blank?
  end

  def translate(text)
    return nil if text.blank?

    call_api(
      "You are a professional translator. Translate the following English text to Korean. " \
      "Output ONLY the Korean translation, nothing else.",
      text
    )
  end

  def summarize(text, max_chars: 300)
    return nil if text.blank?

    call_api(
      "Summarize the following text in Korean for an Instagram post. " \
      "Keep it under #{max_chars} characters. Output ONLY the summary.",
      text
    )
  end

  private

  def call_api(system_prompt, user_content)
    uri = URI(API_URL)
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = true
    http.read_timeout = 30
    cert_path = %w[/etc/ssl/cert.pem /usr/local/etc/openssl@3/cert.pem].find { |p| File.exist?(p) }
    http.ca_file = cert_path if cert_path

    request = Net::HTTP::Post.new(uri)
    request["Authorization"] = "Bearer #{@api_key}"
    request["Content-Type"] = "application/json"
    request.body = {
      model: "llama-3.3-70b-versatile",
      messages: [
        { role: "system", content: system_prompt },
        { role: "user", content: user_content }
      ],
      temperature: 0.3,
      max_tokens: 2048
    }.to_json

    response = http.request(request)
    raise "Groq API error: #{response.code} #{response.body}" unless response.is_a?(Net::HTTPSuccess)

    data = JSON.parse(response.body)
    data.dig("choices", 0, "message", "content")&.strip
  end

  def load_env_key(key)
    env_path = Rails.root.join("..", ".env")
    return nil unless File.exist?(env_path)

    File.readlines(env_path).each do |line|
      line = line.strip
      next if line.empty? || line.start_with?("#")
      k, v = line.split("=", 2)
      return v if k == key
    end
    nil
  end
end
