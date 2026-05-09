class CreateArticles < ActiveRecord::Migration[8.1]
  def change
    create_table :articles do |t|
      t.string :title
      t.string :url
      t.text :content
      t.string :translated_title
      t.text :translated_content
      t.text :summary
      t.datetime :post_datetime
      t.string :image_url
      t.datetime :crawl_datetime
      t.boolean :posted_to_telegram, default: false
      t.boolean :posted_to_instagram, default: false
      t.boolean :posted_to_x, default: false

      t.timestamps
    end

    add_index :articles, :url, unique: true
  end
end
