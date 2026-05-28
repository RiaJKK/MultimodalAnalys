import { useState, useRef } from 'react';
import axios from 'axios';
import styles from "./VideoUpload.module.scss"

function VideoUpload() {
  const [chats, setChats] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [editingChatId, setEditingChatId] = useState(null);
  const [editingName, setEditingName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const fileInputRef = useRef(null);
  const chatCounter = useRef(1);

  const createChat = () => {
    const newChat = {
      id: Date.now(),
      name: `Анализ #${chatCounter.current++}`,
      videos: []
    };
    setChats(prev => [...prev, newChat]);
    setSelectedChatId(newChat.id);
    setMessage('');
  };

  const startEditing = (chat) => {
    setEditingChatId(chat.id);
    setEditingName(chat.name);
  };

  const finishEditing = () => {
    if (editingName.trim()) {
      setChats(prev => prev.map(c =>
        c.id === editingChatId ? { ...c, name: editingName.trim() } : c
      ));
    }
    setEditingChatId(null);
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file || !selectedChatId) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      setMessage('');
      const response = await axios.post('http://127.0.0.1:8000/transcribe', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setChats(prev => prev.map(c =>
        c.id === selectedChatId
          ? { ...c, videos: [...c.videos, { name: file.name, result: response.data }] }
          : c
      ));
      setMessage('Загружено: ' + (response.data.filename || file.name) + "\n" + (response.data.analysis));
    } catch (err) {
      console.error(err);
      setMessage('Ошибка загрузки');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const selectedChat = chats.find(c => c.id === selectedChatId);

  return (
    <div className={styles.video_upload}>
      <div className={styles.left_bar}>
        <button className={styles.new_chat_btn} onClick={createChat}>
          + Новый анализ
        </button>
        <div className={styles.chat_list}>
          {chats.map(chat => (
            <div
              key={chat.id}
              className={`${styles.chat_item} ${chat.id === selectedChatId ? styles.active : ''}`}
              onClick={() => { setSelectedChatId(chat.id); setMessage(''); }}
            >
              {editingChatId === chat.id ? (
                <input
                  className={styles.name_input}
                  value={editingName}
                  autoFocus
                  onChange={e => setEditingName(e.target.value)}
                  onBlur={finishEditing}
                  onKeyDown={e => { if (e.key === 'Enter') finishEditing(); }}
                  onClick={e => e.stopPropagation()}
                />
              ) : (
                <span
                  className={styles.chat_name}
                  onDoubleClick={e => { e.stopPropagation(); startEditing(chat); }}
                >
                  {chat.name}
                </span>
              )}
              <span className={styles.video_count}>{chat.videos.length} видео</span>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.main_area}>
        {!selectedChat ? (
          <div className={styles.empty_state}>
            <p>Выберите или создайте анализ</p>
          </div>
        ) : (
          <>
            <div className={styles.main_header}>
              <h2>{selectedChat.name}</h2>
            </div>
            <div className={styles.upload_section}>
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                onChange={handleFileSelect}
                className={styles.hiddenInput}
              />
              <button
                className={styles.upload_btn}
                onClick={() => fileInputRef.current.click()}
                disabled={uploading}
              >
                {uploading ? 'Загрузка...' : '+ Добавить видео'}
              </button>
              {message && <p className={styles.message}>{message}</p>}
            </div>
            <div className={styles.video_list}>
              {selectedChat.videos.map((v, i) => (
                <div key={i} className={styles.video_item}>
                  <span className={styles.video_icon}>▶</span>
                  <span>{v.name}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default VideoUpload;
