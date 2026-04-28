# Paint TSIS

## Запуск

1. Установить зависимости:

   `python -m pip install -r requirements.txt`

2. Запустить приложение:

   `python paint.py`

## Горячие клавиши

- `p` — Pencil (карандаш)
- `l` — Line (линия)
- `r` — Rectangle (прямоугольник)
- `c` — Circle (круг)
- `h` — Shapes (подрежимы: 4 для смены)
- `e` — Eraser (ластик)
- `f` — Fill (заливка)
- `t` — Text (текст)
- `1/2/3` — толщина кисти 2/5/10 px
- `4` — при активном Shapes: цикл подрежимов (square, right_triangle, equilateral_triangle, rhombus)
- `Ctrl+S` — сохранить canvas (в exports/)

## Примечания

- Если вы используете Python 3.14 и столкнётесь с проблемами установки `pygame`, используйте `pygame-ce` (указан в `requirements.txt`).
- Canvas создаётся внутри окна и сохраняется в папке `exports/` при сохранении.
