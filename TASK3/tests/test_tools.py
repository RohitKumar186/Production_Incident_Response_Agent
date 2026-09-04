from TASK3.tools.log_search import search_logs
from TASK3.tools.metrics_reader import read_metrics
from TASK3.tools.database_reader import read_database
from TASK3.tools.network_checker import check_network


def test_log_search():
    result = search_logs("order-api")

    assert result.status == "SUCCESS"
    assert isinstance(result.data, list)
    assert len(result.data) > 0


def test_metrics_reader():
    result = read_metrics("order-api")

    assert result.status == "SUCCESS"
    assert result.data["service"] == "order-api"


def test_database_reader():
    result = read_database()

    assert result.status == "SUCCESS"
    assert "queries" in result.data


def test_network_checker():
    result = check_network("order-api")

    assert result.status == "SUCCESS"
    assert result.data["service"] == "order-api"