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

ActiveRecord::Schema[8.1].define(version: 2026_10_19_020000) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "bookmarks", force: :cascade do |t|
    t.string "reader_digest", limit: 64, null: false
    t.string "project", limit: 100, null: false
    t.string "document", limit: 240, null: false
    t.string "language", limit: 5, null: false
    t.string "anchor", limit: 200, null: false
    t.string "excerpt", limit: 240, default: "", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["reader_digest", "project", "document", "language", "anchor"], name: "bookmarks_logical_location", unique: true
    t.check_constraint "language::text = ANY (ARRAY['en'::character varying, 'pt-BR'::character varying]::text[])", name: "bookmarks_language"
    t.check_constraint "reader_digest::text ~ '^[0-9a-f]{64}$'::text", name: "bookmarks_reader_digest"
  end

  create_table "catalog_projects", force: :cascade do |t|
    t.string "stable_id", null: false
    t.string "slug", null: false
    t.string "display_name", null: false
    t.boolean "active", default: true, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index "lower((display_name)::text) COLLATE \"C\", stable_id", name: "catalog_projects_order", where: "active"
    t.index ["slug"], name: "index_catalog_projects_on_slug", unique: true
    t.index ["stable_id"], name: "index_catalog_projects_on_stable_id", unique: true
  end

  create_table "highlights", force: :cascade do |t|
    t.string "reader_digest", limit: 64, null: false
    t.string "project", limit: 100, null: false
    t.string "document", limit: 240, null: false
    t.string "language", limit: 5, null: false
    t.string "color", null: false
    t.jsonb "segments", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["reader_digest", "project", "document", "language"], name: "highlights_document_scope"
    t.check_constraint "color::text = ANY (ARRAY['yellow'::character varying, 'blue'::character varying, 'pink'::character varying, 'orange'::character varying, 'purple'::character varying, 'red'::character varying, 'green'::character varying]::text[])", name: "highlights_color"
    t.check_constraint "jsonb_typeof(segments) = 'array'::text AND jsonb_array_length(segments) >= 1 AND jsonb_array_length(segments) <= 32", name: "highlights_segments"
    t.check_constraint "language::text = ANY (ARRAY['en'::character varying, 'pt-BR'::character varying]::text[])", name: "highlights_language"
    t.check_constraint "reader_digest::text ~ '^[0-9a-f]{64}$'::text", name: "highlights_reader_digest"
  end

  create_table "notes", force: :cascade do |t|
    t.string "reader_digest", limit: 64, null: false
    t.string "project", limit: 100, null: false
    t.string "document", limit: 240, null: false
    t.string "language", limit: 5, null: false
    t.jsonb "segments", null: false
    t.string "anchor_digest", limit: 64, null: false
    t.bigint "highlight_id"
    t.text "body", null: false
    t.string "demo_key"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["highlight_id"], name: "index_notes_on_highlight_id", unique: true
    t.index ["reader_digest", "demo_key"], name: "index_notes_on_reader_digest_and_demo_key", unique: true, where: "(demo_key IS NOT NULL)"
    t.index ["reader_digest", "project", "document", "language", "anchor_digest"], name: "notes_logical_location", unique: true
    t.check_constraint "language::text = ANY (ARRAY['en'::character varying, 'pt-BR'::character varying]::text[])", name: "notes_language"
    t.check_constraint "octet_length(body) <= 131072", name: "notes_body_size"
    t.check_constraint "reader_digest::text ~ '^[0-9a-f]{64}$'::text", name: "notes_reader_digest"
  end

  add_foreign_key "notes", "highlights", on_delete: :nullify
end
