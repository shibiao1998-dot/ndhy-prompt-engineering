import React, { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Progress,
  Tag,
  Button,
  Input,
  Space,
  Statistic,
  Descriptions,
  message,
  Tabs
} from 'antd';
import {
  RocketOutlined,
  TeamOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ThunderboltOutlined,
  DatabaseOutlined,
  LineChartOutlined
} from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

// 常量定义
const DYNAMIC_MODE_BASE_TOKENS = 50000; // 基础上下文
const FIXED_MODE_TOKENS = 110000; // 固定 8 位专家模式

// 动态创建专家模式 - 上下文增长计算
const calculateDynamicTokens = (expertCount: number) => {
  const baseTokens = DYNAMIC_MODE_BASE_TOKENS;
  const tokensPerExpert = 10000; // 每个专家约 10k tokens
  const tokensPerSkill = 5000; // 每个技能约 5k tokens
  const skillsPerExpert = 3; // 平均每个专家 3 个技能

  return baseTokens + (expertCount * tokensPerExpert) + (expertCount * skillsPerExpert * tokensPerSkill);
};

// 失败点计算（约 30 专家后出现连接失败）
const getFailurePoint = (expertCount: number) => {
  if (expertCount >= 30) return 'high';
  if (expertCount >= 20) return 'medium';
  return 'low';
};

