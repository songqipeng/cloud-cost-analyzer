"""
Aliyun Data Processor Module
"""
import pandas as pd
from typing import Dict, Any

from .base_data_processor import BaseDataProcessor
from ..utils.logger import get_logger

logger = get_logger()


class AliyunDataProcessor(BaseDataProcessor):
    """Processes Aliyun cost data."""

    def process(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Parses Aliyun cost data from raw API response into a standardized DataFrame.
        """
        if not raw_data:
            logger.warning("Aliyun cost data is empty.")
            return pd.DataFrame()

        all_records = []
        try:
            # Prefer instance-level data
            instance_data = raw_data.get('instance_data', [])
            if instance_data:
                for item in instance_data:
                    all_records.append({
                        'Date': item.get('billing_date', ''),
                        'Service': item.get('product_name', 'Unknown'),
                        'Region': item.get('region', 'Unknown'),
                        'Cost': float(item.get('pretax_amount', 0)),
                        'Currency': item.get('currency', 'CNY'),
                        'Provider': 'aliyun',
                        'ResourceId': item.get('instance_id', ''),
                    })
            # Fallback to product-level data
            else:
                product_data = raw_data.get('product_data', [])
                for item in product_data:
                    all_records.append({
                        'Date': item.get('billing_date', ''),
                        'Service': item.get('product_name', 'Unknown'),
                        'Region': 'Unknown',  # Product level data may not have region
                        'Cost': float(item.get('pretax_amount', 0)),
                        'Currency': item.get('currency', 'CNY'),
                        'Provider': 'aliyun',
                        'ResourceId': item.get('product_code', ''),
                    })

        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse Aliyun data due to key/value error: {e}")
            return pd.DataFrame()

        if not all_records:
            return pd.DataFrame()

        df = pd.DataFrame(all_records)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')
        df.dropna(subset=['Date', 'Cost'], inplace=True)
        df = df.sort_values('Date')

        logger.info(f"Processed {len(df)} records for Aliyun.")
        return self.filter_cost_data(df)
