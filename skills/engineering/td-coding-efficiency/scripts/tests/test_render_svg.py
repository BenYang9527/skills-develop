"""Contract tests for the candidate renderer; no third-party dependencies.

Run: python3 -B -m unittest discover -s <test-directory> -p test_render_svg.py -v
The CLI overwrite test targets a temporary sentinel file and verifies its bytes
remain unchanged. The temporary directory is removed automatically.
"""

import argparse
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET


sys.dont_write_bytecode = True
TEST_DIRECTORY = Path(__file__).resolve().parent
SCRIPT_CANDIDATES = (
    TEST_DIRECTORY.parent / "render_svg.py",  # Installed under scripts/tests/.
    TEST_DIRECTORY / "td-coding-efficiency/scripts/render_svg.py",  # Candidate location.
)
SCRIPT = next((path for path in SCRIPT_CANDIDATES if path.is_file()), None)
if SCRIPT is None:
    raise FileNotFoundError(f"Cannot locate render_svg.py beside tests: {SCRIPT_CANDIDATES}")
SPEC = importlib.util.spec_from_file_location("candidate_render_svg", SCRIPT)
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)
SVG = "{http://www.w3.org/2000/svg}"


def facts():
    """Small valid report with literal contract labels and seven unique stages."""
    return {
        "title": "任务效率",
        "scope": "仅本轮交付",
        "outcome": "已交付，证据边界明确",
        "times": [
            {"label": "总跨度", "seconds": 3661, "note": "首尾时间可核验"},
            {"label": "可观察执行时间", "seconds": None, "note": "无可核验数据"},
            {"label": "阶段窗口合计", "seconds": 0, "note": "已观察为零"},
        ],
        "phases": [
            {"number": f"{number:02}", "seconds": None, "note": "阶段时间未知"}
            for number in range(1, 8)
        ],
        "parallel": [],
        "usage": [],
        "bottlenecks": [],
        "bad_taste": [],
        "unknowns": [],
        "sources": [
            {"id": "E1", "path": "/evidence/report.json", "locator": "L1", "supports": "交付事实"}
        ],
    }


def parsed(data):
    return ET.fromstring(renderer.render(data))


def visible_text(root):
    return [node.text or "" for node in root.iter(f"{SVG}text")]


class DurationContractTests(unittest.TestCase):
    def test_unknown_is_distinct_from_observed_zero(self):
        self.assertEqual(renderer.duration(None), "未知")
        self.assertEqual(renderer.duration(0), "0h 00m 00s")
        content = " ".join(visible_text(parsed(facts())))
        self.assertRegex(content, r"可观察执行时间\s+未知")
        self.assertRegex(content, r"阶段窗口合计\s+0h 00m 00s")

    def test_positive_duration_has_hour_minute_second_units(self):
        self.assertEqual(renderer.duration(3661), "1h 01m 01s")
        self.assertRegex(" ".join(visible_text(parsed(facts()))), r"总跨度\s+1h 01m 01s")

    def test_invalid_seconds_rejected_by_duration_and_every_report_row(self):
        for invalid in (-1, -0.01, float("nan"), float("inf"), -float("inf"), True, False, "0"):
            with self.subTest(value=repr(invalid), entry="duration"):
                with self.assertRaises(ValueError):
                    renderer.duration(invalid)
            for group in ("times", "phases"):
                with self.subTest(value=repr(invalid), group=group):
                    data = facts()
                    data[group][-1]["seconds"] = invalid
                    with self.assertRaises(ValueError):
                        renderer.render(data)


