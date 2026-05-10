#!/usr/bin/env python3
"""
SDAggr v1.7 - Subdomain Aggregator

Reads subdomain lists from stdin, aggregates them by finding the shortest
root domain for each entry, and outputs in sorted order with root headers.

USAGE:
  cat file1.subdomains file2.subdomains .. fileN.subdomains | sdaggr
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


def find_true_roots(all_domains):
    """
    Находит истинные корневые домены - те, которые не являются поддоменами
    других доменов из набора.
    """
    roots = set()
    for domain in all_domains:
        is_root = True
        for other in all_domains:
            if domain != other and domain.endswith('.' + other):
                is_root = False
                break
        if is_root:
            roots.add(domain)
    return roots


def group_by_true_root(domains, true_roots):
    """Группируем домены по их истинному корневому домену"""
    groups = defaultdict(set)
    for domain in domains:
        # Находим, к какому истинному корню относится этот домен
        for root in true_roots:
            if domain == root or domain.endswith('.' + root):
                groups[root].add(domain)
                break
    return groups


def main():
    # Собираем все домены и данные о том, какие были во входных данных (не в заголовках)
    all_domains = set()
    data_set = set()
    # sections: имя заголовка секции -> множество доменов в ней
    sections = defaultdict(set)

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
            all_domains.add(domain)
            data_set.add(domain)
            # Заполняем секции: добавляем домен в набор текущего заголовка
            sections[current_root].add(domain)
            # Сам заголовок тоже считается частью секции
            sections[current_root].add(current_root)

    if not all_domains:
        sys.exit(0)

    # --- ВТОРОЙ ПРОХОД: Агрегация секций по иерархии заголовков ---
    # Сортируем ключи секций (заголовки) по длине (убывание), чтобы обрабатывать от самых длинных (потенциальных поддоменов)
    section_keys = sorted(sections.keys(), key=len, reverse=True)

    for header in section_keys:
        # Если эта секция уже удалена (перенесена в другую), пропускаем
        if header not in sections:
            continue

        # Ищем родительскую секцию среди существующих
        # Родитель - это такой заголовок, на который заканчивается текущий заголовок
        found_parent = None
        for other_header in section_keys:
            if other_header == header:
                continue
            if other_header not in sections:
                continue

            # Проверяем, является ли текущий заголовок поддоменом другого
            if header.endswith('.' + other_header):
                found_parent = other_header
                break # Нашли ближайшего родителя

        if found_parent:
            # Переносим все домены из текущей секции в родительскую
            sections[found_parent].update(sections[header])
            # Удаляем дочернюю секцию
            del sections[header]
    # -------------------------------------------------------------

    # Выводим, отсортировав по корню (ключам словаря sections)
    first = True
    for root in sorted(sections.keys()):
        if not first:
            print()  # Пустая строка между группами
        first = False

        # Печатаем заголовок корневого домена
        print(f"# {root}")

        # Печатаем корневой домен ТОЛЬКО если он был во входных данных
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
