/* sample.h — a tiny header in the WinDevKit family shape, small
 * enough to read at a glance. The bridgekit.py example next to
 * this file generates C# and Rust bindings from it. Real kits'
 * headers live in kits/<Kit>/include/ and work exactly the same
 * way. */
#ifndef SAMPLE_H
#define SAMPLE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifdef SAMPLE_BUILD
#define SM_API __declspec(dllexport)
#else
#define SM_API __declspec(dllimport)
#endif

/* Borrowed string: copy it, never free it. */
SM_API const char *sm_version(void);

/* Caller-owned string: free it with sm_free_string. */
SM_API char *sm_greet(const char *name_utf8);
SM_API void sm_free_string(char *p);

/* Plain value in, value out. */
SM_API int sm_add(int a, int b);
SM_API uint64_t sm_total_bytes(const uint8_t *data, size_t len);

#ifdef __cplusplus
}
#endif

#endif /* SAMPLE_H */
