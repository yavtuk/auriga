from collections import Counter, defaultdict
import datetime
from datetime import date, timedelta
from math import ceil
from os import path
from typing import List

import reportlab.rl_config
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.colors import PCMYKColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from testteamreports.data import operations as ops
from testteamreports.reports.storage import get_new_file_name

MAIN_FONT_NAME = 'Liberation Sans'
MAIN_FONT_FILE = 'fonts/LiberationSans-Regular.ttf'
H1_FONT_SIZE = 32
H2_FONT_SIZE = 18
AXIS_FONT_SIZE = 11

COLOR_GREEN = PCMYKColor(80, 0, 90, 0)
COLOR_RED = PCMYKColor(10, 80, 80, 0)
COLOR_WHITE = PCMYKColor(0, 0, 0, 0)
COLOR_GRAY = PCMYKColor(0, 0, 0, 50)
COLOR_BLACK = PCMYKColor(0, 0, 0, 100)


class PassState:
    # Numbers are significant to mark requirements by max()
    UNKNOWN = 0
    PASS = 1
    NOT_RUN = 2
    FAIL = 3


def _normalize(datas: List[List[int]]) -> List[List[int]]:
    """Convert numbers to % numbers adding up to 100"""
    result = [[] for _ in datas]
    for column in zip(*datas):
        total = sum(column)
        if total <= 0:
            norm_column = [0 for _ in column]
        else:
            # Should fix to make +/- when sum is not exactly 100, but drop it for now
            norm_column = [round(float(x * 100) / total) for x in column]

        for new_value, new_list in zip(norm_column, result):
            new_list.append(new_value)

    return result


