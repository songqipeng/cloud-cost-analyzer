"""
Volcengine Data Processor Module
"""
import pandas as pd
from typing import Dict, Any

from .base_data_processor import BaseDataProcessor
from ..utils.logger import get_logger

logger = get_logger()


class VolcengineDataProcessor(BaseDataProcessor):
    """Processes Volcengine cost data."""

    def process(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Parses Volcengine cost data from raw API response into a standardized DataFrame.
        """
        if not raw_data or 'summary_data' not in raw_data:
            logger.warning("Volcengine cost data is empty or in an invalid format.")
            return pd.DataFrame()

        all_records = []
        try:
            for item in raw_data.get('summary_data', []):
                cost = float(item.get('total_cost', 0))
                if cost < self.cost_threshold:
                    continue

                all_records.append({
                    'Date': item.get('month', '') + '-01',  # Month-level data
                    'Service': item.get('product_name', 'Unknown'),
                    'Region': 'Unknown',  # Volcengine summary data does not provide region
                    'Cost': cost,
                    'Currency': 'CNY',
                    'Provider': 'volcengine',
                    'ResourceId': item.get('product_code', ''),
                })

        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse Volcengine data due to key/value error: {e}")
            return pd.DataFrame()

        if not all_records:
            return pd.DataFrame()

        df = pd.DataFrame(all_records)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date', 'Cost'], inplace=True)
        df = df.sort_values('Date')

        logger.info(f"Processed {len(df)} records for Volcengine.")
        return self.filter_cost_data(df)
