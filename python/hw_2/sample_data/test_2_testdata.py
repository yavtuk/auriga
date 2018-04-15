requirements_data = [
    {"name": "TSR_01", "risk": 5},
    {"name": "TSR_02", "risk": 3},
    {"name": "TSR_03", "risk": 2},
    {"name": "TSR_04", "risk": 1},
    {"name": "TSR_05", "risk": 1},
    {"name": "TSR_06", "risk": 2},
]

test_cases_data = [
    # Одно требование
    {"name": "TC_0001", "requirements": ["TSR_01"]},
    # Покрытие требований не заведено в системе
    {"name": "TC_0002", "requirements": []},
    # Несколько требований, разные уровни риска
    {"name": "TC_0003", "requirements": ["TSR_02", "TSR_03", "TSR_04"]},
    # Несколько требований, один уровень риска
    {"name": "TC_0004", "requirements": ["TSR_04", "TSR_05"]},
    # Тест, который не будет включен в набор
    {"name": "TC_0005", "requirements": ["TSR_05", "TSR_06"]},
]

test_run_data = {
    "start_date": "2018-03-12",
    "end_date": "2018-03-19",
    "description": "Regression Testing",
    "test_cases": ["TC_0001", "TC_0002", "TC_0003", "TC_0004"]
}

# Результаты для test_run_id, соответствующему созданному test_run
test_result_data = [
    {"name": "TC_0001", "is_passed": True, "date_time": "2018-03-13T00:00:00Z"},
    {"name": "TC_0002", "is_passed": True, "date_time": "2018-03-13T23:59:59Z"},
    {"name": "TC_0003", "is_passed": False, "date_time": "2018-03-15T10:43:21Z"},
    # TC_0004 не выполнен
    # Невалидная запись
    {"name": "TC_0005", "is_passed": True, "date_time": "2018-03-20T00:00:00Z"},
]
