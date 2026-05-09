articles = [
  {
    title: "OpenAI Announces GPT-5 with Major Enterprise Pricing Cuts",
    url: "https://techcrunch.com/2026/05/09/openai-gpt5-enterprise",
    content: "OpenAI is set to launch GPT-5 with significant API price reductions for enterprise customers.",
    translated_title: "OpenAI, GPT-5 출시 앞두고 기업용 API 가격 인하 발표",
    translated_content: "OpenAI가 GPT-5 모델 공식 출시를 앞두고 기업 고객을 위한 API 가격을 최대 30% 인하한다고 밝혔다.",
    summary: "OpenAI가 GPT-5 출시와 함께 기업용 API 가격을 30% 인하합니다.",
    posted_to_telegram: true,
    posted_to_instagram: true,
    posted_to_x: true
  },
  {
    title: "Apple Unveils M5 Chip with 40% Performance Boost",
    url: "https://techcrunch.com/2026/05/09/apple-m5-chip",
    content: "Apple has announced its next-generation M5 chip promising 40% better performance.",
    translated_title: "Apple, 차세대 M5 칩 발표... 성능 40% 향상",
    translated_content: "Apple이 차세대 M5 칩을 공개했다. 전작 대비 40% 향상된 성능을 자랑한다.",
    summary: "Apple M5 칩, 전작 대비 40% 성능 향상으로 맥북 프로 라인업 강화.",
    posted_to_telegram: false,
    posted_to_instagram: true,
    posted_to_x: false
  },
  {
    title: "Stripe Officially Enters Korean Market with KakaoPay Partnership",
    url: "https://techcrunch.com/2026/05/08/stripe-korea-kakaopay",
    content: "Stripe has officially launched in South Korea through a partnership with KakaoPay.",
    translated_title: "Stripe, 한국 시장 공식 진출... 카카오페이와 제휴",
    translated_content: "Stripe가 카카오페이와의 전략적 제휴를 통해 한국 시장에 공식 진출했다.",
    posted_to_telegram: true,
    posted_to_instagram: true,
    posted_to_x: false
  },
  {
    title: "Google Cloud Expands Generative AI Startup Investment Program",
    url: "https://techcrunch.com/2026/05/08/google-cloud-ai-startups",
    content: "Google Cloud is expanding its investment program for generative AI startups.",
    posted_to_telegram: false,
    posted_to_instagram: false,
    posted_to_x: false
  },
  {
    title: "Tesla Robotaxi Begins Trial Runs in Austin",
    url: "https://techcrunch.com/2026/05/07/tesla-robotaxi-austin",
    content: "Tesla has started trial runs of its robotaxi service in Austin, Texas.",
    translated_title: "테슬라 로보택시, 오스틴에서 시범 운행 개시",
    translated_content: "테슬라가 텍사스 오스틴에서 로보택시 서비스 시범 운행을 시작했다.",
    summary: "테슬라 로보택시가 오스틴에서 시범 운행을 시작했습니다.",
    posted_to_telegram: true,
    posted_to_instagram: true,
    posted_to_x: true
  }
]

articles.each do |attrs|
  Article.find_or_create_by!(url: attrs[:url]) do |a|
    a.assign_attributes(attrs.merge(crawl_datetime: Time.current))
  end
end

puts "Seeded #{Article.count} articles"
