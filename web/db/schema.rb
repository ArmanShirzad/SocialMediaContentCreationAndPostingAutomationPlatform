# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2026_05_09_021826) do
  create_table "articles", force: :cascade do |t|
    t.text "content"
    t.datetime "crawl_datetime"
    t.datetime "created_at", null: false
    t.string "image_url"
    t.datetime "post_datetime"
    t.boolean "posted_to_instagram", default: false
    t.boolean "posted_to_telegram", default: false
    t.boolean "posted_to_x", default: false
    t.text "summary"
    t.string "title"
    t.text "translated_content"
    t.string "translated_title"
    t.datetime "updated_at", null: false
    t.string "url"
    t.index ["url"], name: "index_articles_on_url", unique: true
  end
end
