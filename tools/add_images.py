#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка графики прототипа «ФОКУС»:
 1) пережимает фотографии из img/ в два размера (hi/lo) и кладёт их в _parts/z-img.html как CSS-классы .im--<key> / .im--<key>-s
 2) подставляет в партиалы фоны <span class="ph__bg im--<key>"> на место серых заглушек
Запуск: python3 tools/add_images.py      (идемпотентно: повторный запуск не дублирует вставки)
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'img')
PARTS = os.path.join(ROOT, '_parts')

# ---------- 1. словари ----------
# alt: осмысленное описание (используется как aria-label; в WP будет alt у <img>)
ALT = {
    'mara':  'Участники городского полумарафона на набережной на рассвете',
    'metro': 'Ночная платформа метро, приближается поезд',
    'bills': 'Квитанции и калькулятор на кухонном столе',
    'selfemp': 'Ноутбук, документы и телефон на рабочем столе',
    'ereader': 'Электронная книга на дубовом столе рядом с бумажными книгами',
    'skate': 'Скейт-площадка с рампами и освещением в городском парке',
    'velo':  'Велосипед пассажира на платформе метро',
    'robot': 'Робот-пылесос на полу светлой гостиной',
    'phone': 'Смартфон в руке на фоне городской улицы',
    'food':  'Фестиваль уличной еды в городском парке вечером',
    'lect':  'Лекционный зал городской библиотеки, слушатели',
    'light': 'Световая инсталляция в тёмном выставочном зале',
    'music': 'Живой концерт инди-группы в небольшом клубе',
    'podcast': 'Микрофон в студии подкастов',
    'depot':  'Метродепо ночью: вагоны под светом фонарей',
    'author': 'Портрет Анны Ковалёвой, редактора раздела «События»',
    'column': 'Портрет Игоря Петрова, обозревателя',
}
HI_W, LO_W = 820, 280
# временные файлы-заменители: ключ -> реальный файл (снимается по мере генерации своих фото)
FILE = {'mara': 'hero-marathon', 'metro': 'metro-night', 'skate': 'skatepark',
        'robot': 'robot-vacuum', 'phone': 'phone-plans', 'food': 'food-festival',
        'lect': 'lecture', 'light': 'lightshow', 'music': 'music',
        'podcast': 'podcast', 'depot': 'depot'}
# если своего файла ещё нет — берём временный из уже сгенерированных
TEMP = {'lect': 'ereader', 'light': 'metro', 'music': 'food', 'podcast': 'selfemp', 'depot': 'metro'}
AUTHOR_FILES = {'author': 'Портрет Анны Ковалёвой, редактора раздела «События»',
                'column': 'Портрет Игоря Петрова, обозревателя'}

# какой ключ в какой файл и в каком порядке (порядок = порядок .ph в файле)
MAP = {
    'a-head.html': ['mara', 'bills', 'selfemp', 'mara', 'ereader', 'metro', 'selfemp',
                    'velo', 'metro', 'bills', 'skate', 'ereader', 'robot', 'phone'],
    'b-screens.html': ['mara', 'food', 'skate', 'light', 'mara'],
    'c-catalog.html': ['ereader', 'robot', 'phone', 'selfemp', 'ereader', 'robot'],
    'd-admin.html': [],
}
# медиаблок главной: три плитки подряд
MEDIA = ['depot', 'podcast', 'mara']

# ---------- 2. пережимаем и пишем CSS ----------
def encode(name, width, quality):
    src = os.path.join(IMG, FILE.get(name, name) + '.jpg')
    if not os.path.exists(src):
        alt = TEMP.get(name)
        if not alt:
            return None
        src = os.path.join(IMG, FILE.get(alt, alt) + '.jpg')
        if not os.path.exists(src):
            return None
    im = Image.open(src).convert('RGB')
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=quality, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode('ascii')

EV_KEYS = {'bills', 'music', 'mara', 'food', 'lect', 'light', 'skate', 'metro', 'velo'}  # ключи ленты мероприятий и «Читайте также»
keys = sorted({k for v in MAP.values() for k in v} | set(MEDIA) | set(AUTHOR_FILES) | EV_KEYS)
blocks, total = [], 0
for k in keys:
    hi = encode(k, HI_W, 60)
    lo = encode(k, LO_W, 50)
    if not hi:
        print('  нет файла:', k + '.jpg'); continue
    total += len(hi) + len(lo)
    blocks.append('.im--%s{background-image:url("data:image/jpeg;base64,%s")}' % (k, hi))
    blocks.append('.im--%s-s{background-image:url("data:image/jpeg;base64,%s")}' % (k, lo))

