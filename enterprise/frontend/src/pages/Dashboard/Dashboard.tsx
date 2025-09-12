import React, { useState, useMemo } from 'react';
import { Row, Col, Card, Statistic, Select, DatePicker, Space, Typography, Spin } from 'antd';
import { 
  DollarOutlined, 
  TrendingUpOutlined, 
  AlertOutlined,
  CloudOutlined,
  TeamOutlined,
  ProjectOutlined
} from '@ant-design/icons';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, 
         XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import dayjs from 'dayjs';
import { motion } from 'framer-motion';

import { useCostData } from '../../hooks/useCostData';
import { useBusinessMetrics } from '../../hooks/useBusinessMetrics';
import { formatCurrency, formatNumber } from '../../utils/formatters';
import { CHART_COLORS } from '../../constants/charts';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

// Mock data for demonstration
const mockCostTrend = [
  { date: '2024-01-01', cost: 12500, forecast: 12000 },
  { date: '2024-01-02', cost: 13200, forecast: 12300 },
  { date: '2024-01-03', cost: 11800, forecast: 12600 },
  { date: '2024-01-04', cost: 14100, forecast: 12900 },
  { date: '2024-01-05', cost: 13500, forecast: 13200 },
  { date: '2024-01-06', cost: 15200, forecast: 13500 },
  { date: '2024-01-07', cost: 14800, forecast: 13800 },
];

const mockServiceCosts = [
  { name: 'Compute (EC2)', cost: 45600, percentage: 35 },
  { name: 'Storage (S3)', cost: 23400, percentage: 18 },
  { name: 'Database (RDS)', cost: 18200, percentage: 14 },
  { name: 'Network', cost: 15600, percentage: 12 },
  { name: 'AI/ML', cost: 13000, percentage: 10 },
  { name: 'Others', cost: 14200, percentage: 11 },
];

const mockTeamCosts = [
  { team: 'Engineering', cost: 78500, budget: 85000 },
  { team: 'Data Science', cost: 45200, budget: 50000 },
  { team: 'DevOps', cost: 32100, budget: 35000 },
  { team: 'QA', cost: 18900, budget: 25000 },
  { team: 'Infrastructure', cost: 55400, budget: 60000 },
];

const mockAnomalies = [
  { id: 1, type: 'Cost Spike', service: 'EC2', severity: 'high', impact: 25.5 },
  { id: 2, type: 'Usage Drop', service: 'S3', severity: 'medium', impact: -15.2 },
  { id: 3, type: 'Idle Resources', service: 'RDS', severity: 'low', impact: 8.7 },
];

interface DashboardProps {}

