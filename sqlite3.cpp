#include "sqlite3.h"

#include <stdlib.h>
//template <typename value_type>
//static inline void assign(value_type& value, const char *src);
//{
//    abort();
//}

//template <>
static inline void assign(std::string &value, const char *src) 
{
    if ( src == NULL ) {
        src = "";
    }
    value = src;
}

//template <>
static inline void assign(int32_t &value, const char *src) 
{
    if ( src == NULL ) {
        value = 0;
        return ;
    }
    value = atoi(src);
}

//template <>
static inline void assign(int8_t &value, const char *src) 
{
    if ( src == NULL ) {
        value = 0;
        return ;
    }
    value = atoi(src);
}

//template <>
static inline void assign(int16_t &value, const char *src) 
{
    if ( src == NULL ) {
        value = 0;
        return ;
    }
    value = atoi(src);
}

//template <>
static inline void assign(int64_t &value, const char *src) 
{
    if ( src == NULL ) {
        value = 0;
        return ;
    }
    value = atoll(src);
}

//template <>
static inline void assign(float &value, const char *src)
{
    if ( src == NULL ) {
        value = 0.0f;
        return ;
    }
    value = atof(src);
}

//template <>
static inline void assign(double &value, const char *src)
{
    if ( src == NULL ) {
        value = 0.0;
        return ;
    }
    value = atof(src);
}

static inline void assign(type_info &ti, const char *src)
{
    if ( ti.type == type_info::integer ) {
        int *value = (int *)ti.data;
        sqlite3_generator::assign(*value, src);
    }
    else if ( ti.type == type_info::string ) {
        std::string *value = (std::string *)ti.data;
        sqlite3_generator::assign(*value, src);
    }
    else {
        assert(false);
    }
}

template <typename record_type>
bool sqlite3_wrap<record_type>::open(const char *name)
{
    bool ret = true;
    dbname = name;
    status = sqlite3_open(dbname, &db);
    if ( status ) {
        msg = (char *)sqlite3_errmsg(db);
        ret = false;
    }
    return ret;
}

template <typename record_type>
bool sqlite3_wrap<record_type>::exec(const char *sql, record_type *records)
{
    status = sqlite3_exec(db, sql, record_type::callback, records, &msg);
    return status == SQLITE_OK;
}

static inline int query_first_int_cb(void *priv, int count, char **values, char **cols)
{
    int *val = (int*)priv;
    *val = atoi(values[0]);
    return 0;
}
template <typename record_type>
bool sqlite3_wrap<record_type>::query_first_int(const char *sql, int *val)
{
    status = sqlite3_exec(db, sql, query_first_int_cb, val, &msg);
    return status == SQLITE_OK;
}

template <typename record_type>
void sqlite3_wrap<record_type>::close()
{
    if ( db ) {
        sqlite3_close(db);
        db = NULL;
        msg = NULL;
        status = SQLITE_OK;
    }
}

template <typename record_set>
int sqlite_record<record_set>::callback(void *priv, int count, char **values, char **cols)
{
    sqlite_record * self = (sqlite_record *)priv;
    record_set &records = self->get_record();
    typename record_set::value_type record;
    for ( int i = 0; i < count; i++ ) {
        // if ( values[i] == NULL ) {
        //     values[i] = (char *)"NULL";
        // }
        type_info ti = record.get_field(cols[i]);
        //record.assign(ti, values[i]);
        assign(ti, values[i]);
    }
    records.push_back(record);
    return 0;
}
