class ApplicationController < ActionController::Base
  include Pagy::Backend

  http_basic_authenticate_with(
    name: ENV.fetch("ADMIN_USER", "admin"),
    password: ENV.fetch("ADMIN_PASSWORD", "changeme"),
    realm: "ContentFlow"
  )

  # Only allow modern browsers supporting webp images, web push, badges, import maps, CSS nesting, and CSS :has.
  allow_browser versions: :modern

  # Changes to the importmap will invalidate the etag for HTML responses
  stale_when_importmap_changes
end
