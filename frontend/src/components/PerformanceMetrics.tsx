import React from 'react';
import { Card, Statistic, Row, Col } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

interface PerformanceMetricsProps {
    data: any;
}

export const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ data }) => {
    if (!data) return null;
    
    return (
        <div className="performance-metrics">
            <Row gutter={16}>
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="Total Return"
                            value={data.total_return * 100}
                            precision={2}
                            suffix="%"
                            prefix={data.total_return > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                            valueStyle={{ color: data.total_return > 0 ? '#3f8600' : '#cf1322' }}
                        />
                    </Card>
                </Col>
                
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="Sharpe Ratio"
                            value={data.sharpe_ratio}
                            precision={2}
                        />
                    </Card>
                </Col>
                
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="Max Drawdown"
                            value={data.max_drawdown * 100}
                            precision={2}
                            suffix="%"
                            valueStyle={{ color: '#cf1322' }}
                        />
                    </Card>
                </Col>
                
                <Col span={6}>
                    <Card>
                        <Statistic
                            title="Win Rate"
                            value={data.win_rate * 100}
                            precision={2}
                            suffix="%"
                        />
                    </Card>
                </Col>
            </Row>
        </div>
    );
}; 