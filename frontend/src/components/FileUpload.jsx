import { Button, Typography, Upload, Card, message } from "antd";
import { InboxOutlined, UploadOutlined } from "@ant-design/icons";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./FileUpload.css";

const { Title, Text } = Typography;
const { Dragger } = Upload;

function FileUpload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (info) => {
    const { file } = info;

    // Check file type
    const isCSV = file.type === "text/csv" || file.name.endsWith(".csv");

    if (!isCSV) {
      message.error("Only CSV files are supported");
      return;
    }

    if (info.file && info.fileList.length > 0) {
      const file = info.fileList[info.fileList.length - 1];
      setFile(file.originFileObj || file);
    } else {
      setFile(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      message.error("Please select a file first");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/process-data/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      message.success("File analyzed successfully!");
      navigate(`/results/${data.id}`);
    } catch (error) {
      console.error("Error:", error);
      message.error("Failed to analyze file: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <Card className="upload-card">
        <header className="upload-header">
          <Title level={2}>
            Data Type Inference Application
            <span className="header-highlight">AI Powered</span>
          </Title>
          <Text type="secondary" className="subtitle">
            Upload your file to analyze data types
          </Text>
        </header>

        <div className="upload-box">
          <Dragger
            name="file"
            multiple={false}
            beforeUpload={(file) => {
              const isCSV =
                file.type === "text/csv" || file.name.endsWith(".csv");
              if (!isCSV) {
                message.error("Only CSV files are supported");
              }
              return false;
            }}
            accept=".csv"
            maxCount={1}
            className="custom-dragger"
            onChange={handleFileChange}
            onRemove={() => setFile(null)}
            fileList={file ? [file] : []}
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined className="upload-icon" />
            </p>
            <p className="ant-upload-text">
              Click or drag file to this area to upload
            </p>
            <p className="ant-upload-hint">
              Support for a single file upload. CSV, Excel files are
              recommended.
            </p>
          </Dragger>

          <Button
            type="primary"
            size="large"
            className="upload-button"
            icon={<UploadOutlined />}
            onClick={handleAnalyze}
            loading={loading}
            disabled={!file}
          >
            Analyze Data Types
          </Button>
        </div>
      </Card>
    </div>
  );
}

export default FileUpload;
