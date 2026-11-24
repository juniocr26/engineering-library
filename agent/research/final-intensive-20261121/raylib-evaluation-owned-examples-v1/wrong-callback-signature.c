#include "raylib.h"
#include <stddef.h>
static int wrong_loader(int name) { return name; }
void install_wrong(void) { SetLoadFileTextCallback(wrong_loader); }
