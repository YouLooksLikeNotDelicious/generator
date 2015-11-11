#ifndef __SQLITE3_H__INCLUDED__
#define __SQLITE3_H__INCLUDED__

#include <sqlite3.h>
#include <string>
#include <cassert>

namespace sqlite3_generator {

struct type_info {
    enum data_type{integer, string};
    void *data;
    data_type type;
};

class base_column {
public:
    // virtual type_info get_field(const std::string &key_name) = 0;
    //void assign(type_info &ti, const char *src);
};

template <typename record_type>
class sqlite3_wrap {
typedef int (*callback)(void *, int, char **, char **);
public:
    sqlite3_wrap()
    : db(NULL), dbname(NULL), status(SQLITE_OK), msg(NULL) {}

    sqlite3_wrap(const char *name)
    : db(NULL), dbname(name), status(SQLITE_OK), msg(NULL)
    {
        open(name);
    }

    sqlite3_wrap(sqlite3 *db, const char *name = NULL)
    :db(db), dbname(name), status(SQLITE_OK), msg(NULL) {}

    ~sqlite3_wrap()
    {
        //close();
    }

    bool open(const char *name);

    bool exec(const char *sql, record_type *records);
    bool query_first_int(const char *sql, int *val);

    void close();

    const char* get_err_msg()
    {
        return msg;
    }

private:
    sqlite3 *db;
    const char *dbname;
    int status;
    char *msg;
};

template <typename record_set>
class sqlite_record {
public:
    static int callback(void *priv, int count, char **values, char **cols);

    record_set & get_record()
    {
        return records;
    }

private:
    record_set records;
};

#include "sqlite3.cpp"

#define column_set_type_init(column_type, column_set_type) typedef std::vector<column_type> column_set_type
#define sqlite_record_type_init(column_type, sqlite_record_type) typedef sqlite_record<std::vector<column_type>> sqlite_record_type
#define sqlite_wrap_type_init(column_type, sqlite_wrap_type) typedef sqlite3_wrap<sqlite_record<std::vector<column_type>>> sqlite_wrap_type
}

#endif
