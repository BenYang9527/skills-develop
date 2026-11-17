#!/usr/bin/env python3
"""Render reviewed task facts as an offline HTML efficiency report."""

import argparse
from html import escape
import json
from pathlib import Path

from render_svg import duration, validate


COLORS = ("#628aa6", "#536eab", "#156b5b", "#ae7f29", "#675c90", "#a45b45")


def number(value):
    if value is None:
        return "未知"
    if type(value) is not int or value < 0:
        raise ValueError("Token and response counts must be nonnegative integers or null")
    return f"{value:,}"


def entries(items):
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def timeline(events):
    rows = []
    for event in events:
        note = f'<p>{escape(event["note"])}</p>' if event.get("note") else ""
        highlight = ' class="highlight"' if event.get("highlight") else ""
        rows.append(
            f'<dt>{escape(event.get("at", "时间未知"))}</dt>'
            f'<dd{highlight}><strong>{escape(event["label"])}</strong>{note}</dd>'
        )
    return '<dl class="timeline">' + "".join(rows) + "</dl>" if rows else ""


def share_bar(groups, total, *, by_stage=False):
    number(total)
    segments = []
    for index, (label, count) in enumerate(groups):
        number(count)
        if count:
            is_implementation = by_stage and (
                "实现" in label or "implement" in label.casefold().split()
            )
            color = COLORS[2 if is_implementation else index % len(COLORS)]
            if by_stage and not is_implementation and color == COLORS[2]:
                color = "#487e83"
            if not by_stage:
                color = COLORS[(2, 4)[index % 2]]
            segments.append((label, count, color, is_implementation))
    accounted = sum(count for _, count, _, _ in segments)
    if total is not None and accounted > total:
        raise ValueError("Grouped Token counts exceed the reported total")
    if not total or not accounted:
        label = "分阶段" if by_stage else "分角色"
        return f'<p class="fine">{label}用量占比未知。</p>'
    if accounted < total:
        segments.append(("归属未知", total - accounted, "#a2aaa4", False))

    bars, legend, descriptions = [], [], []
    for label, count, color, emphasized in segments:
        fraction = count / total * 100
        share = "<0.1%" if fraction < 0.05 else f"{fraction:.1f}%"
        bars.append(f'<span style="width:{fraction:.6f}%;--segment:{color}"></span>')
        css_class = ' class="implement"' if emphasized else ""
        legend.append(
            f'<li{css_class} style="--segment:{color}">{escape(label)} <b>{escape(share)}</b></li>'
        )
        descriptions.append(f"{label} {share}")
    description = escape("，".join(descriptions), quote=True)
    return (
        f'<div class="bar" role="img" aria-label="{description}">{"".join(bars)}</div>'
        f'<ul class="legend">{"".join(legend)}</ul>'
    )


def token_chart(usage, phases):
    total = usage.get("total")
    roles = [(row["role"], row.get("tokens")) for row in usage.get("roles", [])]
    stages = [(row["label"], row.get("tokens")) for row in phases]
    role_bar = share_bar(roles, total)
    stage_bar = share_bar(stages, total, by_stage=True)
    if not usage and not any(count is not None for _, count in stages):
        return ""
    default_stage = any(count for _, count in stages) and bool(total)
    stage_checked, role_checked = (" checked", "") if default_stage else ("", " checked")
    return f"""
      <div class="token-chart">
        <fieldset aria-label="Token 分组方式">
          <label><input id="tokens-stage" type="radio" name="token-group"{stage_checked}>按阶段</label>
          <label><input id="tokens-role" type="radio" name="token-group"{role_checked}>按角色</label>
        </fieldset>
        <div class="by-stage">{stage_bar}</div>
        <div class="by-role">{role_bar}</div>
      </div>"""


def usage_cards(usage):
    fields = (
        ("cached_input", "缓存输入"), ("uncached_input", "非缓存输入"),
        ("output", "输出"), ("reasoning", "其中推理"),
    )
    cards = []
    for row in usage.get("roles", []):
        labels = []
        for key, label in fields:
            if key in row:
                css_class = ' class="subset"' if key == "reasoning" else ""
                labels.append(f'<div{css_class}><dt>{label}</dt><dd>{number(row[key])}</dd></div>')
        context = []
        if row.get("model"):
            context.append(escape(row["model"]))
        if "responses" in row:
            context.append(f'{number(row["responses"])} 个模型响应')
        cards.append(f"""
          <article class="card usage-card">
            <h4>{escape(row["role"])}</h4>
            <strong class="value">{number(row.get("tokens"))}</strong>
            <p class="fine">{" · ".join(context)}</p>
            <dl>{"".join(labels)}</dl>
          </article>""")
    return '<div class="card-grid">' + "".join(cards) + "</div>" if cards else ""


