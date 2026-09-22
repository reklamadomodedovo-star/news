#!/bin/sh
# Сборка прототипа из частей. Запуск: bash build.sh
cd "$(dirname "$0")"
python3 tools/add_images.py >/dev/null 2>&1   # пересобирает _parts/z-img.html, если появились новые фото
cat _parts/a-head.html _parts/b-screens.html _parts/c-catalog.html _parts/d-admin.html \
    _parts/e-kit.html _parts/z-img.html _parts/g-wp.html _parts/f-check-script.html > index.html
echo "собрано: $(wc -c < index.html) байт"
