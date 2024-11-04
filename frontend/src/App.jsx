import { Button, Typography, Upload, Card, message } from "antd";
import { InboxOutlined, UploadOutlined } from "@ant-design/icons";
import { useState } from "react";
import "./FileUpload.css";

const { Title, Text } = Typography;
const { Dragger } = Upload;

function App() {
  const [file, setFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // 修改文件处理函数
  const handleFileChange = (info) => {
    console.log("File info:", info); // 添加调试日志

    if (info.file && info.fileList.length > 0) {
      // 使用最后上传的文件
      const file = info.fileList[info.fileList.length - 1];
      setFile(file.originFileObj || file);
      console.log("File set:", file); // 添加调试日志
    } else {
      setFile(null);
    }
  };

  // 处理文件分析
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
      setAnalysisResult(data);
      message.success("File analyzed successfully!");
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
            beforeUpload={() => false} // 阻止自动上传
            maxCount={1}
            className="custom-dragger"
            onChange={handleFileChange}
            onRemove={() => setFile(null)} // 添加删除处理
            fileList={file ? [file] : []} // 控制显示的文件列表
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
            disabled={!file} // 这里检查 file 是否存在
          >
            Analyze Data Types
          </Button>
        </div>

        {analysisResult && (
          <div className="result-box">
            <Title level={3}>Analysis Results</Title>
            <div className="result-content">
              <h4>Columns and Their Data Types:</h4>
              <ul>
                {Object.entries(analysisResult.dtypes).map(([column, type]) => (
                  <li key={column}>
                    <strong>{column}:</strong> {type}
                  </li>
                ))}
              </ul>

              <h4>Preview of Processed Data:</h4>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      {analysisResult.columns.map((column) => (
                        <th key={column}>{column}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {analysisResult.data.slice(0, 5).map((row, index) => (
                      <tr key={index}>
                        {analysisResult.columns.map((column) => (
                          <td key={column}>{String(row[column])}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

export default App;