const Dashboard: React.FC<DashboardProps> = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(7, 'day'),
    dayjs()
  ]);

  // Hooks for data fetching
  const { data: costData, loading: costLoading } = useCostData(dateRange);
  const { data: businessMetrics, loading: metricsLoading } = useBusinessMetrics(dateRange);

  const isLoading = costLoading || metricsLoading;

  // Computed metrics
  const totalCost = useMemo(() => {
    return mockServiceCosts.reduce((sum, item) => sum + item.cost, 0);
  }, []);

  const costTrend = useMemo(() => {
    const current = totalCost;
    const previous = current * 0.85; // Mock previous period
    return ((current - previous) / previous) * 100;
  }, [totalCost]);

  const efficiency = useMemo(() => {
    return 78.5; // Mock efficiency score
  }, []);

  const activeAccounts = useMemo(() => {
    return 15; // Mock active cloud accounts
  }, []);

  // Handle time range change
  const handleTimeRangeChange = (value: string) => {
    setTimeRange(value);
    const now = dayjs();
    let start = now;
    
    switch (value) {
      case '1d':
        start = now.subtract(1, 'day');
        break;
      case '7d':
        start = now.subtract(7, 'day');
        break;
      case '30d':
        start = now.subtract(30, 'day');
        break;
      case '90d':
        start = now.subtract(90, 'day');
        break;
      default:
        start = now.subtract(7, 'day');
    }
    
    setDateRange([start, now]);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <Title level={2} className="!mb-2">Cloud Cost Dashboard</Title>
          <Text type="secondary">
            Monitor and optimize your multi-cloud spending in real-time
          </Text>
        </div>
        
        <Space>
          <Select
            value={timeRange}
            onChange={handleTimeRangeChange}
            style={{ width: 120 }}
          >
            <Select.Option value="1d">Last 24h</Select.Option>
            <Select.Option value="7d">Last 7 days</Select.Option>
            <Select.Option value="30d">Last 30 days</Select.Option>
            <Select.Option value="90d">Last 90 days</Select.Option>
          </Select>
          
          <RangePicker
            value={dateRange}
            onChange={(dates) => dates && setDateRange(dates)}
          />
        </Space>
      </div>

      {/* Key Metrics */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <Statistic
                title="Total Cost"
                value={totalCost}
                formatter={(value) => formatCurrency(Number(value))}
                prefix={<DollarOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
              <div className="mt-2">
                <Text type={costTrend >= 0 ? 'danger' : 'success'}>
                  {costTrend >= 0 ? '+' : ''}{costTrend.toFixed(1)}% vs last period
                </Text>
              </div>
            </Card>
          </motion.div>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card>
              <Statistic
                title="Cost Efficiency"
                value={efficiency}
                suffix="%"
                prefix={<TrendingUpOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
              <div className="mt-2">
                <Text type="success">
                  +2.3% improvement this month
                </Text>
              </div>
            </Card>
          </motion.div>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <Statistic
                title="Active Alerts"
                value={mockAnomalies.length}
                prefix={<AlertOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
              <div className="mt-2">
                <Text type="warning">
                  {mockAnomalies.filter(a => a.severity === 'high').length} high priority
                </Text>
              </div>
            </Card>
          </motion.div>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card>
              <Statistic
                title="Cloud Accounts"
                value={activeAccounts}
                prefix={<CloudOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
              <div className="mt-2">
                <Text type="secondary">
                  Across 4 cloud providers
                </Text>
              </div>
            </Card>
          </motion.div>
        </Col>
      </Row>

      {/* Charts Row 1 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card title="Cost Trend & Forecast" className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockCostTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tickFormatter={(value) => dayjs(value).format('MMM DD')} />
                  <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      formatCurrency(value),
                      name === 'cost' ? 'Actual Cost' : 'Forecast'
                    ]}
                    labelFormatter={(value) => dayjs(value).format('MMM DD, YYYY')}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="cost" 
                    stroke="#1890ff" 
                    strokeWidth={3}
                    dot={{ fill: '#1890ff', strokeWidth: 2, r: 4 }}
                    name="Actual Cost"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="forecast" 
                    stroke="#52c41a" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                    name="Forecast"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </motion.div>
        </Col>

        <Col xs={24} lg={8}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card title="Cost by Service" className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={mockServiceCosts}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    paddingAngle={2}
                    dataKey="cost"
                  >
                    {mockServiceCosts.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </motion.div>
        </Col>
      </Row>

      {/* Charts Row 2 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <Card title="Team Cost vs Budget" className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mockTeamCosts} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="team" />
                  <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      formatCurrency(value),
                      name === 'cost' ? 'Actual Cost' : 'Budget'
                    ]}
                  />
                  <Legend />
                  <Bar dataKey="budget" fill="#e6f7ff" name="Budget" />
                  <Bar dataKey="cost" fill="#1890ff" name="Actual Cost" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </motion.div>
        </Col>

        <Col xs={24} lg={8}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.7 }}
          >
            <Card title="Cost Anomalies" className="h-80">
              <div className="space-y-4">
                {mockAnomalies.map((anomaly) => (
                  <div 
                    key={anomaly.id}
                    className={`p-3 rounded-lg border-l-4 ${
                      anomaly.severity === 'high' 
                        ? 'border-red-500 bg-red-50' 
                        : anomaly.severity === 'medium'
                        ? 'border-yellow-500 bg-yellow-50'
                        : 'border-blue-500 bg-blue-50'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <Text strong>{anomaly.type}</Text>
                        <div className="text-sm text-gray-600">
                          {anomaly.service}
                        </div>
                      </div>
                      <div className="text-right">
                        <Text 
                          type={anomaly.impact > 0 ? 'danger' : 'success'}
                          strong
                        >
                          {anomaly.impact > 0 ? '+' : ''}{anomaly.impact}%
                        </Text>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </motion.div>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;