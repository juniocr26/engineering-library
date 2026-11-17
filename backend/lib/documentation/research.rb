# frozen_string_literal: true
require 'json'
require 'net/http'
require 'uri'
require 'resolv'
require 'ipaddr'
require 'timeout'
require 'digest'
require 'time'
require 'nokogiri'

module Documentation
  # Public technology references only. Never receives source code or chooses queries
  # from it. The explicitly configured local search provider is a separate boundary.
  class Research
    class Rejected < StandardError; end
    LIMIT = 524_288
    TECHNOLOGIES = ['Ruby', 'PHP', 'Go', 'Rust', 'Java', 'Spring Boot', 'FastAPI', 'Pydantic', 'Node.js', 'PostgreSQL', 'Docker', 'SearXNG', 'React', 'TypeScript', 'Laravel', 'Redis', 'RabbitMQ', 'OpenSSL', 'Python'].freeze
    PUBLIC_QUERY_WORDS = %w[documentation official reference api language configuration validation default defaults environment variables type types json schema serialization http https net ipaddr url uri client server timeout timeouts exception exceptions error errors handling retry retries database transaction transactions isolation filesystem atomic replacement rename concurrency uuid random identifiers units bytes binary enum enums record records fields nullable optional required security authentication version versions compatibility].freeze
    BLOCKED_V4 = %w[0.0.0.0/8 10.0.0.0/8 100.64.0.0/10 127.0.0.0/8 169.254.0.0/16 172.16.0.0/12 192.0.0.0/24 192.0.2.0/24 192.168.0.0/16 198.18.0.0/15 198.51.100.0/24 203.0.113.0/24 224.0.0.0/4 240.0.0.0/4].map { |s| IPAddr.new(s) }.freeze
    BLOCKED_V6 = %w[2001::/23 2001:db8::/32 2002::/16 3fff::/20].map { |s| IPAddr.new(s) }.freeze

    def initialize(env = ENV, prohibited: [])
      @mode = env.fetch('DOCS_RESEARCH', 'offline')
      raise Rejected, 'DOCS_RESEARCH must be offline, urls or search' unless %w[offline urls search].include?(@mode)
      @endpoint = env.fetch('DOCS_SEARCH_URL', 'http://research:8080/search')
      @prohibited = prohibited.reject { |s| s.to_s.size < 3 }
    end

    def public_ip?(address)
      ip = IPAddr.new(address)
      return false if ip.ipv4_mapped?
      if ip.ipv4?
        BLOCKED_V4.none? { |range| range.include?(ip) }
      else
        IPAddr.new('2000::/3').include?(ip) && BLOCKED_V6.none? { |range| range.include?(ip) }
      end
    rescue IPAddr::InvalidAddressError
      false
    end

    def validate_url(value, hosts = [])
      raise Rejected, 'URL too long' unless value.is_a?(String) && value.bytesize <= 2048
      uri = URI.parse(value)
      raise Rejected, 'public HTTP(S) URL required' unless %w[http https].include?(uri.scheme) && uri.host && !uri.userinfo && !uri.fragment
      raise Rejected, 'only standard public HTTP(S) ports allowed' unless uri.port == (uri.scheme == 'https' ? 443 : 80)
      host = uri.hostname.downcase
      raise Rejected, 'unsafe hostname' if host.include?('%') || host.end_with?('.') || host == 'localhost' || host.end_with?('.local', '.internal', '.localhost')
      raise Rejected, 'URL outside approved primary-source hosts' unless hosts.empty? || hosts.include?(host)
      addresses = resolve(host)
      raise Rejected, 'DNS has no exclusively public addresses' if addresses.empty? || addresses.any? { |a| !public_ip?(a) }
      [uri, addresses.first]
    rescue URI::InvalidURIError => e
      raise Rejected, e.message
    end

    def resolve(host)
      Timeout.timeout(3) { Resolv.getaddresses(host) }
    end

    def request(uri, address, max_bytes: LIMIT)
      http = Net::HTTP.new(uri.hostname, uri.port, nil) # Do not inherit proxy credentials.
      http.ipaddr = address # Pin the validated IP; TLS still verifies the URL hostname.
      http.use_ssl = uri.scheme == 'https'
      http.open_timeout = 5
      http.read_timeout = 10
      http.write_timeout = 5
      req = Net::HTTP::Get.new(uri.request_uri)
      req['User-Agent'] = 'LocalDocumentationResearch/1.0'
      req['Accept'] = 'text/html,text/plain,application/json'
      req['Accept-Encoding'] = 'identity'
      data = +''.b
      result = nil
      Timeout.timeout(20) do
        http.request(req) do |response|
          response.read_body do |chunk|
            data << chunk
            raise Rejected, 'research response exceeds byte limit' if data.bytesize > max_bytes
          end
          result = { status: response.code.to_i, headers: response.to_hash, body: data }
        end
      end
      result
    end

    def fetch(url, hosts: [], terms: [])
      current = url
      3.times do |redirect|
        uri, address = validate_url(current, hosts)
        response = request(uri, address)
        if [301, 302, 303, 307, 308].include?(response[:status])
          raise Rejected, 'redirect limit exceeded' if redirect == 2
          location = response[:headers].fetch('location', []).first
          raise Rejected, 'redirect without location' unless location
          current = URI.join(uri, location).to_s
          next
        end
        raise Rejected, "public source HTTP #{response[:status]}" unless response[:status] == 200
        type = response[:headers].fetch('content-type', ['']).first.split(';').first
        raise Rejected, 'unsupported source content type' unless %w[text/html text/plain].include?(type)
        text = response[:body].dup.force_encoding('UTF-8')
        raise Rejected, 'non-UTF-8 source' unless text.valid_encoding?
        if type == 'text/html'
          document = Nokogiri::HTML(text)
          document.css('script,style,noscript,nav,header,footer,form,[hidden],[aria-hidden="true"]').remove
          title = document.at_css('title')&.text.to_s.strip[0, 160]
          main = document.at_css('main,article,[role="main"]') || document
          paragraphs = main.css('p,pre').map(&:text)
        else
          title = uri.hostname
          paragraphs = text.split(/\n\s*\n/)
        end
        terms = terms.join(' ').downcase.scan(/[a-z0-9.]{3,}/).uniq
        paragraphs = paragraphs.map { |p| p.gsub(/\s+/, ' ').strip }.select { |p| p.size >= 40 }
        paragraphs = paragraphs.sort_by { |p| -terms.count { |term| p.downcase.include?(term) } }
        # Minimal excerpts, not full page copies. At most 100 words per source.
        excerpt = paragraphs.first(2).join(' ').split(/\s+/).first(100).join(' ')[0, 800]
        raise Rejected, 'empty public source passage' if excerpt.empty?
        return { 'url' => uri.to_s, 'consulted_at' => Time.now.utc.iso8601, 'title' => title,
          'passage' => excerpt, 'passage_sha256' => Digest::SHA256.hexdigest(excerpt),
          'evidence_kind' => 'untrusted public technology reference; not local implementation proof' }
      end
    end

    def validate_query(query, technology, version)
      raise Rejected, 'explicit technology and version required' unless [technology, version].all? { |v| v.is_a?(String) && (1..80).cover?(v.size) }
      raise Rejected, 'query must be bounded public technology text' unless query.is_a?(String) && (5..160).cover?(query.size) && query.match?(/\A[a-zA-Z0-9 .:+?()_-]+\z/)
      raise Rejected, 'query must name its technology and version' unless [technology, version].all? { |v| query.downcase.include?(v.downcase) }
      raise Rejected, 'private identifier or path in query' if @prohibited.any? { |v| query.downcase.include?(v.downcase) } || query.match?(/secret|password|credential|bearer|localhost|127\.0\.|metadata|[A-Za-z0-9_-]{40,}/i)
      raise Rejected, 'technology is not in the reviewed public research vocabulary' unless TECHNOLOGIES.any? { |value| value.casecmp?(technology) }
      raise Rejected, 'version must be a public semantic version' unless version.match?(/\A\d{1,4}(?:\.\d{1,4}){0,2}(?:-(?:alpha|beta|rc)(?:\.\d{1,3})?)?\z/)
      allowed = PUBLIC_QUERY_WORDS + technology.downcase.split + [version.downcase]
      raise Rejected, 'query contains unapproved terms; use public technology/version/topic words only' unless query.downcase.split.all? { |word| allowed.include?(word) }
      query
    end

    def search(query)
      uri = URI.parse(@endpoint)
      raise Rejected, 'search endpoint must be the explicitly configured local research service' unless uri.scheme == 'http' && uri.host == 'research' && uri.port == 8080 && uri.path == '/search' && !uri.userinfo && !uri.query && !uri.fragment
      uri.query = URI.encode_www_form(q: query, format: 'json', categories: 'general', safesearch: 1)
      # Local provider is operator-configured, not a public fetch or model-chosen URL.
      address = resolve(uri.hostname).first
      raise Rejected, 'local search service unavailable' unless address
      response = request(uri, address, max_bytes: 131_072)
      raise Rejected, "search HTTP #{response[:status]}" unless response[:status] == 200
      data = JSON.parse(response[:body])
      { 'urls' => data.fetch('results').first(8).filter_map { |r| r['url'] if r.is_a?(Hash) },
        'upstream_errors' => data.fetch('unresponsive_engines', []) }
    end

    def collect(settings)
      return { 'mode' => @mode, 'status' => 'offline', 'references' => [], 'warnings' => [] } if @mode == 'offline'
      warnings = []
      settings ||= {}
      technology, version = settings.values_at('technology', 'version')
      hosts = settings.fetch('primary_hosts', [])
      raise Rejected, 'primary_hosts must be a bounded hostname list' unless hosts.is_a?(Array) && hosts.size <= 8 && hosts.all? { |h| h.is_a?(String) && h.match?(/\A[a-z0-9.-]+\z/) }
      urls = settings.fetch('urls', []).dup
      raise Rejected, 'at most two explicit source URLs' unless urls.is_a?(Array) && urls.size <= 2
      if !urls.empty? || settings['query']
        raise Rejected, 'explicit public technology and version required' unless [technology, version].all? { |v| v.is_a?(String) && (1..80).cover?(v.size) && v.match?(/\A[a-zA-Z0-9 ._+-]+\z/) }
      end
      search_status = 'not-requested'
      if @mode == 'search' && settings['query']
        query = validate_query(settings['query'], technology, version)
        begin
          result = search(query)
          search_status = 'completed'
          warnings << { 'kind' => 'search-upstream-errors', 'details' => result['upstream_errors'] } unless result['upstream_errors'].empty?
          urls.concat(result['urls'].select { |url| hosts.include?(URI.parse(url).hostname) rescue false })
          warnings << { 'kind' => 'no-approved-search-results' } if urls.empty?
        rescue StandardError => error
          search_status = 'unavailable'
          warnings << { 'kind' => 'search-unavailable', 'error' => error.message }
        end
      end
      references = []
      maximum = settings.fetch('max_sources', 2)
      raise Rejected, 'max_sources must be 1 or 2' unless [1, 2].include?(maximum)
      urls.uniq.first(4).each do |url|
        break if references.size == maximum
        begin
          ref = fetch(url, hosts: hosts, terms: [technology, version, settings['query']].compact)
          expected = settings['version_pattern']
          if expected && !ref.values_at('url', 'title', 'passage').join(' ').include?(expected)
            warnings << { 'kind' => 'version-mismatch', 'url' => ref['url'], 'expected' => expected }
            next
          end
          references << ref.merge('id' => "W#{references.size + 1}", 'technology' => technology, 'requested_version' => version)
        rescue StandardError => error
          warnings << { 'kind' => 'source-rejected', 'url' => url, 'error' => error.message }
        end
      end
      { 'mode' => @mode, 'status' => references.empty? ? 'degraded' : 'available', 'search_status' => search_status,
        'query' => @mode == 'search' ? settings['query'] : nil, 'references' => references, 'warnings' => warnings }
    end
  end
end