const AIEmployeeDemo: React.FC = () => {
  const [expertCount, setExpertCount] = useState<number>(10);
  const [requirement, setRequirement] = useState<string>('');

  const dynamicTokens = calculateDynamicTokens(expertCount);
  const failureRisk = getFailurePoint(expertCount);

  // 对比数据
  const comparisonData = {
    dynamic: {
      name: '动态创建专家模式',
      tokens: dynamicTokens,
      cost: dynamicTokens * 0.000015, // 假设每 1M tokens $15
      stability: failureRisk === 'high' ? '低' : failureRisk === 'medium' ? '中' : '高',
      scalability: '理论上无限，实际受限于上下文窗口',
      quality: '不一致（依赖临时创建的专家质量）'
    },
    fixed: {
      name: '固定工作流模式',
      tokens: FIXED_MODE_TOKENS,
      cost: FIXED_MODE_TOKENS * 0.000015,
      stability: '高',
      scalability: '可预测，可扩展专家库',
      quality: '稳定 60 分 + 可迭代'
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* 标题区域 */}
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <Title level={1}>
          <ThunderboltOutlined style={{ marginRight: '12px', color: '#1890ff' }} />
          AI 员工模式对比 Demo
        </Title>
        <Paragraph style={{ fontSize: '16px', color: '#666' }}>
          交互式展示两种 AI 员工架构模式的对比：动态创建专家 vs 固定工作流
        </Paragraph>
      </div>

      {/* 模式对比卡片 */}
      <Row gutter={[24, 24]} style={{ marginBottom: '48px' }}>
        <Col span={12}>
          <Card
            title={
              <Space>
                <RocketOutlined style={{ color: '#ff4d4f' }} />
                <Text strong>模式 A：动态创建专家</Text>
              </Space>
            }
            bordered={false}
            style={{
              height: '100%',
              borderColor: failureRisk === 'high' ? '#ff4d4f' : failureRisk === 'medium' ? '#faad14' : '#52c41a',
              borderWidth: '2px'
            }}
          >
            <Descriptions column={1} size="small">
              <Descriptions.Item label="设计">
                主 Agent 作为 Leader，按需创建领域专家
              </Descriptions.Item>
              <Descriptions.Item label="专家池">
                随业务积累不断增长
              </Descriptions.Item>
              <Descriptions.Item label="理论覆盖">
                全业务领域
              </Descriptions.Item>
              <Descriptions.Item label="当前专家数">
                <Input
                  type="number"
                  value={expertCount}
                  onChange={(e) => setExpertCount(Number(e.target.value))}
                  style={{ width: '100px' }}
                  min={1}
                  max={100}
                />
              </Descriptions.Item>
              <Descriptions.Item label="Token 消耗">
                <Text type={dynamicTokens > 1000000 ? 'danger' : 'success'}>
                  {(dynamicTokens / 1000).toFixed(0)}K tokens
                  {dynamicTokens > 1000000 && <WarningOutlined style={{ marginLeft: '8px' }} />}
                </Text>
              </Descriptions.Item>
              <Descriptions.Item label="失败风险">
                <Tag color={failureRisk === 'high' ? 'red' : failureRisk === 'medium' ? 'orange' : 'green'}>
                  {failureRisk === 'high' ? '高（连接失败）' : failureRisk === 'medium' ? '中' : '低'}
                </Tag>
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: '16px' }}>
              <Text type="secondary">上下文增长曲线</Text>
              <Progress
                percent={Math.min((dynamicTokens / 1000000) * 100, 100)}
                strokeColor={dynamicTokens > 1000000 ? '#ff4d4f' : '#1890ff'}
                format={() => `${(dynamicTokens / 1000).toFixed(0)}K / 1M`}
              />
              {dynamicTokens > 1000000 && (
                <Text type="danger" style={{ fontSize: '12px' }}>
                  <WarningOutlined /> 超过 1M 上下文窗口，可能出现连接失败
                </Text>
              )}
            </div>
          </Card>
        </Col>

        <Col span={12}>
          <Card
            title={
              <Space>
                <TeamOutlined style={{ color: '#52c41a' }} />
                <Text strong>模式 B：固定工作流 AI 员工</Text>
              </Space>
            }
            bordered={false}
            style={{
              height: '100%',
              borderColor: '#52c41a',
              borderWidth: '2px'
            }}
          >
            <Descriptions column={1} size="small">
              <Descriptions.Item label="设计">
                8 位固定专家流水线
              </Descriptions.Item>
              <Descriptions.Item label="专家配置">
                需求→产品→架构→UX→开发→测试→部署
              </Descriptions.Item>
              <Descriptions.Item label="上下文">
                可预测，Token 消耗有上限
              </Descriptions.Item>
              <Descriptions.Item label="Token 消耗">
                <Text type="success">{(FIXED_MODE_TOKENS / 1000).toFixed(0)}K tokens</Text>
              </Descriptions.Item>
              <Descriptions.Item label="稳定性">
                <Tag color="green">高</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="产出质量">
                <Tag color="blue">稳定 60 分 +</Tag>
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: '16px' }}>
              <Text type="secondary">上下文使用率</Text>
              <Progress
                percent={(FIXED_MODE_TOKENS / 1000000) * 100}
                strokeColor="#52c41a"
                format={() => `${(FIXED_MODE_TOKENS / 1000).toFixed(0)}K / 1M (${((FIXED_MODE_TOKENS / 1000000) * 100).toFixed(1)}%)`}
              />
              <Text type="success" style={{ fontSize: '12px' }}>
                <CheckCircleOutlined /> 远低于上下文限制，稳定运行
              </Text>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 核心指标对比 */}
      <Title level={2} style={{ marginBottom: '24px' }}>
        <LineChartOutlined style={{ marginRight: '12px' }} />
        核心指标对比
      </Title>

      <Row gutter={[24, 24]} style={{ marginBottom: '48px' }}>
        <Col span={6}>
          <Card title="人效比" bordered={false}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="动态模式"
                  value={2}
                  suffix="项目/月"
                  valueStyle={{ fontSize: '24px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="固定模式"
                  value={10}
                  suffix="项目/月"
                  valueStyle={{ color: '#52c41a', fontSize: '24px' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        <Col span={6}>
          <Card title="交付周期" bordered={false}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="动态模式"
                  value={30}
                  suffix="天"
                  valueStyle={{ fontSize: '24px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="固定模式"
                  value={3}
                  suffix="天"
                  valueStyle={{ color: '#52c41a', fontSize: '24px' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        <Col span={6}>
          <Card title="Token 成本/项目" bordered={false}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="动态模式"
                  value={comparisonData.dynamic.cost.toFixed(2)}
                  suffix="$"
                  valueStyle={{ fontSize: '24px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="固定模式"
                  value={comparisonData.fixed.cost.toFixed(2)}
                  suffix="$"
                  valueStyle={{ color: '#52c41a', fontSize: '24px' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>

        <Col span={6}>
          <Card title="产出质量" bordered={false}>
            <Row gutter={16}>
              <Col span={12}>
                <Text>动态模式</Text>
                <div style={{ marginTop: '8px' }}>
                  <Tag color="orange">不一致</Tag>
                </div>
              </Col>
              <Col span={12}>
                <Text>固定模式</Text>
                <div style={{ marginTop: '8px' }}>
                  <Tag color="green">稳定 60 分+</Tag>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 执行流程可视化 */}
      <Title level={2} style={{ marginBottom: '24px' }}>
        <DatabaseOutlined style={{ marginRight: '12px' }} />
        执行流程对比
      </Title>

      <Tabs defaultActiveKey="fixed">
        <Tabs.TabPane tab="固定工作流模式" key="fixed">
          <Card bordered={false}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              {[
                { icon: '🎯', name: '需求分析', color: '#1890ff' },
                { icon: '📐', name: '产品定义', color: '#722ed1' },
                { icon: '🏛️', name: '技术架构', color: '#13c2c2' },
                { icon: '🎨', name: 'UX 设计', color: '#eb2f96' },
                { icon: '🖌️', name: 'UI 设计', color: '#fa541c' },
                { icon: '🖥️', name: '前端开发', color: '#52c41a' },
                { icon: '⚙️', name: '后端开发', color: '#2f54eb' },
                { icon: '🧪', name: '测试部署', color: '#fa8c16' },
              ].map((step, index) => (
                <React.Fragment key={step.name}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{
                      width: '80px',
                      height: '80px',
                      borderRadius: '50%',
                      background: step.color,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '32px',
                      margin: '0 auto 8px'
                    }}>
                      {step.icon}
                    </div>
                    <Text>{step.name}</Text>
                  </div>
                  {index < 7 && (
                    <div style={{ flex: 1, borderBottom: '2px dashed #999', margin: '0 8px', position: 'relative', top: '-30px' }}>
                      <span style={{ position: 'absolute', right: '-10px', top: '-10px' }}>→</span>
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>
            <div style={{ marginTop: '24px', textAlign: 'center' }}>
              <Tag color="green">可预测</Tag>
              <Tag color="blue">标准化</Tag>
              <Tag color="green">Token 消耗稳定</Tag>
              <Tag color="blue">质量可控</Tag>
            </div>
          </Card>
        </Tabs.TabPane>

        <Tabs.TabPane tab="动态创建专家模式" key="dynamic">
          <Card bordered={false}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap' }}>
              <div style={{ textAlign: 'center', marginRight: '32px' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '50%',
                  background: '#ff4d4f',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '32px',
                  margin: '0 auto 8px'
                }}>
                  🧠
                </div>
                <Text>Leader Agent</Text>
              </div>

              <div style={{ flex: 1, borderBottom: '2px dashed #999', maxWidth: '200px' }}>→</div>

              <div style={{ textAlign: 'center', margin: '0 16px' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '50%',
                  background: '#faad14',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '32px',
                  margin: '0 auto 8px'
                }}>
                  🔍
                </div>
                <Text>分析需求</Text>
              </div>

              <div style={{ flex: 1, borderBottom: '2px dashed #999', maxWidth: '200px' }}>→</div>

              <div style={{ textAlign: 'center', margin: '0 16px' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '50%',
                  background: '#1890ff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '32px',
                  margin: '0 auto 8px'
                }}>
                  ➕
                </div>
                <Text>创建专家</Text>
              </div>

              <div style={{ flex: 1, borderBottom: '2px dashed #999', maxWidth: '200px' }}>→</div>

              <div style={{ textAlign: 'center', margin: '0 16px' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '50%',
                  background: '#722ed1',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '32px',
                  margin: '0 auto 8px'
                }}>
                  🎭
                </div>
                <Text>分配任务</Text>
              </div>

              <div style={{ flex: 1, borderBottom: '2px dashed #999', maxWidth: '200px' }}>→</div>

              <div style={{ textAlign: 'center' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '50%',
                  background: '#52c41a',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '32px',
                  margin: '0 auto 8px'
                }}>
                  ⚡
                </div>
                <Text>执行</Text>
              </div>
            </div>
            <div style={{ marginTop: '24px', textAlign: 'center' }}>
              <Tag color="red">不可预测</Tag>
              <Tag color="orange">上下文爆炸</Tag>
              <Tag color="red">Token 消耗高</Tag>
              <Tag color="orange">质量不稳定</Tag>
            </div>
          </Card>
        </Tabs.TabPane>
      </Tabs>

      {/* 需求输入演示区域 */}
      <Title level={2} style={{ marginTop: '48px', marginBottom: '24px' }}>
        <RocketOutlined style={{ marginRight: '12px' }} />
        需求输入演示
      </Title>

      <Card bordered={false}>
        <Paragraph>
          尝试输入一个产品需求，查看两种模式的处理差异：
        </Paragraph>

        <TextArea
          rows={4}
          value={requirement}
          onChange={(e) => setRequirement(e.target.value)}
          placeholder="例如：我需要一个内部工具，让销售团队可以录入客户信息，并自动生成跟进提醒..."
          style={{ marginBottom: '16px' }}
        />

        <Space>
          <Button
            type="primary"
            disabled={!requirement}
            onClick={() => message.info('固定工作流模式启动：8 位专家开始协作处理需求...')}
          >
            <TeamOutlined /> 使用固定工作流模式
          </Button>
          <Button
            disabled={!requirement}
            onClick={() => message.warning('动态创建专家模式：分析需求中...创建专家...（上下文快速增长中...）')}
          >
            <RocketOutlined /> 使用动态创建专家模式
          </Button>
        </Space>

        {requirement && (
          <div style={{ marginTop: '24px' }}>
            <Descriptions title="需求分析" bordered column={2}>
              <Descriptions.Item label="需求类型">内部工具开发</Descriptions.Item>
              <Descriptions.Item label="复杂度">中等</Descriptions.Item>
              <Descriptions.Item label="预计工作量（固定模式）">3 天</Descriptions.Item>
              <Descriptions.Item label="预计工作量（动态模式）">7-14 天（含上下文问题调试）</Descriptions.Item>
              <Descriptions.Item label="Token 消耗（固定模式）">~110K</Descriptions.Item>
              <Descriptions.Item label="Token 消耗（动态模式）">~300K-500K</Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </Card>

      {/* 总结区域 */}
      <Card
        style={{ marginTop: '48px', background: '#f6ffed', borderColor: '#52c41a' }}
        bordered={true}
      >
        <Title level={3} style={{ color: '#52c41a' }}>
          <CheckCircleOutlined style={{ marginRight: '8px' }} />
          结论：固定工作流模式是当前技术条件下的最优选择
        </Title>

        <Row gutter={24}>
          <Col span={8}>
            <Text strong>技术可行性</Text>
            <div style={{ marginTop: '8px' }}>
              <Tag color="green">上下文可控</Tag>
              <Tag color="green">稳定性高</Tag>
              <Tag color="green">易于维护</Tag>
            </div>
          </Col>
          <Col span={8}>
            <Text strong>经济效益</Text>
            <div style={{ marginTop: '8px' }}>
              <Tag color="blue">成本可预测</Tag>
              <Tag color="blue">ROI 可测量</Tag>
              <Tag color="blue">5-10 倍人效提升</Tag>
            </div>
          </Col>
          <Col span={8}>
            <Text strong>业务价值</Text>
            <div style={{ marginTop: '8px' }}>
              <Tag color="purple">快速交付</Tag>
              <Tag color="purple">质量稳定</Tag>
              <Tag color="purple">可规模化</Tag>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default AIEmployeeDemo;
