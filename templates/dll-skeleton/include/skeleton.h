/* {{REPO}}.dll — C ABI. All strings UTF-8, NUL-terminated.
 * char* results are caller-owned: free with {{PREFIX}}_free_string().
 * On failure they return NULL; see {{PREFIX}}_last_error(). */
#ifndef {{GUARD}}
#define {{GUARD}}
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#if defined(_WIN32) && defined({{PREFIX_UPPER}}_BUILD)
#define {{PREFIX_UPPER}}_API __declspec(dllexport)
#elif defined(_WIN32)
#define {{PREFIX_UPPER}}_API __declspec(dllimport)
#else
#define {{PREFIX_UPPER}}_API
#endif
#define {{PREFIX_UPPER}}_OK 0
#define {{PREFIX_UPPER}}_ERR_INVALID_ARG 1
#define {{PREFIX_UPPER}}_ERR_NOT_SUPPORTED 2
#define {{PREFIX_UPPER}}_ERR_NOT_FOUND 3
#define {{PREFIX_UPPER}}_ERR_ACCESS_DENIED 4
#define {{PREFIX_UPPER}}_ERR_PLATFORM 5
#define {{PREFIX_UPPER}}_ERR_INTERNAL 6
{{PREFIX_UPPER}}_API const char *{{PREFIX}}_version(void);
{{PREFIX_UPPER}}_API const char *{{PREFIX}}_last_error(void);
{{PREFIX_UPPER}}_API int {{PREFIX}}_last_error_code(void);
{{PREFIX_UPPER}}_API void {{PREFIX}}_free_string(char *p);
#ifdef __cplusplus
}
#endif
#endif
