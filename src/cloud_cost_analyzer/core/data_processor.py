"""
AWS Data Processor Module
"""
import pandas as pd
from typing import Dict, Any

from .base_data_processor import BaseDataProcessor
from ..utils.logger import get_logger

logger = get_logger()


class DataProcessor(BaseDataProcessor):
    """Processes AWS cost data."""

    def process(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Parses AWS cost data from raw API response into a standardized DataFrame.
        """
        if not raw_data or 'ResultsByTime' not in raw_data:
            logger.warning("AWS cost data is empty or in an invalid format.")
            return pd.DataFrame()

        parsed_data = []
        try:
            for result in raw_data.get('ResultsByTime', []):
                time_period = result['TimePeriod']['Start']
                for group in result.get('Groups', []):
                    keys = group['Keys']
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])

                    if cost < self.cost_threshold:
                        continue

                    parsed_data.append({
                        'Date': time_period,
                        'Service': keys[0] if len(keys) > 0 else 'Unknown',
                        'Region': keys[1] if len(keys) > 1 else 'Unknown',
                        'Cost': cost,
                        'Currency': group['Metrics']['UnblendedCost']['Unit'],
                        'Provider': 'aws',
                        'UsageType': keys[2] if len(keys) > 2 else 'Unknown',
                    })
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse AWS data due to key/index error: {e}")
            return pd.DataFrame()

        if not parsed_data:
            return pd.DataFrame()

        df = pd.DataFrame(parsed_data)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        logger.info(f"Processed {len(df)} records for AWS.")
        return self.filter_cost_data(df)
