#!/usr/bin/env python3
"""
SDMerge v1.3 - Merge and sort subdomain lists with root domain grouping

Reads subdomain lists from stdin, merges them, groups by root domain, and
outputs in sorted order with root domain headers. Root domain is always
printed first in each section.

USAGE:
  cat file1.subdomains file2.subdomains .. fileN.subdomains | sdmerge

"""

import sys
from collections import defaultdict


def parse_line(line):
    """Разбираем строку и извлекает домен (игнорируя комментарии)"""
    line = line.strip()
    if not line or line.startswith('#'):
        return None

    # Удаляем часть с комментарием, если она есть
    if '#' in line:
        domain = line.split('#', 1)[0].strip()
    else:
        domain = line

    if not domain:
        return None

    return domain.lower()


def find_roots(domains):
    """
    Определяем корневые домены из набора доменов
    Корневой домен — это домен, который не является поддоменом другого домена из набора
    """
    roots = set()
    for domain in domains:
        is_root = True
        for other in domains:
            if domain != other and domain.endswith('.' + other):
                is_root = False
                break
        if is_root:
            roots.add(domain)
    return roots


def group_by_root(domains, roots):
    """Группируем домены по их корневому домену"""
    groups = defaultdict(set)
    for domain in domains:
        # Находим, к какому корневому домену относится этот домен
        assigned = False
        for root in roots:
            if domain == root or domain.endswith('.' + root):
                groups[root].add(domain)
                assigned = True
                break
        if not assigned:
            # Сирота - считаем его собственным корневым доменом
            groups[domain].add(domain)
    return groups


def main():
    # Читаем и разбираем все домены из stdin
    all_domains = set()

    for line in sys.stdin:
        domain = parse_line(line)
        if domain:
            all_domains.add(domain)

    if not all_domains:
        sys.exit(0)

    # Находим корневые домены
    roots = find_roots(all_domains)

    # Группируем домены по корню
    groups = group_by_root(all_domains, roots)

    # Выводим, отсортировав по корню: сначала корневой домен, затем отсортированные поддомены
    first = True
    for root in sorted(groups.keys()):
        if not first:
            print()  # Пустая строка между группами
        first = False

        # Печатаем заголовок корневого домена
        print(f"# {root}")

        # Печатаем сначала корневой домен
        print(root)

        # Печатаем отсортированные поддомены (исключая корень)
        subdomains = [d for d in groups[root] if d != root]
        for subdomain in sorted(subdomains):
            print(subdomain)

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
