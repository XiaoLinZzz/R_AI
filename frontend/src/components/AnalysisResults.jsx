import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Typography, Card, Button, message, Spin, List, Table } from "antd";
import axios from "axios";
import { ArrowLeftOutlined } from "@ant-design/icons";
const { Title, Text } = Typography;
import "./AnalysisResults.css";

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
              dataSource={Object.entries(analysisResult.dtypes)}
              renderItem={([column, type]) => (
                <List.Item>
                  <Card size="small" bordered>
                    <Text strong>{column}</Text>
                    <br />
                    <Text type="secondary">{type}</Text>
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
              <Table
                dataSource={analysisResult.data.slice(0, 5)}
                columns={analysisResult.columns.map((column) => ({
                  title: column,
                  dataIndex: column,
                  key: column,
                  render: (text) => String(text),
                }))}
                pagination={false}
                scroll={{ x: "max-content" }}
              />
            </div>
          </Card>
        </div>
      </Card>
    </div>
  );
}

export default AnalysisResults;
