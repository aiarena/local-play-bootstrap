#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* Rosetta for Linux translates x86 `lock cmpxchg` into ARM atomics, which
   fault (SIGBUS) when the operand crosses a 16-byte boundary; x86 does not.
   SC2 4.10 keeps pthread mutexes at 2-byte-aligned addresses, so glibc's
   pthread_mutex_lock dies at map load. Route every misaligned mutex to an
   aligned shadow mutex; aligned mutexes pass straight through.

   Shadows live in a chained hash table keyed by the mutex address. An entry
   is removed (and its shadow freed) by pthread_mutex_destroy or a re-init of
   the same address, so the table holds only live misaligned mutexes.

   Limits: a shadow is process-private and keeps only the mutex type
   (normal/recursive/errorcheck/adaptive). Process-shared, robust and
   priority-inheritance attributes are not carried over. */

#define BUCKETS 4096 /* power of two */

struct entry {
    uintptr_t key;
    pthread_mutex_t shadow;
    struct entry *next;
};

static struct entry *buckets[BUCKETS];
static pthread_mutex_t table_lock = PTHREAD_MUTEX_INITIALIZER;

static int (*r_init)(pthread_mutex_t *, const pthread_mutexattr_t *);
static int (*r_destroy)(pthread_mutex_t *);
static int (*r_lock)(pthread_mutex_t *);
static int (*r_trylock)(pthread_mutex_t *);
static int (*r_timedlock)(pthread_mutex_t *, const struct timespec *);
static int (*r_unlock)(pthread_mutex_t *);
static int (*r_cwait)(pthread_cond_t *, pthread_mutex_t *);
static int (*r_ctimedwait)(pthread_cond_t *, pthread_mutex_t *, const struct timespec *);
static int log_on;

__attribute__((constructor)) static void setup(void) {
    r_init = dlsym(RTLD_NEXT, "pthread_mutex_init");
    r_destroy = dlsym(RTLD_NEXT, "pthread_mutex_destroy");
    r_lock = dlsym(RTLD_NEXT, "pthread_mutex_lock");
    r_trylock = dlsym(RTLD_NEXT, "pthread_mutex_trylock");
    r_timedlock = dlsym(RTLD_NEXT, "pthread_mutex_timedlock");
    r_unlock = dlsym(RTLD_NEXT, "pthread_mutex_unlock");
    r_cwait = dlvsym(RTLD_NEXT, "pthread_cond_wait", "GLIBC_2.3.2");
    if (!r_cwait) r_cwait = dlsym(RTLD_NEXT, "pthread_cond_wait");
    r_ctimedwait = dlvsym(RTLD_NEXT, "pthread_cond_timedwait", "GLIBC_2.3.2");
    if (!r_ctimedwait) r_ctimedwait = dlsym(RTLD_NEXT, "pthread_cond_timedwait");
    log_on = getenv("ALIGNMUTEX_LOG") != NULL;
}

static inline int misaligned(const void *m) { return ((uintptr_t)m & 3) != 0; }

static inline size_t bucket_of(uintptr_t key) {
    return (size_t)((key >> 1) ^ (key >> 13)) & (BUCKETS - 1);
}

/* The shadow for misaligned mutex m, created on first use with m's type.
   NULL only if the allocation fails. */
static pthread_mutex_t *shadow(pthread_mutex_t *m) {
    uintptr_t key = (uintptr_t)m;
    struct entry **head = &buckets[bucket_of(key)];
    pthread_mutex_t *s = NULL;
    r_lock(&table_lock);
    for (struct entry *e = *head; e; e = e->next)
        if (e->key == key) { s = &e->shadow; break; }
    if (!s) {
        struct entry *e = aligned_alloc(64, (sizeof *e + 63) & ~(size_t)63);
        if (e) {
            int kind;
            memcpy(&kind, (char *)m + 16, sizeof kind); /* __data.__kind */
            pthread_mutexattr_t a;
            pthread_mutexattr_init(&a);
            pthread_mutexattr_settype(&a, kind & 3);
            r_init(&e->shadow, &a);
            pthread_mutexattr_destroy(&a);
            e->key = key;
            e->next = *head;
            *head = e;
            s = &e->shadow;
            if (log_on) fprintf(stderr, "alignmutex: shadow for %p kind %d\n", (void *)m, kind & 3);
        } else if (log_on) {
            fprintf(stderr, "alignmutex: out of memory for %p\n", (void *)m);
        }
    }
    r_unlock(&table_lock);
    return s;
}

/* Remove and free m's shadow, if it has one. */
static void forget(pthread_mutex_t *m) {
    uintptr_t key = (uintptr_t)m;
    r_lock(&table_lock);
    for (struct entry **p = &buckets[bucket_of(key)]; *p; p = &(*p)->next) {
        if ((*p)->key == key) {
            struct entry *e = *p;
            *p = e->next;
            r_destroy(&e->shadow);
            free(e);
            break;
        }
    }
    r_unlock(&table_lock);
}

int pthread_mutex_init(pthread_mutex_t *m, const pthread_mutexattr_t *a) {
    if (!r_init) setup();
    if (misaligned(m)) forget(m); /* drop a stale shadow at this address */
    return r_init(m, a);          /* plain stores; fine at any alignment */
}
int pthread_mutex_destroy(pthread_mutex_t *m) {
    if (!r_destroy) setup();
    if (!misaligned(m)) return r_destroy(m);
    forget(m);
    return 0;
}
int pthread_mutex_lock(pthread_mutex_t *m) {
    if (!r_lock) setup();
    if (!misaligned(m)) return r_lock(m);
    pthread_mutex_t *s = shadow(m);
    return s ? r_lock(s) : ENOMEM;
}
int pthread_mutex_trylock(pthread_mutex_t *m) {
    if (!r_trylock) setup();
    if (!misaligned(m)) return r_trylock(m);
    pthread_mutex_t *s = shadow(m);
    return s ? r_trylock(s) : ENOMEM;
}
int pthread_mutex_timedlock(pthread_mutex_t *m, const struct timespec *t) {
    if (!r_timedlock) setup();
    if (!misaligned(m)) return r_timedlock(m, t);
    pthread_mutex_t *s = shadow(m);
    return s ? r_timedlock(s, t) : ENOMEM;
}
int pthread_mutex_unlock(pthread_mutex_t *m) {
    if (!r_unlock) setup();
    if (!misaligned(m)) return r_unlock(m);
    pthread_mutex_t *s = shadow(m);
    return s ? r_unlock(s) : ENOMEM;
}
int pthread_cond_wait(pthread_cond_t *c, pthread_mutex_t *m) {
    if (!r_cwait) setup();
    if (!misaligned(m)) return r_cwait(c, m);
    pthread_mutex_t *s = shadow(m);
    return s ? r_cwait(c, s) : ENOMEM;
}
int pthread_cond_timedwait(pthread_cond_t *c, pthread_mutex_t *m, const struct timespec *t) {
    if (!r_ctimedwait) setup();
    if (!misaligned(m)) return r_ctimedwait(c, m, t);
    pthread_mutex_t *s = shadow(m);
    return s ? r_ctimedwait(c, s, t) : ENOMEM;
}