def phase_table(phases, columns):
    if not phases:
        return '<p class="fine">未取得任务阶段清单。</p>'
    headers = ["阶段", "耗时", *(columns or ["记录"])]
    rows = []
    for row in phases:
        label = escape(row["label"])
        records = row.get("records") if columns else [row["note"]]
        if records is None:
            records = ["未知"] * len(columns)
        if not isinstance(records, list) or len(records) != len(headers) - 2:
            raise ValueError("Each phase must have one record per phase column")
        cells = "".join(f'<td>{escape(record or "未知")}</td>' for record in records)
        note = ""
        if columns and row["note"]:
            note = f'<small>{escape(row["note"])}</small>'
        highlighted = "实现" in row["label"] or "implement" in row["label"].casefold().split()
        css_class = ' class="implement"' if highlighted else ""
        rows.append(
            f'<tr{css_class}><th scope="row">{escape(row["number"])} {label}{note}</th>'
            f'<td>{duration(row["seconds"])}</td>{cells}</tr>'
        )
    head = "".join(f'<th scope="col">{escape(header)}</th>' for header in headers)
    return f'<div class="table-scroll"><table><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def report_details(data, usage):
    cards = "".join(f"""
      <article class="card incident">
        <h4>{escape(row["label"])}</h4>
        <strong class="value">{escape(row["value"])}</strong>
        <p>{escape(row.get("result", ""))}</p>
        <p class="fine">{escape(row.get("note", ""))}</p>
      </article>""" for row in data.get("incidents", []))
    incidents = f'<div class="card-grid">{cards}</div>' if cards else f'<ul>{entries(data["bottlenecks"])}</ul>'
    observations = entries(data["bad_taste"])
    usage_notes = entries(data["usage"])
    coverage = f'<p class="fine">{escape(usage["coverage"])}</p>' if usage.get("coverage") else ""
    evidence = "".join(
        f'<li><strong>{escape(item["id"])} · {escape(item["supports"])}</strong>'
        f'<span>{escape(item["path"])} · {escape(item["locator"])}</span></li>'
        for item in data["sources"]
    )
    return f"""
    <details class="report-details">
      <summary>展开记录、其他阻塞和精确用量</summary>
      <nav aria-label="明细导航">
        <a href="#incidents">其他阻塞</a><a href="#usage">精确用量</a><a href="#phases">阶段记录</a>
      </nav>
      <section id="incidents">
        <h2>其他阻塞</h2>
        {incidents}
        {f'<h3>新观察</h3><ul>{observations}</ul>' if observations else ''}
      </section>
      <section id="usage">
        <h2>精确用量 <span class="status">{escape(usage.get("cost") or "费用未知")}</span></h2>
        {usage_cards(usage)}
        {coverage}
        {f'<ul class="fine">{usage_notes}</ul>' if usage_notes else ''}
      </section>
      <section id="phases">
        <h2>阶段记录</h2>
        <p class="fine">总跨度 · {escape(data["times"][0]["note"])}</p>
        <p class="fine">阶段窗口合计 <b>{duration(data["times"][2]["seconds"])}</b> · {escape(data["times"][2]["note"])}</p>
        {phase_table(data["phases"], data.get("phase_columns", []))}
        <h3>实现分工</h3>
        <ul>{entries(data["parallel"]) or "<li>分工证据不足。</li>"}</ul>
        {f'<h3>数据缺口</h3><ul>{entries(data["unknowns"])}</ul>' if data["unknowns"] else ''}
      </section>
      {f'<details class="evidence"><summary>证据来源</summary><ul>{evidence}</ul></details>' if evidence else ''}
    </details>"""


def render(data):
    validate(data)
    usage = data.get("token_usage", {})
    tokens = number(usage.get("total"))
    title = escape(data["title"])
    takeaway = f'<h2>{escape(data["takeaway"])}</h2>' if data.get("takeaway") else ""
    css = Path(__file__).with_name("report.css").read_text(encoding="utf-8")
    times = "".join(
        f'<div><span>{escape(row["label"])}</span><strong>{duration(row["seconds"])}</strong></div>'
        for row in data["times"][:2]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
<main>
  <header>
    <p class="eyebrow">Coding 效率评估</p>
    <h1>{title}</h1>
    <p class="fine">{escape(data["scope"])}</p>
  </header>
  <article>
    <section class="lead">{takeaway}<p>{escape(data["outcome"])}</p></section>
    {timeline(data.get("timeline", []))}
    <section class="metrics">
      <h2>这次花了多少</h2>
      <div class="metrics-grid">
        {times}
        <div><span>已记录 Token</span><strong>{tokens}</strong></div>
      </div>
      <p class="fine">{escape(data["times"][1]["note"])}</p>
      {token_chart(usage, data["phases"])}
    </section>
    {report_details(data, usage)}
  </article>
</main>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    content = render(json.loads(args.data.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as target:
        target.write(content)
    print(args.output)


if __name__ == "__main__":
    main()
