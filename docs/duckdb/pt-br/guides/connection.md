# duckdb — Interface de consultas

Trecho parcial temporário do modelo, revisado. Contratos importantes continuam sem documentação. Sem aprovação de publicação; citações do código e evidências completas da revisão ficam preservadas separadamente.

Revisão de origem: `e41515de6f7efb19b43293ab49cb967cd64ab9f9`.

## 1

A classe Connection fornece métodos para consultar e enviar consultas de banco de dados. O método Query recebe uma string de consulta e retorna um objeto QueryResult, enquanto o método Submit recebe uma string de consulta e parâmetros de consulta e retorna um objeto QueryResult. Os métodos também suportam sobrecarga para diferentes tipos de parâmetros.

Fonte: `src/main/connection.cpp:98`; SHA-256: `ab52da4dbde85ba40bda124b5e1368460870ac5b75333155c8d1f3c794a13700`.

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


