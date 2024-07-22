import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [file3, setFile3] = useState(null);
  const [jobId, setJobId] = useState('');
  const [jobStatus, setJobStatus] = useState('');
  const [downloadLink, setDownloadLink] = useState('');

  const handleFileChange = (e, setFile) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('files', file1);
    formData.append('files', file2);
    formData.append('files', file3);

    try {
      const response = await axios.post('http://127.0.0.1:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setJobId(response.data.job_id);
      setJobStatus('Pending');
    } catch (error) {
      console.error('Error uploading files:', error);
    }
  };

  useEffect(() => {
    if (jobId) {
      const interval = setInterval(async () => {
        try {
          const response = await axios.get(`http://127.0.0.1:8000/jobs/${jobId}`);
          setJobStatus(response.data.status);
          if (response.data.status === 'Completed') {
            setDownloadLink(response.data.download_url);
            clearInterval(interval);
          }
        } catch (error) {
          console.error('Error fetching job status:', error);
        }
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [jobId]);

  return (
    <div className="App">
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={(e) => handleFileChange(e, setFile1)} />
        <input type="file" onChange={(e) => handleFileChange(e, setFile2)} />
        <input type="file" onChange={(e) => handleFileChange(e, setFile3)} />
        <button type="submit">Upload</button>
      </form>
      {jobId && <p>Job ID: {jobId}</p>}
      {jobStatus && <p>Job Status: {jobStatus}</p>}
      {downloadLink && <a href={downloadLink}>Download Combined Video</a>}
    </div>
  );
}

export default App;
