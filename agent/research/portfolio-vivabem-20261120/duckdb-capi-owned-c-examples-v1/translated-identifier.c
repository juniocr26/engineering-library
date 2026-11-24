#include "duckdb.h"
duckdb_state query_with_cleanup(duckdb_connection connection, const char *query) {
    duckdb_result result = {0};
    duckdb_state state = duckdb_query(connection, query, &result);
    if (state == DuckDBError) {
        const char *borrowed = duckdb_result_erro(&result);
        (void)borrowed;
    }
    duckdb_destroy_result(&result);
    return state;
}
