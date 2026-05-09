ENV["RAILS_ENV"] ||= "test"
require_relative "../config/environment"
require "rails/test_help"

module ActiveSupport
  class TestCase
    parallelize(workers: :number_of_processors)

    fixtures :all
  end
end

class ActionDispatch::IntegrationTest
  def auth_headers
    credentials = ActionController::HttpAuthentication::Basic.encode_credentials("admin", "changeme")
    { "HTTP_AUTHORIZATION" => credentials }
  end

  def get(path, **opts)
    opts[:headers] = (opts[:headers] || {}).merge(auth_headers)
    super
  end

  def post(path, **opts)
    opts[:headers] = (opts[:headers] || {}).merge(auth_headers)
    super
  end

  def patch(path, **opts)
    opts[:headers] = (opts[:headers] || {}).merge(auth_headers)
    super
  end
end
