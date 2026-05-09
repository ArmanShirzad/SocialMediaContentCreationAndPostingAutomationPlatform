require "net/http"
require "rss"

class GoogleNewsService
  BASE_URL = "https://news.google.com/rss/search"

  def search(keyword, limit: 20)
    uri = URI(BASE_URL)
    uri.query = URI.encode_www_form(
      q: keyword,
      hl: "ko",
      gl: "KR",
      ceid: "KR:ko"
    )

    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = true
    http.read_timeout = 15
    http.verify_mode = OpenSSL::SSL::VERIFY_PEER
    cert_path = ENV["SSL_CERT_FILE"] || %w[
      /etc/ssl/cert.pem
      /usr/local/etc/openssl/cert.pem
      /usr/local/etc/openssl@3/cert.pem
    ].find { |p| File.exist?(p) }
    http.ca_file = cert_path if cert_path

    response = http.get(uri.request_uri)
    raise "Google News 검색 실패: #{response.code}" unless response.is_a?(Net::HTTPSuccess)

    feed = RSS::Parser.parse(response.body, false)
    return [] unless feed

    feed.items.first(limit).map do |item|
      {
        title: clean_title(item.title),
        url: extract_real_url(item.link),
        source: extract_source(item.title),
        published_at: item.pubDate&.to_s,
        description: strip_html(item.description)
      }
    end
  end

  private

  def clean_title(title)
    title&.sub(/\s*-\s*[^-]+\z/, "")&.strip
  end

  def extract_source(title)
    match = title&.match(/\s*-\s*([^-]+)\z/)
    match ? match[1].strip : nil
  end

  def extract_real_url(google_url)
    return google_url unless google_url&.include?("news.google.com")

    uri = URI(google_url)
    params = URI.decode_www_form(uri.query || "")
    url_param = params.find { |k, _| k == "url" }
    url_param ? url_param[1] : google_url
  rescue
    google_url
  end

  def strip_html(html)
    return nil if html.blank?
    html.gsub(/<[^>]+>/, "").strip.truncate(300)
  end
end
