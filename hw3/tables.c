#include "tables.h"

#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct triple pif[1000];
int pif_index = 0;

static char *copy_string(const char *str) {
    size_t length = strlen(str) + 1;
    char *copy = malloc(length);
    if (copy != NULL) {
        memcpy(copy, str, length);
    }
    return copy;
}

static int write_csv_field(FILE *file, const char *value) {
    if (fputc('"', file) == EOF) {
        return -1;
    }

    while (*value != '\0') {
        if (*value == '"' && fputc('"', file) == EOF) {
            return -1;
        }
        if (fputc(*value++, file) == EOF) {
            return -1;
        }
    }

    return fputc('"', file) == EOF ? -1 : 0;
}

static int write_symbol_table(FILE *file, const struct HashTable *table) {
    int result = 0;
    if (fputs("SYMBOL TABLE\n", file) == EOF ||
        fputs("\"Key\",\"Value\"\n", file) == EOF) {
        return -1;
    }

    for (int i = 0; result == 0 && i < table->size; i++) {
        for (const struct list *entry = table->table[i];
             entry != NULL;
             entry = entry->next) {
            if (entry->entry.key == NULL || entry->entry.value == NULL ||
                write_csv_field(file, entry->entry.key) != 0 ||
                fputc(',', file) == EOF ||
                write_csv_field(file, entry->entry.value) != 0 ||
                fputc('\n', file) == EOF) {
                result = -1;
                break;
            }
        }
    }

    return result;
}

static int write_pif_table(FILE *file) {
    if (pif_index < 0 || pif_index > (int)(sizeof pif / sizeof pif[0])) {
        return -1;
    }

    int result = 0;
    if (fputs("PIF TABLE\n", file) == EOF ||
        fputs("\"Position\",\"Category\",\"Index\",\"Token\"\n", file) == EOF) {
        return -1;
    }

    for (int i = 0; result == 0 && i < pif_index; i++) {
        if (pif[i].category == NULL || pif[i].token == NULL ||
            fprintf(file, "%d,", i) < 0 ||
            write_csv_field(file, pif[i].category) != 0 ||
            fprintf(file, ",%d,", pif[i].index) < 0 ||
            write_csv_field(file, pif[i].token) != 0 ||
            fputc('\n', file) == EOF) {
            result = -1;
        }
    }

    return result;
}

/* FIX: write both labeled tables through one open file. */
int writeTables(const struct HashTable *table, const char *filename) {
    if (table == NULL || table->table == NULL || table->size <= 0 ||
        filename == NULL) {
        return -1;
    }

    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        return -1;
    }

    int result = write_symbol_table(file, table);
    if (result == 0 && fputc('\n', file) == EOF) {
        result = -1;
    }
    if (result == 0) {
        result = write_pif_table(file);
    }
    if (fclose(file) != 0) {
        result = -1;
    }
    return result;
}

/* FIX: allocate one table and a zero-initialized bucket array, checking failures. */
struct HashTable* initHashTable(int size) {
    if (size <= 0 || (size_t)size > SIZE_MAX / sizeof(struct list *)) {
        return NULL;
    }

    struct HashTable *table = malloc(sizeof *table);
    if (table == NULL) {
        return NULL;
    }

    table->table = calloc((size_t)size, sizeof *table->table);
    if (table->table == NULL) {
        free(table);
        return NULL;
    }

    table->size = size;
    table->count = 0;
    return table;
}

/* FIX: rehash existing nodes into a new bucket array without reallocating entries. */
int resizeHashTable(struct HashTable *table, int new_size) {
    if (table == NULL || table->table == NULL || new_size <= 0 ||
        (size_t)new_size > SIZE_MAX / sizeof *table->table) {
        return -1;
    }

    struct list **new_table = calloc((size_t)new_size, sizeof *new_table);
    if (new_table == NULL) {
        return -1;
    }

    for (int i = 0; i < table->size; i++) {
        struct list *entry = table->table[i];
        while (entry != NULL) {
            struct list *next = entry->next;
            int bucket = hash(entry->entry.key, new_size);
            entry->next = new_table[bucket];
            new_table[bucket] = entry;
            entry = next;
        }
    }

    free(table->table);
    table->table = new_table;
    table->size = new_size;
    return 0;
}

