class AddPerformanceIndexes < ActiveRecord::Migration[8.1]
  def change
    add_index :articles, :posted_to_telegram
    add_index :articles, :posted_to_instagram
    add_index :articles, :posted_to_x
    add_index :articles, :translated_title
  end
end
