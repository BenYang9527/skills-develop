#!/usr/bin/env python3
"""Render reviewed task facts as a standalone SVG; Python standard library only."""
import argparse
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

PHASES = [('澄清', 'Clarify'), ('计划', 'Plan'), ('实现', 'Implement'),
          ('验证', 'Verify'), ('文档', 'Docs'), ('审查', 'Review'), ('提交', 'Submit')]
TIME_LABELS = ['总跨度', '可观察执行时间', '阶段窗口合计']


def seconds(value):
    if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                              or not math.isfinite(value) or value < 0):
        raise ValueError('seconds must be a finite nonnegative number or null')
    return value


def duration(value):
    seconds(value)
    if value is None:
        return '未知'
    hours, rest = divmod(round(value), 3600)
    minutes, secs = divmod(rest, 60)
    return f'{hours}h {minutes:02d}m {secs:02d}s'


def text(value):
    if not isinstance(value, str):
        raise ValueError('text fields must be strings')
    if any(not (c in '\n\r\t' or 0x20 <= ord(c) <= 0xD7FF
                    or 0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF)
           for c in value):
        raise ValueError('text contains characters forbidden in XML 1.0')
    return value


def wrap(value, columns):
    """Wrap CJK and long unbroken identifiers without dropping characters."""
    lines, line, width = [], '', 0
    for char in text(value).replace('\r\n', '\n').replace('\r', '\n'):
        if char == '\n':
            lines.append(line)
            line, width = '', 0
            continue
        # Reserve 1.1em per character at the call site, including wide Latin W/M.
        step = 2
        if width + step > columns and line:
            # Keep short space-delimited IDs and numbers together when possible.
            split = line.rfind(' ')
            if split > 0:
                lines.append(line[:split+1])
                line = line[split+1:]
                width = len(line) * 2
            else:
                lines.append(line)
                line, width = '', 0
        line += char
        width += step
    return lines + [line]


def validate(data):
    for key in ['title', 'scope', 'outcome']:
        text(data[key])
    if [r['label'] for r in data['times']] != TIME_LABELS:
        raise ValueError('times must contain the three documented labels in order')
    if [r['number'] for r in data['phases']] != [f'{n:02}' for n in range(1, 8)]:
        raise ValueError('phases must contain 01 through 07 in order')
    for row in data['times'] + data['phases']:
        seconds(row['seconds'])
        text(row['note'])
    for key in ['parallel', 'usage', 'bottlenecks', 'bad_taste', 'unknowns']:
        if not isinstance(data[key], list):
            raise ValueError(f'{key} must be an array')
        for item in data[key]:
            text(item)
    if not isinstance(data['sources'], list):
        raise ValueError('sources must be an array')
    ids = []
    for source in data['sources']:
        for key in ['id', 'path', 'locator', 'supports']:
            text(source[key])
        ids.append(source['id'])
    if len(ids) != len(set(ids)):
        raise ValueError('source IDs must be unique')


def render(data):
    validate(data)
    elements = []
    y = 48

    def paragraph(value, size=18, color='#233449', bold=False, indent=0):
        nonlocal y
        for line in wrap(value, int((1036-indent) / (size * 1.1) * 2)):
            elements.append(f'<text x="{52+indent}" y="{y}" font-size="{size}" '
                            f'fill="{color}" font-weight="{700 if bold else 400}">{escape(line)}</text>')
            y += size * 1.55

    def heading(value):
        nonlocal y
        y += 23
        elements.append(f'<path d="M52 {y-18}h1036" stroke="#dce4ee"/>')
        y += 15
        paragraph(value, 22, bold=True)
        y += 5

    paragraph(data['title'], 32, bold=True)
    paragraph(data['scope'], 16, '#61718a')
    y += 12
    paragraph(data['outcome'], 20, bold=True)
    heading('时间 · 三种口径分别看')
    card_y = y
    note_lines = [wrap(row['note'], int(298 / (15 * 1.1) * 2)) for row in data['times']]
    card_height = 95 + max(map(len, note_lines)) * 24
    for index, row in enumerate(data['times']):
        x = 52 + index * 352
        elements.append(f'<rect x="{x}" y="{card_y-22}" width="332" height="{card_height}" '
                        'rx="14" fill="white" stroke="#dce4ee"/>')
        for value, offset, size, color in [(row['label'], 4, 18, '#61718a'),
                                            (duration(row['seconds']), 46, 27, '#17695a')]:
            elements.append(f'<text x="{x+17}" y="{card_y+offset}" font-size="{size}" '
                            f'fill="{color}">{escape(value)}</text>')
        for i, line in enumerate(note_lines[index]):
            elements.append(f'<text x="{x+17}" y="{card_y+78+i*24}" font-size="15" '
                            f'fill="#61718a">{escape(line)}</text>')
    y = card_y + card_height + 10
    heading('01–07 阶段窗口')
    paragraph('条长比较已知阶段窗口；未知不补零，条长不是全任务占比。', 16, '#61718a')
    maximum = max((row['seconds'] or 0 for row in data['phases']), default=0)
    for row, (zh, en) in zip(data['phases'], PHASES):
        paragraph(f"{row['number']}  {zh} {en}    {duration(row['seconds'])}", 20, bold=True)
        elements.append(f'<rect x="52" y="{y-10}" width="1036" height="10" rx="5" '
                        'fill="#e8edf4"/>')
        if row['seconds'] is None:
            elements.append(f'<path d="M52 {y-5}h1036" stroke="#a5afc2" '
                            'stroke-width="2" stroke-dasharray="6 6"/>')
        elif maximum:
            width = 1036 * row['seconds'] / maximum
            elements.append(f'<rect x="52" y="{y-10}" width="{width}" height="10" '
                            'rx="5" fill="#7561c9"/>')
        y += 22
        if row['note']:
            paragraph(row['note'], 16, '#61718a', indent=38)
        y += 9
    sections = [('Implement · 计划与实际并行', 'parallel', '并行证据不足'),
                ('Token 与成本', 'usage', '用量与成本未知'),
                ('阻塞与返工', 'bottlenecks', '暂无可确认记录'),
                ('Bad taste · 新观察', 'bad_taste', '暂无新增'),
                ('影响判断的数据缺口', 'unknowns', '暂无已识别缺口')]
    for title, key, fallback in sections:
        heading(title)
        for value in data[key] or [fallback]:
            paragraph(value)
            y += 8
    heading('证据索引 · 完整路径见同名 JSON')
    for source in data['sources']:
        paragraph(f"[{source['id']}] {source['supports']}", 15, '#61718a')
    height = math.ceil(y + 35)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1140" height="{height}" '
            f'viewBox="0 0 1140 {height}" role="img" aria-labelledby="title desc">'
            f'<title id="title">{escape(data["title"])}</title>'
            '<desc id="desc">任务交付、时间、阶段、并行、用量与数据缺口</desc>'
            f'<rect width="1140" height="{height}" fill="#f7f9fc"/>'
            '<g font-family="PingFang SC, Microsoft YaHei, Arial, sans-serif">'
            + ''.join(elements) + '</g></svg>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    content = render(json.loads(args.data.read_text(encoding='utf-8')))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as target:
        target.write(content)
    print(args.output)


if __name__ == '__main__':
    main()
