class SettingsController < ApplicationController
  ALLOWED_KEYS = %w[
    GROQ_API_KEY PEXELS_API_KEY
    INSTAGRAM_USERNAME INSTAGRAM_PASSWORD
    TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID
    X_BEARER_TOKEN X_API_KEY X_API_KEY_SECRET X_ACCESS_TOKEN X_ACCESS_TOKEN_SECRET
  ].freeze

  SECRET_KEYS = %w[
    GROQ_API_KEY PEXELS_API_KEY INSTAGRAM_PASSWORD
    TELEGRAM_BOT_TOKEN X_BEARER_TOKEN X_API_KEY X_API_KEY_SECRET
    X_ACCESS_TOKEN X_ACCESS_TOKEN_SECRET
  ].freeze

  def show
    @settings = load_settings
  end

  def update
    write_settings(params[:settings])
    redirect_to settings_path, notice: "설정이 저장되었습니다."
  end

  private

  def env_path
    Rails.root.join("..", ".env").to_s
  end

  def mask_value(key, value)
    return value if value.blank?
    return value unless SECRET_KEYS.include?(key)

    value.length > 8 ? "#{"*" * (value.length - 4)}#{value[-4..]}" : "*" * value.length
  end

  def load_settings
    path = env_path
    return {} unless File.exist?(path)

    raw = File.readlines(path).each_with_object({}) do |line, hash|
      line = line.strip
      next if line.empty? || line.start_with?("#")
      key, value = line.split("=", 2)
      hash[key] = value if key && value && ALLOWED_KEYS.include?(key)
    end

    raw.transform_values.with_index { |v, _| v }
    raw.each_with_object({}) do |(k, v), h|
      h[k] = { value: v, masked: mask_value(k, v) }
    end
  end

  def write_settings(new_settings)
    return unless new_settings.is_a?(ActionController::Parameters) || new_settings.is_a?(Hash)

    path = env_path
    lines = File.exist?(path) ? File.readlines(path) : []

    new_settings.each do |key, value|
      key = key.to_s.strip
      next unless ALLOWED_KEYS.include?(key)
      value = value.to_s.strip
      next if value.empty? || value.match?(/\A\*+\w{0,4}\z/)

      found = false
      lines.map! do |line|
        if line.strip.start_with?("#{key}=") || line.strip.start_with?("# #{key}=")
          found = true
          "#{key}=#{value}\n"
        else
          line
        end
      end

      lines << "#{key}=#{value}\n" unless found
    end

    File.write(path, lines.join)
  end
end
