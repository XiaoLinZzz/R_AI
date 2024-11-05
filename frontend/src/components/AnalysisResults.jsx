import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Typography, Card, Button, message, Spin, List, Table } from "antd";
import axios from "axios";
import { ArrowLeftOutlined } from "@ant-design/icons";
import {
  FileTextOutlined,
  NumberOutlined,
  CheckSquareOutlined,
  CalendarOutlined,
  UnorderedListOutlined,
  FunctionOutlined,
} from "@ant-design/icons";
const { Title, Text } = Typography;
import "./AnalysisResults.css";

// 添加日期格式化辅助函数
const formatDate = (dateString) => {
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return dateString; // 如果日期无效，返回原始字符串

  // 使用 padStart 确保月份和日期都是两位数
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const year = date.getFullYear();

  return `${month}/${day}/${year}`;
};

// 修改值格式化辅助函数
const formatValue = (value, type) => {
  if (value === null || value === undefined) return "-";

  const baseType = type.toLowerCase().split("[")[0];

  switch (baseType) {
    case "datetime64":
      return formatDate(value);
    case "bool":
      return value ? "Yes" : "No";
    case "float64":
    case "float32":
      return typeof value === "number" ? value.toFixed(2) : value;
    default:
      return String(value);
  }
};

// 添加数据类型格式化辅助函数
const getTypeInfo = (type) => {
  // 移除可能的额外信息，只保留核心类型
  const baseType = type.toLowerCase().split("[")[0];

  const typeMap = {
    object: {
      label: "Text",
      icon: <FileTextOutlined style={{ marginRight: 8, color: "#1890ff" }} />,
    },
    int64: {
      label: "Integer",
      icon: <NumberOutlined style={{ marginRight: 8, color: "#52c41a" }} />,
    },
    int32: {
      label: "Integer",
      icon: <NumberOutlined style={{ marginRight: 8, color: "#52c41a" }} />,
    },
    int16: {
      label: "Integer",
      icon: <NumberOutlined style={{ marginRight: 8, color: "#52c41a" }} />,
    },
    int8: {
      label: "Integer",
      icon: <NumberOutlined style={{ marginRight: 8, color: "#52c41a" }} />,
    },
    float64: {
      label: "Decimal",
      icon: <NumberOutlined style={{ marginRight: 8, color: "#722ed1" }} />,
    },
    float32: {
      label: "Decimal",
      icon: <NumberOutlined style={{ marginRight: 8, color: "#722ed1" }} />,
    },
    bool: {
      label: "Boolean",
      icon: (
        <CheckSquareOutlined style={{ marginRight: 8, color: "#fa8c16" }} />
      ),
    },
    datetime64: {
      label: "Date/Time",
      icon: <CalendarOutlined style={{ marginRight: 8, color: "#eb2f96" }} />,
    },
    category: {
      label: "Category",
      icon: (
        <UnorderedListOutlined style={{ marginRight: 8, color: "#13c2c2" }} />
      ),
    },
    complex: {
      label: "Complex Number",
      icon: <FunctionOutlined style={{ marginRight: 8, color: "#f5222d" }} />,
    },
  };

  return (
    typeMap[baseType] || {
      label: type,
      icon: <FileTextOutlined style={{ marginRight: 8, color: "#8c8c8c" }} />,
    }
  );
};

function AnalysisResults() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        console.log("Fetching analysis for ID:", id);
        const { data } = await axios.get(
          `http://localhost:8000/api/analysis/${id}/`
        );

        console.log("Received analysis data:", data);
        setAnalysisResult(data);
        setError(null);
      } catch (error) {
        console.error("Error fetching analysis:", error);

        let errorMessage = "Failed to load analysis results";
        if (error.response) {
          if (error.response.data && typeof error.response.data === "object") {
            errorMessage =
              error.response.data.error ||
              error.response.data.message ||
              errorMessage;
          } else if (error.response.status === 500) {
            errorMessage = "Internal server error. Please try again later.";
          }
        } else if (error.request) {
          errorMessage =
            "No response from server. Please check your connection.";
        } else {
          errorMessage = error.message || errorMessage;
        }

        setError(errorMessage);
        message.error(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchAnalysis();
    }
  }, [id, navigate]);

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "50px" }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="error-card">
        <Title level={3}>Error</Title>
        <p>{error}</p>
        <Button type="primary" onClick={() => navigate("/")}>
          Return to Upload
        </Button>
      </Card>
    );
  }

  if (!analysisResult) {
    return (
      <Card className="error-card">
        <Title level={3}>No Data Found</Title>
        <p>The requested analysis could not be found.</p>
        <Button type="primary" onClick={() => navigate("/")}>
          Return to Upload
        </Button>
      </Card>
    );
  }

  // 修改列的定义
  const columns = analysisResult?.columns.map((column) => ({
    title: column,
    dataIndex: column,
    key: column,
    render: (text) => formatValue(text, analysisResult.dtypes[column]),
  }));

  // 修改数据类型展示
  const dataTypesList = Object.entries(analysisResult?.dtypes || {}).map(
    ([column, type]) => {
      const typeInfo = getTypeInfo(type);
      return {
        column,
        type: typeInfo.label,
        icon: typeInfo.icon,
      };
    }
  );

  return (
    <div className="result-box">
      <Card className="result-card" bordered={false}>
        <div className="header-section">
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate("/")}
            style={{ marginBottom: 24 }}
          >
            Return to Upload
          </Button>
          <Title level={2}>Analysis Results</Title>
        </div>

        <Card className="info-card" bordered={false}>
          <div className="file-info">
            <div className="info-item">
              <Text type="secondary">File Name</Text>
              <Text strong>{analysisResult.file_name}</Text>
            </div>
            <div className="info-item">
              <Text type="secondary">Upload Time</Text>
              <Text strong>
                {new Date(analysisResult.upload_time).toLocaleString()}
              </Text>
            </div>
          </div>
        </Card>

        <div className="result-content">
          <Card
            title="Columns and Their Data Types"
            className="data-card"
            bordered={false}
          >
            <List
              grid={{ gutter: 16, column: 3 }}
              dataSource={dataTypesList}
              renderItem={(item) => (
                <List.Item>
                  <Card size="small" bordered>
                    <Text strong>{item.column}</Text>
                    <br />
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        marginTop: 4,
                      }}
                    >
                      {item.icon}
                      <Text type="secondary">{item.type}</Text>
                    </div>
                  </Card>
                </List.Item>
              )}
            />
          </Card>

          <Card
            title="Preview of Processed Data"
            className="data-card"
            bordered={false}
          >
            <div className="table-container">
              <Table dataSource={analysisResult.data} columns={columns} />
            </div>
          </Card>
        </div>
      </Card>
    </div>
  );
}

export default AnalysisResults;