class TextAndXmlTests(unittest.TestCase):
    def test_xml_metacharacters_remain_text_and_cannot_inject_elements(self):
        value = '<s>&"\'中</s>'
        data = facts()
        for key in ("title", "scope", "outcome"):
            data[key] = value
        for key in ("parallel", "usage", "bottlenecks", "bad_taste", "unknowns"):
            data[key] = [value]
        data["times"][0]["note"] = value
        data["phases"][0]["note"] = value
        data["sources"][0].update(id="E<&>", supports=value)
        root = parsed(data)
        self.assertEqual(root.find(f"{SVG}title").text, value)
        self.assertGreaterEqual(visible_text(root).count(value), 10)
        self.assertIn(f"[E<&>] {value}", visible_text(root))
        self.assertFalse(any(node.tag in ("s", f"{SVG}s") for node in root.iter()))

    def test_cjk_and_latin_wrapping_reserves_two_units_per_character(self):
        self.assertEqual(renderer.wrap("中文测试中", 4), ["中文", "测试", "中"])
        self.assertEqual(renderer.wrap("ab中文cd", 4), ["ab", "中文", "cd"])
        self.assertEqual(renderer.wrap("WMWMW", 4), ["WM", "WM", "W"])
        self.assertEqual(renderer.wrap("WMW", 5), ["WM", "W"])

    def test_short_numbers_and_ids_move_intact_at_space_boundaries(self):
        for token in ("12345", "ID-42"):
            with self.subTest(token=token, entry="wrap"):
                value = "WWWW " + token
                lines = renderer.wrap(value, 12)
                self.assertEqual(lines, ["WWWW ", token])
                self.assertEqual("".join(lines), value)
            for entry, prefix, size, x in (
                ("body", "M" * 50 + " ", "18", "52"),
                ("card", "W" * 15 + " ", "15", "69"),
            ):
                with self.subTest(token=token, entry=entry):
                    data = facts()
                    if entry == "body":
                        data["parallel"] = [prefix + token]
                    else:
                        data["times"][0]["note"] = prefix + token
                    lines = [
                        node.text for node in parsed(data).iter(f"{SVG}text")
                        if node.attrib["font-size"] == size
                        and node.attrib["x"] == x
                        and node.text in (prefix, token)
                    ]
                    self.assertEqual(lines, [prefix, token])
                    self.assertEqual("".join(lines), prefix + token)

    def test_wide_latin_body_and_indented_notes_stay_within_width_budgets(self):
        # 1.1em reserves room for W/M: 52 chars at 18px, 56 at 16px.
        for char in ("W", "M"):
            for field, size, x, limit, budget in (
                ("parallel", 18, 52, 52, 1036),
                ("phase-note", 16, 90, 56, 998),
            ):
                for count in (limit - 1, limit, limit + 1, limit * 5 + 3):
                    with self.subTest(char=char, field=field, count=count):
                        data = facts()
                        value = char * count
                        if field == "parallel":
                            data["parallel"] = [value]
                        else:
                            data["phases"][0]["note"] = value
                        nodes = [
                            node for node in parsed(data).iter(f"{SVG}text")
                            if node.attrib["font-size"] == str(size)
                            and node.attrib["x"] == str(x)
                            and node.text and set(node.text) == {char}
                        ]
                        self.assertEqual("".join(node.text for node in nodes), value)
                        self.assertEqual(len(nodes), (count + limit - 1) // limit)
                        for node in nodes:
                            self.assertLessEqual(len(node.text), limit)
                            self.assertLessEqual(len(node.text) * size * 1.1, budget)
                            self.assertLessEqual(x + len(node.text) * size * 1.1, 1088)

    def test_wide_latin_card_notes_respect_298_pixel_content_width(self):
        # At 15px, 18 wide characters reserve 297px; 19 must wrap.
        for char in ("W", "M"):
            for count in (17, 18, 19, 93):
                with self.subTest(char=char, count=count):
                    data = facts()
                    value = char * count
                    for row in data["times"]:
                        row["note"] = value
                    root = parsed(data)
                    cards = [node for node in root.iter(f"{SVG}rect") if node.attrib.get("width") == "332"]
                    self.assertEqual(len(cards), 3)
                    for card in cards:
                        content_x = float(card.attrib["x"]) + 17
                        content_right = float(card.attrib["x"]) + 332 - 17
                        nodes = [
                            node for node in root.iter(f"{SVG}text")
                            if node.attrib["font-size"] == "15"
                            and float(node.attrib["x"]) == content_x
                            and node.text and set(node.text) == {char}
                        ]
                        self.assertEqual("".join(node.text for node in nodes), value)
                        self.assertEqual(len(nodes), (count + 17) // 18)
                        for node in nodes:
                            self.assertLessEqual(len(node.text), 18)
                            self.assertLessEqual(len(node.text) * 15 * 1.1, 298)
                            self.assertLessEqual(content_x + len(node.text) * 15 * 1.1, content_right)
                            self.assertLess(float(node.attrib["y"]), float(card.attrib["y"]) + float(card.attrib["height"]))

    def test_long_unbroken_text_wraps_and_report_height_fits_every_line(self):
        value = "唯一长标识" + "X" * 1000 + "末尾"
        data = facts()
        data["parallel"] = [value]
        root = parsed(data)
        rows = visible_text(root)
        first = next(i for i, line in enumerate(rows) if line.startswith("唯一长标识"))
        pieces = []
        for line in rows[first:]:
            pieces.append(line)
            if line.endswith("末尾"):
                break
        self.assertGreater(len(pieces), 5)
        self.assertEqual("".join(pieces), value)
        self.assertTrue(all(len(line) < 110 for line in pieces))
        height = int(root.attrib["height"])
        self.assertEqual(root.attrib["viewBox"], f"0 0 1140 {height}")
        self.assertGreater(height, int(parsed(facts()).attrib["height"]))
        self.assertTrue(all(float(node.attrib["y"]) < height for node in root.iter(f"{SVG}text")))

    def test_explicit_newlines_are_preserved_and_normalized(self):
        self.assertEqual(renderer.wrap("第一行\r\n\r第二行\n", 40), ["第一行", "", "第二行", ""])

    def test_xml_control_characters_are_rejected_before_serialization(self):
        for invalid in ("\x00", "\x01", "\x0b", "\x1f"):
            with self.subTest(codepoint=ord(invalid)):
                data = facts()
                data["outcome"] = "前" + invalid + "后"
                with self.assertRaises(ValueError):
                    renderer.render(data)

    def test_other_xml_forbidden_codepoints_are_rejected(self):
        for invalid in ("\ud800", "\udfff", "\ufffe", "\uffff"):
            with self.subTest(codepoint=hex(ord(invalid))):
                data = facts()
                data["scope"] = "前" + invalid + "后"
                with self.assertRaises(ValueError):
                    renderer.render(data)


class ReportStructureTests(unittest.TestCase):
    def test_each_stage_number_and_name_is_rendered_once_in_order(self):
        root = parsed(facts())
        rows = visible_text(root)
        expected = [
            "01  澄清 Clarify    未知", "02  计划 Plan    未知",
            "03  实现 Implement    未知", "04  验证 Verify    未知",
            "05  文档 Docs    未知", "06  审查 Review    未知",
            "07  提交 Submit    未知",
        ]
        self.assertEqual([line for line in rows if line in expected], expected)

    def test_missing_duplicate_extra_and_reordered_stages_are_rejected(self):
        for mutation in ("missing", "duplicate", "extra", "reordered"):
            with self.subTest(mutation=mutation):
                data = facts()
                if mutation == "missing":
                    data["phases"].pop(3)
                elif mutation == "duplicate":
                    data["phases"][3]["number"] = "03"
                elif mutation == "extra":
                    data["phases"].append({"number": "08", "seconds": 0, "note": ""})
                else:
                    data["phases"][0], data["phases"][1] = data["phases"][1], data["phases"][0]
                with self.assertRaises(ValueError):
                    renderer.render(data)

    def test_time_labels_cannot_be_missing_duplicated_or_reordered(self):
        for labels in (("总跨度", "阶段窗口合计"), ("总跨度",) * 3,
                       ("阶段窗口合计", "可观察执行时间", "总跨度")):
            with self.subTest(labels=labels):
                data = facts()
                data["times"] = [{"label": label, "seconds": None, "note": ""} for label in labels]
                with self.assertRaises(ValueError):
                    renderer.render(data)

    def test_duplicate_evidence_ids_are_rejected(self):
        data = facts()
        data["sources"].append(dict(data["sources"][0], path="/another/source"))
        with self.assertRaises(ValueError):
            renderer.render(data)

    def test_report_data_is_not_mutated_by_rendering(self):
        data = facts()
        original = deepcopy(data)
        renderer.render(data)
        self.assertEqual(data, original)


class CliOutputProtectionTests(unittest.TestCase):
    def test_existing_output_is_not_overwritten(self):
        # A regression may corrupt only disposable data, never the test source.
        with tempfile.TemporaryDirectory(prefix="task-efficiency-test-") as directory:
            output = Path(directory) / "existing-report.svg"
            sentinel = b"Existing report must survive.\x00\xff"
            output.write_bytes(sentinel)
            source = Mock()
            source.read_text.return_value = json.dumps(facts(), ensure_ascii=False)
            args = argparse.Namespace(data=source, output=output)
            with patch.object(argparse.ArgumentParser, "parse_args", return_value=args), \
                    patch("sys.stdout", new_callable=io.StringIO) as stdout:
                with self.assertRaises(FileExistsError):
                    renderer.main()
                self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(output.read_bytes(), sentinel)

    def test_invalid_input_cannot_touch_the_output(self):
        data = facts()
        data["phases"].pop()
        source = Mock()
        source.read_text.return_value = json.dumps(data)
        output = Mock()
        args = argparse.Namespace(data=source, output=output)
        with patch.object(argparse.ArgumentParser, "parse_args", return_value=args):
            with self.assertRaises(ValueError):
                renderer.main()
        output.parent.mkdir.assert_not_called()
        output.open.assert_not_called()


if __name__ == "__main__":
    unittest.main()
