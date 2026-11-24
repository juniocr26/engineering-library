#include "raylib.h"
#include <stddef.h>
void inspect_text(const char *name) {
    char *text = LoadFileText(name);
    if (text != NULL) UnloadFileText(text);
}
bool delegate_save(const char *name, const char *text) { return SaveFileText(name, text); }
