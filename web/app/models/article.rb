class Article < ApplicationRecord
  validates :url, presence: true, uniqueness: true

  scope :recent, -> { order(created_at: :desc) }

  def status
    if all_posted?
      :completed
    elsif any_posted?
      :partial
    else
      :pending
    end
  end

  def status_label
    case status
    when :completed then "완료"
    when :partial then "진행중"
    when :pending then "대기중"
    end
  end

  def all_posted?
    posted_to_telegram? && posted_to_instagram? && posted_to_x?
  end

  def any_posted?
    posted_to_telegram? || posted_to_instagram? || posted_to_x?
  end

  def translated?
    translated_title.present? && translated_content.present?
  end
end