css = ('<!-- ФОТОГРАФИИ ПРОТОТИПА: сжатые JPEG в data-URI.\n'
       '     В WordPress здесь обычные <img src> из медиабиблиотеки с srcset и WebP. -->\n'
       '<style>\n' + '\n'.join(blocks) + '\n</style>\n')
open(os.path.join(PARTS, 'z-img.html'), 'w', encoding='utf-8').write(css)
print('z-img.html: %d классов, %.0f КБ base64' % (len(blocks), total / 1024))

# ---------- 3. подставляем фоны в партиалы ----------
PH_RE = re.compile(r'<div class="ph([^"]*)"><span>([^<]*)</span></div>')

def patch(fname, keys):
    path = os.path.join(PARTS, fname)
    s = open(path, encoding='utf-8').read()
    if 'ph__bg' in s:
        print('  %s: уже размечено, пропускаю' % fname); return
    i = [0]
    def sub(m):
        if i[0] >= len(keys):
            return m.group(0)
        k = keys[i[0]]; i[0] += 1
        cls = ('ph ' + m.group(1)).replace('  ', ' ').strip()
        return ('<div class="%s">'
                '<span class="ph__bg im--%s" role="img" aria-label="%s" data-img="%s"></span>'
                '</div>') % (cls, k, ALT.get(k, ''), k)
    s2, n = PH_RE.subn(sub, s)
    open(path, 'w', encoding='utf-8').write(s2)
    print('  %s: заменено %d заглушек' % (fname, n))

for f, keys in MAP.items():
    if keys and os.path.exists(os.path.join(PARTS, f)):
        patch(f, keys)

# медиаплитки (у них класс .med__ph, а не .ph)
path = os.path.join(PARTS, 'a-head.html')
s = open(path, encoding='utf-8').read()
if 'med__ph' in s and 'ph__bg im--depot' not in s:
    i = [0]
    def submed(m):
        k = MEDIA[i[0]] if i[0] < len(MEDIA) else None
        i[0] += 1
        if not k:
            return m.group(0)
        return m.group(0)[:-len('</span>')] + ('<span class="ph__bg im--%s" role="img" aria-label="%s" data-img="%s"></span></span>'
                                               % (k, ALT.get(k, ''), k))
    s2, n = re.subn(r'<span class="med__ph">.*?</span></span>', submed, s, flags=re.S)
    open(path, 'w', encoding='utf-8').write(s2)
    print('  a-head.html: медиаплиток размечено %d' % n)


# ---------- 4. портреты авторов (если файлы уже сгенерированы) ----------
def patch_authors():
    """Аватары: подставляем фото, только если файлы уже сгенерированы (иначе остаются инициалы)."""
    def has(name):
        return os.path.exists(os.path.join(IMG, name + '.jpg'))

    if has('author'):
        for f, marker in (('b-screens.html', '<span class="autor__av">АК</span>'),
                          ('a-head.html',   '<span class="autor__av">АК</span>')):
            path = os.path.join(PARTS, f)
            if not os.path.exists(path):
                continue
            s = open(path, encoding='utf-8').read()
            if 'im--author' not in s and marker in s:
                s = s.replace(marker, '<span class="autor__av"><span class="ph__bg im--author" role="img" '
                                      'aria-label="Анна Ковалёва"></span></span>', 1)
                open(path, 'w', encoding='utf-8').write(s)
                print('  %s: аватар автора подставлен' % f)
    else:
        print('  портреты авторов: файлов ещё нет, шаг пропущен')

    if has('column'):
        path = os.path.join(PARTS, 'a-head.html')
        s = open(path, encoding='utf-8').read()
        marker = '<div class="byline"><span>Игорь Петров, обозреватель</span></div>'
        if 'im--column' not in s and marker in s:
            s = s.replace(marker, '<div class="byline"><span class="autor__av autor__av--sm"><span class="ph__bg im--column" '
                                  'role="img" aria-label="Игорь Петров"></span></span><span>Игорь Петров, обозреватель</span></div>', 1)
            open(path, 'w', encoding='utf-8').write(s)
            print('  a-head.html: портрет колумниста подставлен')

patch_authors()
