require 'json'
require 'ripper'
require 'digest'
class ResearchParser < Ripper::SexpBuilderPP
  attr_reader :diagnostics
  def initialize(source, name)
    @diagnostics = []
    super(source, name)
  end
  def on_parse_error(message)
    @diagnostics << { 'line' => lineno, 'column' => column, 'message' => message }
  end
end
source = File.binread(ARGV.fetch(0)).force_encoding(Encoding::UTF_8)
parser = ResearchParser.new(source, 'public-actionpack-request.rb')
sexp = parser.parse
names = %w[request_method request_method_symbol method method_symbol check_method]
selected = Hash[names.map { |name| [name, []] }]
walk = lambda do |node|
  if node.is_a?(Array)
    if node[0] == :def && names.include?(node[1][1])
      selected[node[1][1]] << node
    end
    node.each { |child| walk.call(child) if child.is_a?(Array) }
  end
end
walk.call(sexp) if sexp
valid = !sexp.nil? && parser.diagnostics.empty? && selected.values.all? { |items| items.length == 1 }
puts JSON.generate({
  'ruby_description' => RUBY_DESCRIPTION, 'ripper_version' => Ripper::Version,
  'source_sha256' => Digest::SHA256.hexdigest(source),
  'status' => valid ? 'PARSED_FULL_FILE_SELECTED_METHODS' : 'INCONCLUSIVE_SYNTAX_OR_SELECTION',
  'diagnostics' => parser.diagnostics,
  'selected_method_counts' => Hash[selected.map { |name, items| [name, items.length] }],
  'selected_method_nodes' => valid ? selected : {},
  'full_file_sexp' => valid ? sexp : nil,
  'target_source_loaded_or_executed' => false,
  'scope' => 'Full public source parsed as data; no Rails/gemspec require, eval, server, request-method or app/test execution. Ruby2.6 parser profile does not validate actionpack runtime compatibility.'
})
