"""
Base class for all data processors.
"""
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, List


class BaseDataProcessor(ABC):
    """Abstract base class for cloud cost data processors."""

    def __init__(self, cost_threshold: float = 0.01):
        """
        Initializes the data processor.
        Args:
            cost_threshold: The minimum cost threshold to consider.
        """
        self.cost_threshold = cost_threshold

    @abstractmethod
    def process(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Processes raw cost data from a cloud provider into a standardized DataFrame.

        Args:
            raw_data: The raw dictionary data from the cloud provider's API.

        Returns:
            A standardized pandas DataFrame with cost information.
        """
        pass

    def filter_cost_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters the cost data DataFrame.
        """
        if df.empty:
            return df

        # Filter out records with costs below the threshold
        filtered_df = df[df['Cost'] >= self.cost_threshold].copy()

        # Filter out entries with 'NoRegion' if the column exists
        if 'Region' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Region'] != 'NoRegion'].copy()

        return filtered_df

    def analyze_costs_by_service(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyzes costs by service.
        """
        if df.empty:
            return pd.DataFrame()

        service_stats = df.groupby('Service').agg(
            Cost_sum=('Cost', 'sum'),
            Cost_mean=('Cost', 'mean'),
            Record_count=('Cost', 'count')
        ).round(4)

        service_stats.columns = ['总费用', '平均费用', '记录数']
        return service_stats.sort_values('总费用', ascending=False)

    def analyze_costs_by_region(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyzes costs by region.
        """
        if df.empty or 'Region' not in df.columns:
            return pd.DataFrame()

        region_stats = df.groupby('Region').agg(
            Cost_sum=('Cost', 'sum'),
            Cost_mean=('Cost', 'mean'),
            Record_count=('Cost', 'count')
        ).round(4)

        region_stats.columns = ['总费用', '平均费用', '记录数']
        return region_stats.sort_values('总费用', ascending=False)

    def get_cost_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Gets a summary of the costs.
        """
        if df.empty:
            return {
                'total_cost': 0.0,
                'avg_daily_cost': 0.0,
                'max_daily_cost': 0.0,
                'min_daily_cost': 0.0,
                'record_count': 0,
                'date_range': 0,
                'currency': 'USD' # Default currency
            }

        daily_costs = df.groupby(pd.to_datetime(df['Date']).dt.date)['Cost'].sum()
        currency = df['Currency'].iloc[0] if 'Currency' in df.columns and not df.empty else 'USD'

        return {
            'total_cost': df['Cost'].sum(),
            'avg_daily_cost': daily_costs.mean(),
            'max_daily_cost': daily_costs.max(),
            'min_daily_cost': daily_costs.min(),
            'record_count': len(df),
            'date_range': (df['Date'].max() - df['Date'].min()).days + 1 if not df.empty else 0,
            'currency': currency
        }

    def detect_cost_anomalies(self, df: pd.DataFrame, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detects cost anomalies.
        """
        if df.empty:
            return []

        daily_costs = df.groupby(pd.to_datetime(df['Date']).dt.date)['Cost'].sum()
        if len(daily_costs) < 3:
            return []

        mean_cost = daily_costs.mean()
        std_cost = daily_costs.std()
        if std_cost == 0:
            return []

        anomalies = []
        for date, cost in daily_costs.items():
            deviation = (cost - mean_cost) / std_cost
            if abs(deviation) > threshold:
                anomalies.append({
                    'date': date,
                    'cost': cost,
                    'deviation': deviation,
                    'type': 'high' if cost > mean_cost else 'low'
                })
        return anomalies

    def get_top_services(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        Gets the top N services by cost.
        """
        service_stats = self.analyze_costs_by_service(df)
        return service_stats.head(top_n)

    def get_top_regions(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        Gets the top N regions by cost.
        """
        region_stats = self.analyze_costs_by_region(df)
        return region_stats.head(top_n)