/* FIX: release the copied keys/values, chain nodes, bucket array, and table. */
void destroyHashTable(struct HashTable *table) {
    if (table == NULL) {
        return;
    }

    for (int i = 0; i < table->size; i++) {
        struct list *entry = table->table[i];
        while (entry != NULL) {
            struct list *next = entry->next;
            free(entry->entry.key);
            free(entry->entry.value);
            free(entry);
            entry = next;
        }
    }

    free(table->table);
    free(table);
}

/* FIX: use the supplied table size, so the result is always a valid bucket. */
int hash(const char *str, int table_size) {
    if (str == NULL || table_size <= 0) {
        return -1;
    }

    unsigned long value = 5381;
    int c;
    while ((c = (unsigned char)*str++) != '\0') {
        value = ((value << 5) + value) + (unsigned long)c;
    }

    return (int)(value % (unsigned long)table_size);
}

/* FIX: safely traverse a collision chain and compare complete key strings. */
char* get(const struct HashTable *table, const char *key) {
    if (table == NULL || table->table == NULL || key == NULL || table->size <= 0) {
        return NULL;
    }

    int bucket = hash(key, table->size);
    for (const struct list *entry = table->table[bucket];
         entry != NULL;
         entry = entry->next) {
        if (strcmp(entry->entry.key, key) == 0) {
            return entry->entry.value;
        }
    }

    return NULL;
}

/* FIX: update duplicate keys without leaking; copy strings and count only inserts. */
int put(struct HashTable *table, const char *key, const char *value) {
    if (table == NULL || table->table == NULL || key == NULL || value == NULL ||
        table->size <= 0) {
        return -1;
    }

    int bucket = hash(key, table->size);
    for (struct list *entry = table->table[bucket];
         entry != NULL;
         entry = entry->next) {
        if (strcmp(entry->entry.key, key) == 0) {
            char *new_value = copy_string(value);
            if (new_value == NULL) {
                return -1;
            }
            free(entry->entry.value);
            entry->entry.value = new_value;
            return bucket;
        }
    }

    if (table->count == INT_MAX) {
        return -1;
    }

    struct list *entry = malloc(sizeof *entry);
    if (entry == NULL) {
        return -1;
    }

    entry->entry.key = copy_string(key);
    entry->entry.value = copy_string(value);
    if (entry->entry.key == NULL || entry->entry.value == NULL) {
        free(entry->entry.key);
        free(entry->entry.value);
        free(entry);
        return -1;
    }

    /* FIX: grow before insertion to keep the load factor at or below 0.75. */
    if ((size_t)table->count + 1 > ((size_t)table->size * 3) / 4) {
        if (table->size > INT_MAX / 2 ||
            resizeHashTable(table, table->size * 2) != 0) {
            free(entry->entry.key);
            free(entry->entry.value);
            free(entry);
            return -1;
        }
    }

    bucket = hash(key, table->size);
    struct list **link = &table->table[bucket];
    while (*link != NULL) {
        link = &(*link)->next;
    }

    entry->next = NULL;
    *link = entry;
    table->count++;
    return bucket;
}

/* FIX: unlink and free a key's node, then keep the entry count accurate. */
int removeKey(struct HashTable *table, const char *key) {
    if (table == NULL || table->table == NULL || key == NULL || table->size <= 0) {
        return -1;
    }

    int bucket = hash(key, table->size);
    struct list **link = &table->table[bucket];
    while (*link != NULL) {
        struct list *entry = *link;
        if (strcmp(entry->entry.key, key) == 0) {
            *link = entry->next;
            free(entry->entry.key);
            free(entry->entry.value);
            free(entry);
            table->count--;
            return 1;
        }
        link = &entry->next;
    }

    return 0;
}