def create_testrun_summary_pdf(testrun_id: int) -> str:
    ###################################
    # 1. Fetch data from the DB
    ###################################

    test_run = ops.get_test_run_by_id(testrun_id)
    test_cases = ops.get_all_tests_in_set(testrun_id)
    test_results = ops.get_all_test_results(testrun_id)
    all_requirements = ops.get_all_requirements()
    test_to_requirement = {
        case.name: [req.name for req in ops.get_all_requirements_for_test(case)]
        for case in test_cases}

    ###################################
    # 2. Data Analysis
    ###################################

    # Fill Pass/Fail states for tests and requirements
    testcases_passed_state = {case.name: PassState.NOT_RUN for case in test_cases}
    passed_by_date = defaultdict(lambda: 0)
    failed_by_date = defaultdict(lambda: 0)
    start_date = test_run.start_date
    end_date = test_run.end_date
    for test_result in test_results:
        result_date = test_result.date_time.date()
        if start_date <= result_date <= end_date:
            tc = test_result.test_case
            is_passed = test_result.is_passed
            testcases_passed_state[tc.name] = PassState.PASS if is_passed else PassState.FAIL

            if is_passed:
                passed_by_date[result_date] += 1
            else:
                failed_by_date[result_date] += 1

    # Prepare list of requirements
    # requirements_in_run = set()
    # for req_list in test_to_requirement.values():
    #     requirements_in_run.update(req_list)

    requirements_status_list = {req.name: [PassState.UNKNOWN] for req in all_requirements}
    for tc_name, tc_status in testcases_passed_state.items():
        for req_name in test_to_requirement[tc_name]:
            if req_name in requirements_status_list:
                requirements_status_list[req_name].append(tc_status)

    # Calculate Fail/NotRun/Pass for each requirement
    requirements_passed_state = {
        item[0]: max(item[1])
        for item in requirements_status_list.items()
    }

    # Calculate burndown timelines
    start_dt = datetime.datetime.combine(start_date, datetime.time.min)
    days = (end_date - start_date).days + 1
    not_run_timeline = [len(test_cases)]
    pass_timeline = [0]
    fail_timeline = [0]
    for day in range(0, days):
        today = (start_dt + timedelta(days=day)).date()
        passed_today = passed_by_date[today]
        failed_today = failed_by_date[today]
        not_run_timeline.append(not_run_timeline[-1] - passed_today - failed_today)
        pass_timeline.append(pass_timeline[-1] + passed_today)
        fail_timeline.append(fail_timeline[-1] + failed_today)

    # Drop initial values in timelines
    not_run_timeline = not_run_timeline[1:]
    pass_timeline = pass_timeline[1:]
    fail_timeline = fail_timeline[1:]

    # Make risk scale without gaps
    risk_levels = [req.risk for req in all_requirements]
    min_risk = min(risk_levels)
    max_risk = max(risk_levels)
    risk_levels = [risk for risk in range(min_risk, max_risk + 1)]

    # Risk pass/fail statistics
    risk_by_req_name = {req.name: req.risk for req in all_requirements}
    passed_by_risk = [0 for _ in risk_levels]
    failed_by_risk = [0 for _ in risk_levels]
    not_run_by_risk = [0 for _ in risk_levels]
    for req_name, req_status in requirements_passed_state.items():
        risk_value = risk_by_req_name[req_name]
        i = risk_value - min_risk
        if req_status == PassState.PASS:
            passed_by_risk[i] += 1
        elif req_status == PassState.FAIL:
            failed_by_risk[i] += 1
        elif req_status == PassState.NOT_RUN:
            not_run_by_risk[i] += 1

    ###################################
    # 3. Creation of the PDF
    ###################################

    file_path = get_new_file_name(extension=".pdf")
    c = init_pdf(file_path)

    # Add title
    c.setFont(MAIN_FONT_NAME, H1_FONT_SIZE)
    c.drawString(100, 770, 'TEST SUMMARY REPORT')
    c.setFont(MAIN_FONT_NAME, 18)
    c.drawString(100, 730, test_run.description)
    c.drawString(100, 700, '{} - {}'.format(start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y')))

    # Add Pass/Fail pie chart
    count = Counter(testcases_passed_state.values())
    chart = draw_pass_fail_piechart([count[PassState.PASS], count[PassState.FAIL], count[PassState.NOT_RUN]])
    pass_rate = round(100 * count[PassState.PASS] / len(testcases_passed_state))

    c.setFont(MAIN_FONT_NAME, 18)
    c.drawString(110, 650, 'Test Cases')
    c.drawString(110, 630, 'Pass Rate = {}%'.format(pass_rate))
    chart.drawOn(c, 100, 460)

    # Add requirement Pass/Fail pie chart
    count = Counter(requirements_passed_state.values())
    pass_rate = round(100 * count[PassState.PASS] / len(requirements_passed_state))
    chart = draw_req_coverage_piechart(
        [count[PassState.PASS], count[PassState.FAIL], count[PassState.NOT_RUN], count[PassState.UNKNOWN]])

    c.setFont(MAIN_FONT_NAME, 18)
    c.drawString(320, 650, 'Requirements')
    c.drawString(320, 630, 'Pass Rate = {}%'.format(pass_rate))
    chart.drawOn(c, 310, 460)

    # Add burndown
    chart = draw_test_burndown(
        not_run_timeline, pass_timeline, fail_timeline,
        start_date, end_date)

    c.setFont(MAIN_FONT_NAME, 18)
    c.drawString(110, 460, 'Test Set Burndown')
    chart.drawOn(c, 100, 305)

    # Add risk histogram
    chart = draw_req_risk_histogram(risk_levels, passed_by_risk, failed_by_risk, not_run_by_risk)

    c.setFont(MAIN_FONT_NAME, 18)
    c.drawString(110, 225, 'Pass Rate for Each Risk Level')
    chart.drawOn(c, 100, 75)

    c.save()

    return path.split(file_path)[1]


def register_fonts():
    font_path = path.join(path.dirname(__file__), MAIN_FONT_FILE)
    reportlab.rl_config.warnOnMissingFontGlyphs = 0
    pdfmetrics.registerFont(TTFont(MAIN_FONT_NAME, font_path))


def init_pdf(file_path: str) -> Canvas:
    c = Canvas(file_path)
    register_fonts()
    return c


def draw_pass_fail_piechart(passed_data: List[int]) -> Drawing:
    passed_data_labels = ['Passed', 'Failed', 'Not run']
    d = Drawing(width=200, height=200)
    pc = Pie()
    pc.x = 50
    pc.y = 50
    pc.width = 80
    pc.height = 80
    pc.slices[0].fillColor = COLOR_GREEN
    pc.slices[1].fillColor = COLOR_RED
    pc.slices[2].fillColor = COLOR_GRAY
    pc.direction = 'anticlockwise'
    pc.data = passed_data
    pc.labels = passed_data_labels
    pc.sideLabels = True
    pc.slices.fontName = MAIN_FONT_NAME
    pc.slices.fontSize = AXIS_FONT_SIZE
    d.add(pc)
    return d


def draw_req_coverage_piechart(passed_data: List[int]) -> Drawing:
    passed_data_labels = ['Passed', 'Failed', 'Not run', 'Not covered']
    d = Drawing(width=200, height=200)
    pc = Pie()
    pc.x = 50
    pc.y = 50
    pc.width = 80
    pc.height = 80
    pc.slices[0].fillColor = COLOR_GREEN
    pc.slices[1].fillColor = COLOR_RED
    pc.slices[2].fillColor = COLOR_GRAY
    pc.slices[3].fillColor = COLOR_WHITE
    pc.direction = 'anticlockwise'
    pc.data = passed_data
    pc.labels = passed_data_labels
    pc.sideLabels = True
    pc.slices.fontName = MAIN_FONT_NAME
    pc.slices.fontSize = AXIS_FONT_SIZE
    d.add(pc)
    return d


def draw_test_burndown(not_run_line: List[int],
                       passed_line: List[int],
                       falied_line: List[int],
                       start_date: date, end_date: date) -> Drawing:
    max_days = 10
    days = (end_date - start_date).days + 1
    assert days == \
           len(not_run_line) == \
           len(passed_line) == \
           len(falied_line), "Line data for burndown should be equal to number of days"

    step_days = 1
    if days > max_days:
        step_days = ceil(float(days) / max_days)

    step = timedelta(days=step_days)
    num_steps = int(ceil(float(days) / step_days))
    start_dt = datetime.datetime.combine(start_date, datetime.time.min)
    end_dt = datetime.datetime.combine(end_date, datetime.time.min)
    category_dates = [(start_dt + step * n) for n in range(0, num_steps)]
    line1_data = [not_run_line[step_days * n] for n in range(0, num_steps)]
    line2_data = [passed_line[step_days * n] for n in range(0, num_steps)]
    line3_data = [falied_line[step_days * n] for n in range(0, num_steps)]
    if category_dates[-1] < end_dt:
        category_dates.append(end_dt)
        line1_data.append(not_run_line[-1])
        line2_data.append(passed_line[-1])
        line3_data.append(falied_line[-1])

    d = Drawing(width=350, height=140)
    lc = HorizontalLineChart()
    lc.x = 0
    lc.y = 0
    lc.width = 350
    lc.height = 140
    lc.data = [line1_data, line2_data, line3_data]
    lc.lines[0].strokeColor = COLOR_GRAY
    lc.lines[1].strokeColor = COLOR_GREEN
    lc.lines[2].strokeColor = COLOR_RED
    lc.joinedLines = 1
    lc.lines.strokeWidth = 2
    lc.valueAxis.valueMin = 0
    lc.valueAxis.valueMax = max(not_run_line) + 1
    lc.valueAxis.labels.fontName = MAIN_FONT_NAME
    lc.valueAxis.labels.fontSize = AXIS_FONT_SIZE
    lc.categoryAxis.categoryNames = [next_date.strftime('%Y-%m-%d')
                                     for next_date in category_dates]
    lc.categoryAxis.labels.fontName = MAIN_FONT_NAME
    lc.categoryAxis.labels.fontSize = AXIS_FONT_SIZE
    lc.categoryAxis.labels.dy = -15
    lc.categoryAxis.labels.angle = 30
    d.add(lc)
    return d


def draw_req_risk_histogram(risk_values: List[int],
                            passed_by_risk: List[int],
                            failed_by_risk: List[int],
                            not_run_by_risk: List[int]) -> Drawing:
    d = Drawing(width=350, height=130)
    vbc = VerticalBarChart()
    vbc.x = 0
    vbc.y = 0
    vbc.width = 350
    vbc.height = 130
    vbc.data = _normalize([passed_by_risk, failed_by_risk, not_run_by_risk])
    vbc.bars[0].fillColor = COLOR_GREEN
    vbc.bars[1].fillColor = COLOR_RED
    vbc.bars[2].fillColor = COLOR_GRAY
    vbc.valueAxis.valueMin = 0
    vbc.valueAxis.valueMax = 110
    vbc.valueAxis.valueStep = 20
    vbc.valueAxis.labels.fontName = MAIN_FONT_NAME
    vbc.valueAxis.labels.fontSize = AXIS_FONT_SIZE
    vbc.categoryAxis.categoryNames = [str(x) for x in risk_values]
    vbc.categoryAxis.style = 'stacked'
    vbc.categoryAxis.labels.fontName = MAIN_FONT_NAME
    vbc.categoryAxis.labels.fontSize = AXIS_FONT_SIZE
    d.add(vbc)
    return d
