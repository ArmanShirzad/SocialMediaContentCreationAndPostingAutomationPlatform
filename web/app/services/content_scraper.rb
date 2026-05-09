require "net/http"
require "nokogiri"

class ContentScraper
  USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

  def scrape(url)
    uri = URI(url)
    response = fetch(uri)
    raise "페이지를 불러올 수 없습니다: #{response.code}" unless response.is_a?(Net::HTTPSuccess)

    doc = Nokogiri::HTML(response.body)

    {
      title: extract_title(doc),
      content: extract_content(doc),
      image_url: extract_image(doc, uri)
    }
  end

  private

  def fetch(uri, redirect_limit = 5)
    raise "리다이렉트 초과" if redirect_limit == 0

    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = uri.scheme == "https"
    http.read_timeout = 15
    cert_path = %w[/etc/ssl/cert.pem /usr/local/etc/openssl@3/cert.pem].find { |p| File.exist?(p) }
    http.ca_file = cert_path if cert_path

    request = Net::HTTP::Get.new(uri)
    request["User-Agent"] = USER_AGENT
    request["Accept"] = "text/html"

    response = http.request(request)

    if response.is_a?(Net::HTTPRedirection)
      location = response["location"]
      new_uri = location.start_with?("http") ? URI(location) : URI.join(uri, location)
      return fetch(new_uri, redirect_limit - 1)
    end

    response
  end

  def extract_title(doc)
    # Try og:title first, then <title>, then h1
    og = doc.at_css('meta[property="og:title"]')&.[]("content")
    return og.strip if og.present?

    h1 = doc.at_css("h1")&.text
    return h1.strip if h1.present?

    doc.at_css("title")&.text&.strip
  end

  def extract_content(doc)
    # Remove unwanted elements
    doc.css("script, style, nav, header, footer, aside, .ad, .advertisement, .sidebar, .comments, .related").remove

    # Try common article selectors
    selectors = [
      "article .entry-content",
      "article .post-content",
      ".article-body",
      ".story-body",
      "article",
      '[role="main"]',
      ".post-content",
      ".entry-content"
    ]

    content_node = nil
    selectors.each do |sel|
      node = doc.at_css(sel)
      if node
        content_node = node
        break
      end
    end

    content_node ||= doc.at_css("body")

    # Extract paragraphs
    paragraphs = content_node.css("p").map { |p| p.text.strip }.reject(&:blank?)
    paragraphs.join("\n\n").truncate(5000)
  end

  def extract_image(doc, base_uri)
    og = doc.at_css('meta[property="og:image"]')&.[]("content")
    return og if og.present?

    img = doc.at_css("article img")&.[]("src")
    return img if img.present?

    nil
  end
end
