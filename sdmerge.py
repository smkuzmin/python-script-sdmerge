#!/usr/bin/env python3
"""
SDMerge v1.6 - Subdomain Merger

Reads subdomain lists from stdin, merges them, groups by root domain, and
outputs in sorted order with root domain headers. Root domain is always
printed first in each section (if present in input).

USAGE:
  cat file1.subdomains file2.subdomains .. fileN.subdomains | sdmerge
"""

import sys
from collections import defaultdict


def parse_line(line):
    """Разбираем строку и извлекаем домен, игнорируя комментарии после #"""
    line = line.strip()
    if not line or line.startswith('#'):
        return None

    # Убираем комментарии в конце строки (всё после #)
    if '#' in line:
        domain = line.split('#', 1)[0].strip()
    else:
        domain = line.strip()

    if not domain:
        return None

    # Базовая валидация: домен не должен содержать пробелов
    if ' ' in domain:
        return None

    return domain.lower()


def main():
    # sections: корневой домен -> множество доменов в этой секции
    sections = defaultdict(set)
    # data_set: домены, которые были в данных (не в заголовках)
    data_set = set()

    current_root = None

    for line in sys.stdin:
        original = line.strip()
        if not original:
            continue

        # Проверяем, является ли строка заголовком секции
        if original.startswith('#'):
            # Извлекаем корневой домен из заголовка
            header = original[1:].strip()
            if '#' in header:
                header = header.split('#', 1)[0].strip()
            if header and ' ' not in header:
                current_root = header.lower()
            continue

        # Обычная строка с доменом
        if current_root is None:
            continue  # Пропускаем домены до первого заголовка

        domain = parse_line(line)
        if domain:
            sections[current_root].add(domain)
            data_set.add(domain)

    if not sections:
        sys.exit(0)

    # Выводим, отсортировав по корню
    first = True
    for root in sorted(sections.keys()):
        if not first:
            print()  # Пустая строка между группами
        first = False

        # Печатаем заголовок корневого домена
        print(f"# {root}")

        # Печатаем корневой домен ТОЛЬКО если он был во входных данных (не в заголовке)
        if root in data_set:
            print(root)

        # Печатаем отсортированные поддомены (исключая корень)
        for sub in sorted(d for d in sections[root] if d != root):
            print(sub)

# Точка входа
if __name__ == '__main__':
    # Показываем справку при вызове с -h или --help, или если запущен без перенаправления ввода
    if sys.stdin.isatty() or '-h' in sys.argv or '--help' in sys.argv:
        print(__doc__, file=sys.stderr)
        sys.exit(0)

    # Обрабатываем прерывание без вывода ошибки
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
