from boltons.iterutils import default_visit
from boltons.fileutils import iter_find_files

key_value = default_visit((), 'item', 7)
paths = iter_find_files('owned-example', '*.txt', max_depth=0)
