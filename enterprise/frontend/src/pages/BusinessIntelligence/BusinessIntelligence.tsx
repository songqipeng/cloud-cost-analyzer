import React, { useState, useMemo } from 'react';
import { Row, Col, Card, Statistic, Select, DatePicker, Space, Typography, Table, Tag, Progress, Spin, Button } from 'antd';
import { 
  DollarOutlined, 
  UserOutlined, 
  FunctionOutlined,
  TrophyOutlined,
  RiseOutlined,
  FallOutlined,
  AlertOutlined
} from '@ant-design/icons';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, ScatterChart, Scatter,
         XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import dayjs from 'dayjs';
import { motion } from 'framer-motion';

import { formatCurrency, formatNumber, formatPercentage } from '../../utils/formatters';
import { CHART_COLORS } from '../../constants/charts';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

// Mock data for unit economics
const mockUnitEconomics = [
  { metric: 'Cost per Customer', value: 45.67, change: -8.2, trend: 'down' },
  { metric: 'Cost per Feature', value: 1250.34, change: 5.1, trend: 'up' },
  { metric: 'Cost per Transaction', value: 0.23, change: -12.5, trend: 'down' },
  { metric: 'Revenue per Dollar Spent', value: 3.45, change: 15.2, trend: 'up' },
];

const mockCustomerCosts = [
  { 
    customerId: 'CUST-001', 
    name: 'TechCorp Ltd', 
    monthlyCost: 15420, 
    monthlyRevenue: 45000,
    margin: 65.7,
    transactions: 145000,
    costPerTransaction: 0.106
  },
  { 
    customerId: 'CUST-002', 
    name: 'DataFlow Inc', 
    monthlyCost: 8950, 
    monthlyRevenue: 28000,
    margin: 68.0,
    transactions: 89000,
    costPerTransaction: 0.101
  },
  { 
    customerId: 'CUST-003', 
    name: 'CloudNative Co', 
    monthlyCost: 22100, 
    monthlyRevenue: 62000,
    margin: 64.4,
    transactions: 198000,
    costPerTransaction: 0.112
  },
  { 
    customerId: 'CUST-004', 
    name: 'ScaleUp Solutions', 
    monthlyCost: 12300, 
    monthlyRevenue: 34500,
    margin: 64.3,
    transactions: 112000,
    costPerTransaction: 0.110
  },
  { 
    customerId: 'CUST-005', 
    name: 'Enterprise Labs', 
    monthlyCost: 35600, 
    monthlyRevenue: 98000,
    margin: 63.7,
    transactions: 345000,
    costPerTransaction: 0.103
  },
];

const mockFeatureCosts = [
  { feature: 'User Authentication', cost: 2340, revenue: 8500, usage: 145000, efficiency: 363 },
  { feature: 'Data Processing', cost: 15600, revenue: 45000, usage: 89000, efficiency: 288 },
  { feature: 'Analytics Engine', cost: 8900, revenue: 25000, usage: 67000, efficiency: 281 },
  { feature: 'File Storage', cost: 4500, revenue: 12000, usage: 234000, efficiency: 267 },
  { feature: 'API Gateway', cost: 3200, revenue: 9500, usage: 456000, efficiency: 297 },
  { feature: 'Machine Learning', cost: 12400, revenue: 38000, usage: 23000, efficiency: 306 },
];

const mockCostTrend = [
  { date: '2024-01-01', costPerCustomer: 48.5, costPerFeature: 1180, revenue: 285000 },
  { date: '2024-01-02', costPerCustomer: 47.2, costPerFeature: 1220, revenue: 290000 },
  { date: '2024-01-03', costPerCustomer: 46.8, costPerFeature: 1245, revenue: 295000 },
  { date: '2024-01-04', costPerCustomer: 45.9, costPerFeature: 1235, revenue: 298000 },
  { date: '2024-01-05', costPerCustomer: 45.1, costPerFeature: 1255, revenue: 302000 },
  { date: '2024-01-06', costPerCustomer: 44.8, costPerFeature: 1265, revenue: 305000 },
  { date: '2024-01-07', costPerCustomer: 45.67, costPerFeature: 1250, revenue: 308000 },
];

const mockROIData = [
  { segment: 'Enterprise', investment: 125000, return: 450000, roi: 260 },
  { segment: 'SMB', investment: 78000, return: 234000, roi: 200 },
  { segment: 'Startup', investment: 45000, return: 167000, roi: 271 },
  { segment: 'Government', investment: 89000, return: 298000, roi: 235 },
];

