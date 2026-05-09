class ScrapeJob < ApplicationJob
  queue_as :default

  def perform(keyword: nil)
    service = ScraperService.new
    service.run(keyword: keyword)
  end
end
