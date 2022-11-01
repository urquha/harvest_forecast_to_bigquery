import httpx
import os

headers = {
            'Forecast-Account-ID': os.environ.get("FORECAST_ACCOUNT_ID"),
            'Authorization': 'Bearer {}'.format(os.environ.get("FORECAST_ACCESS_TOKEN")),
            'User-Agent': 'Forecast Harvest Python API',
        }

x = httpx.post("https://api.forecastapp.com/assignments/9843892389", headers=headers, data={})
import pytest
pytest.set_trace()
print(x)