interface BusinessIntelligenceProps {}

const BusinessIntelligence: React.FC<BusinessIntelligenceProps> = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedMetric, setSelectedMetric] = useState('cost_per_customer');
  const [loading, setLoading] = useState(false);

  // Handle metric change
  const handleMetricChange = (value: string) => {
    setSelectedMetric(value);
    setLoading(true);
    setTimeout(() => setLoading(false), 1000); // Simulate API call
  };

  // Customer table columns
  const customerColumns = [
    {
      title: 'Customer',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => (
        <div>
          <div className="font-medium">{text}</div>
          <div className="text-xs text-gray-500">{record.customerId}</div>
        </div>
      ),
    },
    {
      title: 'Monthly Cost',
      dataIndex: 'monthlyCost',
      key: 'monthlyCost',
      render: (value: number) => formatCurrency(value),
      sorter: (a: any, b: any) => a.monthlyCost - b.monthlyCost,
    },
    {
      title: 'Monthly Revenue',
      dataIndex: 'monthlyRevenue',
      key: 'monthlyRevenue',
      render: (value: number) => formatCurrency(value),
      sorter: (a: any, b: any) => a.monthlyRevenue - b.monthlyRevenue,
    },
    {
      title: 'Gross Margin',
      dataIndex: 'margin',
      key: 'margin',
      render: (value: number) => (
        <span className={value >= 65 ? 'text-green-600' : value >= 60 ? 'text-yellow-600' : 'text-red-600'}>
          {value.toFixed(1)}%
        </span>
      ),
      sorter: (a: any, b: any) => a.margin - b.margin,
    },
    {
      title: 'Cost per Transaction',
      dataIndex: 'costPerTransaction',
      key: 'costPerTransaction',
      render: (value: number) => `$${value.toFixed(3)}`,
      sorter: (a: any, b: any) => a.costPerTransaction - b.costPerTransaction,
    },
    {
      title: 'Transactions',
      dataIndex: 'transactions',
      key: 'transactions',
      render: (value: number) => formatNumber(value),
      sorter: (a: any, b: any) => a.transactions - b.transactions,
    },
  ];

  // Feature table columns
  const featureColumns = [
    {
      title: 'Feature',
      dataIndex: 'feature',
      key: 'feature',
    },
    {
      title: 'Cost',
      dataIndex: 'cost',
      key: 'cost',
      render: (value: number) => formatCurrency(value),
      sorter: (a: any, b: any) => a.cost - b.cost,
    },
    {
      title: 'Revenue Attribution',
      dataIndex: 'revenue',
      key: 'revenue',
      render: (value: number) => formatCurrency(value),
      sorter: (a: any, b: any) => a.revenue - b.revenue,
    },
    {
      title: 'Usage',
      dataIndex: 'usage',
      key: 'usage',
      render: (value: number) => formatNumber(value),
      sorter: (a: any, b: any) => a.usage - b.usage,
    },
    {
      title: 'Efficiency Score',
      dataIndex: 'efficiency',
      key: 'efficiency',
      render: (value: number) => (
        <div className="flex items-center space-x-2">
          <Progress 
            percent={Math.min(value / 4, 100)} 
            size="small" 
            showInfo={false}
            strokeColor={value >= 300 ? '#52c41a' : value >= 250 ? '#faad14' : '#ff4d4f'}
          />
          <span className="text-sm">{value}</span>
        </div>
      ),
      sorter: (a: any, b: any) => a.efficiency - b.efficiency,
    },
  ];

  if (loading) {
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
          <Title level={2} className="!mb-2">Business Intelligence</Title>
          <Text type="secondary">
            Unit economics and business value analysis of your cloud investments
          </Text>
        </div>
        
        <Space>
          <Select
            value={selectedMetric}
            onChange={handleMetricChange}
            style={{ width: 180 }}
          >
            <Select.Option value="cost_per_customer">Cost per Customer</Select.Option>
            <Select.Option value="cost_per_feature">Cost per Feature</Select.Option>
            <Select.Option value="roi_analysis">ROI Analysis</Select.Option>
            <Select.Option value="margin_analysis">Margin Analysis</Select.Option>
          </Select>
          
          <Select
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 120 }}
          >
            <Select.Option value="7d">Last 7 days</Select.Option>
            <Select.Option value="30d">Last 30 days</Select.Option>
            <Select.Option value="90d">Last 90 days</Select.Option>
          </Select>
        </Space>
      </div>

      {/* Unit Economics KPIs */}
      <Row gutter={[16, 16]}>
        {mockUnitEconomics.map((metric, index) => (
          <Col xs={24} sm={12} lg={6} key={metric.metric}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card>
                <Statistic
                  title={metric.metric}
                  value={metric.value}
                  formatter={(value) => 
                    metric.metric.includes('Revenue') 
                      ? `${Number(value).toFixed(2)}x`
                      : formatCurrency(Number(value))
                  }
                  prefix={
                    metric.metric.includes('Customer') ? <UserOutlined /> :
                    metric.metric.includes('Feature') ? <FunctionOutlined /> :
                    metric.metric.includes('Revenue') ? <TrophyOutlined /> :
                    <DollarOutlined />
                  }
                  valueStyle={{ 
                    color: metric.trend === 'up' ? '#52c41a' : '#1890ff' 
                  }}
                />
                <div className="mt-2 flex items-center space-x-1">
                  {metric.trend === 'up' ? 
                    <RiseOutlined className="text-green-500" /> : 
                    <FallOutlined className="text-red-500" />
                  }
                  <Text type={metric.trend === 'up' ? 'success' : 'danger'}>
                    {Math.abs(metric.change).toFixed(1)}% vs last period
                  </Text>
                </div>
              </Card>
            </motion.div>
          </Col>
        ))}
      </Row>

      {/* Unit Economics Trend Chart */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card title="Unit Economics Trends" className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockCostTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => dayjs(value).format('MMM DD')} 
                  />
                  <YAxis 
                    yAxisId="cost"
                    orientation="left"
                    tickFormatter={(value) => `$${value}`}
                  />
                  <YAxis 
                    yAxisId="revenue"
                    orientation="right"
                    tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
                  />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      name === 'revenue' 
                        ? formatCurrency(value)
                        : `$${Number(value).toFixed(2)}`,
                      name === 'costPerCustomer' ? 'Cost per Customer' :
                      name === 'costPerFeature' ? 'Cost per Feature' : 'Revenue'
                    ]}
                    labelFormatter={(value) => dayjs(value).format('MMM DD, YYYY')}
                  />
                  <Legend />
                  <Line 
                    yAxisId="cost"
                    type="monotone" 
                    dataKey="costPerCustomer" 
                    stroke="#1890ff" 
                    strokeWidth={3}
                    name="Cost per Customer"
                  />
                  <Line 
                    yAxisId="cost"
                    type="monotone" 
                    dataKey="costPerFeature" 
                    stroke="#52c41a" 
                    strokeWidth={2}
                    name="Cost per Feature"
                  />
                  <Line 
                    yAxisId="revenue"
                    type="monotone" 
                    dataKey="revenue" 
                    stroke="#faad14" 
                    strokeWidth={2}
                    name="Revenue"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </motion.div>
        </Col>
      </Row>

      {/* Customer Analysis */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card 
              title="Customer Cost Analysis" 
              extra={
                <Button type="primary" size="small">
                  Export Report
                </Button>
              }
            >
              <Table
                columns={customerColumns}
                dataSource={mockCustomerCosts}
                rowKey="customerId"
                pagination={{ pageSize: 10 }}
                size="small"
              />
            </Card>
          </motion.div>
        </Col>
      </Row>

      {/* Feature Analysis & ROI */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <Card title="Feature Cost Analysis">
              <Table
                columns={featureColumns}
                dataSource={mockFeatureCosts}
                rowKey="feature"
                pagination={false}
                size="small"
              />
            </Card>
          </motion.div>
        </Col>

        <Col xs={24} lg={8}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.7 }}
          >
            <Card title="ROI by Segment" className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mockROIData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" tickFormatter={(value) => `${value}%`} />
                  <YAxis type="category" dataKey="segment" width={80} />
                  <Tooltip
                    formatter={(value: number) => [`${value}%`, 'ROI']}
                  />
                  <Bar 
                    dataKey="roi" 
                    fill="#1890ff"
                    radius={[0, 4, 4, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </motion.div>
        </Col>
      </Row>
    </div>
  );
};

export default BusinessIntelligence;