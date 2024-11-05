import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import FileUpload from "./components/FileUpload";
import AnalysisResults from "./components/AnalysisResults";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<FileUpload />} />
        <Route path="/results/:id" element={<AnalysisResults />} />
      </Routes>
    </Router>
  );
}

export default App;
