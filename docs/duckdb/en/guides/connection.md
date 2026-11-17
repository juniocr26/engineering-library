# duckdb — Query interface

Temporary reviewed partial model excerpt. Important contracts remain undocumented. Not approved for publication; source quotes and full review evidence are preserved separately.

Source revision: `e41515de6f7efb19b43293ab49cb967cd64ab9f9`.

## 1

The Connection class provides methods for querying and submitting queries to a database context. The Query method takes a query string and returns a QueryResult object, while the Submit method takes a query string and query parameters and returns a QueryResult object. The methods also support overloading for different parameter types.

Source: `src/main/connection.cpp:98`; SHA-256: `ab52da4dbde85ba40bda124b5e1368460870ac5b75333155c8d1f3c794a13700`.

    unique_ptr<QueryResult> Connection::Query(const string &query) {
    	return context->Query(query, QueryParameters());
    }
    
    unique_ptr<QueryResult> Connection::Query(unique_ptr<SQLStatement> statement, shared_ptr<ResultFormat> format) {
    	return context->Query(std::move(statement), std::move(format));
    }
    
    unique_ptr<QueryResult> Connection::Query(const string &query, shared_ptr<ResultFormat> format) {
    	return context->Query(query, std::move(format));
    }
    
    unique_ptr<QueryResult> Connection::Submit(const string &query, const QueryParameters &query_parameters) {
    	return context->Submit(query, query_parameters);
    }
    
    unique_ptr<QueryResult> Connection::Submit(unique_ptr<SQLStatement> statement,
                                               const QueryParameters &query_parameters) {
    	return context->Submit(std::move(statement), query_parameters);
    }
    
    unique_ptr<QueryResult> Connection::Submit(const string &query, shared_ptr<ResultFormat> format) {
    	return context->Submit(query, std::move(format));
    }
    
    unique_ptr<QueryResult> Connection::Submit(unique_ptr<SQLStatement> statement, shared_ptr<ResultFormat> format) {
    	return context->Submit(std::move(statement), std::move(format));


