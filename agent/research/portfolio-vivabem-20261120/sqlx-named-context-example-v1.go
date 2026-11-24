package examples

import "github.com/jmoiron/sqlx"

func BindWidget() (string, []interface{}, error) {
    return sqlx.Named("SELECT code FROM widgets WHERE id=:id", map[string]interface{}{"id": 7})
}
