Rails.application.configure do
  config.content_security_policy do |policy|
    policy.default_src :self
    policy.font_src    :self, "https://cdn.jsdelivr.net", "https://fonts.gstatic.com", "https://fonts.googleapis.com"
    policy.img_src     :self, :https, :data
    policy.object_src  :none
    policy.script_src  :self
    policy.style_src   :self, :unsafe_inline, "https://cdn.jsdelivr.net", "https://fonts.googleapis.com"
    policy.frame_ancestors :none
    policy.base_uri    :self
    policy.form_action :self
  end
end
