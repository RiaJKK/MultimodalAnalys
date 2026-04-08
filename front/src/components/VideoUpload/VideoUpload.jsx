import { useState } from 'react';
import axios from 'axios';
import styles from "./VideoUpload.module.scss"


function VideoUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Выберите файл!');
      return;
    }

    const formData = new FormData();
    formData.append('file', file); // ключ 'video' — на бэкенде так же нужно

    try {
      setUploading(true);
      const response = await axios.post('http://127.0.0.1:8000/transcribe', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage('Видео успешно загружено: ' + response.data.filename + "текст:" + response.data.text);
    } catch (err) {
      console.error(err);
      setMessage('Ошибка загрузки');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className={styles.video_upload}>

      <div className={styles.left_bar}>
        <label className={styles.choose_btn}>
          <p>Выбрать видео</p>
          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            className={styles.hiddenInput}
          />
        </label>  
        <hr/>   
      </div>
      <div className={styles.upload}>
        <button onClick={handleUpload} disabled={uploading} className={styles.choose_btn}>
          <div className={styles.text}>
          {uploading ? 'Загрузка...' : 'Загрузить видео'}
          </div>
        </button>
        <div className={styles.text}>
          {message && <p>{message}</p>}
        </div>
      </div>
      
    </div>
  );
}

export default VideoUpload;