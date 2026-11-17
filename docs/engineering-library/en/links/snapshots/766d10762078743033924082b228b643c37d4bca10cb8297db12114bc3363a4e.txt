require "test_helper"

class HealthTest < ActionDispatch::IntegrationTest
  test "health responds without exposing database credentials" do
    get "/up"
    assert_response :success
    assert_not_includes response.body, ENV.fetch("POSTGRES_PASSWORD")
  end

  test "database accepts a query" do
    assert_equal 1, ActiveRecord::Base.connection.select_value("SELECT 1")
  end
end
