namespace :catalog do
  desc "Synchronize the PostgreSQL metadata index from bilingual Markdown bios"
  task sync: :environment do
    puts Catalog::Sync.call.inspect
  end
end
