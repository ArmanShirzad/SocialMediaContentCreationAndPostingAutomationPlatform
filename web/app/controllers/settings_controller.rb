class SettingsController < ApplicationController
  def show
    @env_file = env_path
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

  def load_settings
    path = env_path
    return {} unless File.exist?(path)

    File.readlines(path).each_with_object({}) do |line, hash|
      line = line.strip
      next if line.empty? || line.start_with?("#")
      key, value = line.split("=", 2)
      hash[key] = value if key && value
    end
  end

  def write_settings(new_settings)
    return unless new_settings.is_a?(ActionController::Parameters) || new_settings.is_a?(Hash)

    path = env_path
    lines = File.exist?(path) ? File.readlines(path) : []
    updated_keys = []

    new_settings.each do |key, value|
      key = key.to_s.strip
      next if key.empty?
      value = value.to_s.strip

      found = false
      lines.map! do |line|
        if line.strip.start_with?("#{key}=") || line.strip.start_with?("# #{key}=")
          found = true
          "#{key}=#{value}\n"
        else
          line
        end
      end

      unless found
        lines << "#{key}=#{value}\n"
      end
      updated_keys << key
    end

    File.write(path, lines.join)
  end
end
