/* BridgeKit test fixture - the type shapes the 2026-11 full survey
 * of the collection's shipped headers found beyond the original
 * grammar: int64_t out-parameters, uint8_t buffers and out-buffers,
 * size_t, double, function-pointer typedefs and a callbacks struct.
 * Lines are trimmed copies of the real shipped headers
 * (SettingsKit include/settingskit.h, ImageKit include/imagekit.h,
 * ProviderKit include/providerkit.h) with the prefixes unified to
 * SC_ so the shapes can live in one fixture. */
#ifndef SCALARS_H
#define SCALARS_H

#include <stdint.h>
#include <stddef.h>

typedef struct ScDoc ScDoc;

SC_API const char *sc_version(void);
SC_API void sc_free_string(char *p);
SC_API int sc_schema_version(ScDoc *doc, int64_t *out);
SC_API int sc_set_f64(ScDoc *doc, const char *path, double value);
SC_API void sc_free_buffer(uint8_t *p, size_t len);
SC_API int sc_encode(ScDoc *doc, uint8_t **out_ptr, size_t *out_len);
SC_API uint64_t sc_load_bytes(const uint8_t *data, size_t len);

typedef int (*ScListFn)(void *user_data, const char *uri, char **out_json);
typedef void (*ScFreeFn)(void *user_data, char *p);

typedef struct ScCallbacks {
    uint32_t struct_size;
    ScListFn list;
    ScFreeFn free_string;
} ScCallbacks;

SC_API int sc_register(const ScCallbacks *callbacks, void *user_data);
SC_API int sc_run(const char *spec_json, ScListFn progress_cb, void *user_data);

#endif
