#ifndef HW3_TABLES_H
#define HW3_TABLES_H

#ifdef __cplusplus
extern "C" {
#endif

struct pair {
    char *key;
    char *value;
};

struct list {
    struct list *next;
    struct pair entry;
};

struct HashTable {
    int size;
    int count;
    struct list **table;
};

struct triple {
    char *category;
    int index;
    char *token;
};

/* FIX: declarations live in the header; definitions are in tables.c. */
struct HashTable* initHashTable(int size);
void destroyHashTable(struct HashTable *table);
int hash(const char *str, int table_size);
char* get(const struct HashTable *table, const char *key);
int put(struct HashTable *table, const char *key, const char *value);
int resizeHashTable(struct HashTable *table, int new_size);
int removeKey(struct HashTable *table, const char *key);
int writeTables(const struct HashTable *table, const char *filename);
char *concatStrings(const char *first, const char *second);

extern struct triple pif[1000];
extern int pif_index;

#ifdef __cplusplus
}
#endif

#endif
