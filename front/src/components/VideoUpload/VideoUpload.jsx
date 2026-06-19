import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import styles from "./VideoUpload.module.scss";

function VideoUpload() {
  const [chats, setChats] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [editingChatId, setEditingChatId] = useState(null);
  const [editingName, setEditingName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  
  const fileInputRef = useRef(null);
  const chatCounter = useRef(1);

  // 🎯 Drag & Drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (file?.type.startsWith('video/') && selectedChatId) {
      await uploadFile(file);
    }
  };

  const uploadFile = async (file) => {
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
          ? { ...c, videos: [...c.videos, { 
              id: Date.now(), 
              name: file.name, 
              result: response.data,
              uploadedAt: new Date().toISOString()
            }] }
          : c
      ));
      
      setMessage(`✅ Загружено: ${file.name}\n${response.data.analysis || ''}`);
    } catch (err) {
      console.error(err);
      setMessage('❌ Ошибка загрузки. Проверьте соединение.');
    } finally {
      setUploading(false);
    }
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (file && selectedChatId) {
      await uploadFile(file);
    }
    e.target.value = '';
  };

  const createChat = () => {
    const newChat = {
      id: Date.now(),
      name: `Анализ #${chatCounter.current++}`,
      videos: [],
      createdAt: new Date().toISOString()
    };
    setChats(prev => [...prev, newChat]);
    setSelectedChatId(newChat.id);
    setMessage('');
  };

  const startEditing = (chat, e) => {
    e?.stopPropagation();
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

  const selectedChat = chats.find(c => c.id === selectedChatId);

  // ⌨️ Keyboard shortcut: Ctrl+N для нового чата
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        createChat();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className={styles.video_upload}>
      {/* 📋 Sidebar */}
      <aside className={styles.left_bar}>
        <button 
          className={styles.new_chat_btn} 
          onClick={createChat}
          title="Ctrl+N"
        >
          Новый анализ
        </button>
        
        <nav className={styles.chat_list}>
          {chats.length === 0 ? (
            <div className={styles.empty_state} style={{ fontSize: '13px', padding: '20px' }}>
              Нет анализов
            </div>
          ) : (
            chats.map(chat => (
              <div
                key={chat.id}
                className={`${styles.chat_item} ${chat.id === selectedChatId ? styles.active : ''}`}
                onClick={() => { setSelectedChatId(chat.id); setMessage(''); }}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && setSelectedChatId(chat.id)}
              >
                {editingChatId === chat.id ? (
                  <input
                    className={styles.name_input}
                    value={editingName}
                    autoFocus
                    onChange={e => setEditingName(e.target.value)}
                    onBlur={finishEditing}
                    onKeyDown={e => { 
                      if (e.key === 'Enter') finishEditing();
                      if (e.key === 'Escape') setEditingChatId(null);
                    }}
                    onClick={e => e.stopPropagation()}
                    placeholder="Название анализа..."
                  />
                ) : (
                  <span
                    className={styles.chat_name}
                    onDoubleClick={(e) => startEditing(chat, e)}
                    title="Двойной клик для переименования"
                  >
                    {chat.name}
                  </span>
                )}
                <span className={styles.video_count}>
                  {chat.videos.length} {chat.videos.length === 1 ? 'видео' : 'видео'}
                </span>
              </div>
            ))
          )}
        </nav>
      </aside>

      {/* 🖼️ Main Content */}
      <main 
        className={styles.main_area}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {!selectedChat ? (
          <div className={styles.empty_state}>
            <p>Создайте новый анализ или выберите существующий, чтобы начать работу с видео</p>
          </div>
        ) : (
          <>
            <header className={styles.main_header}>
              <h2>{selectedChat.name}</h2>
            </header>
            
            {/* 📤 Upload Zone */}
            <section className={`${styles.upload_section} ${isDragging ? styles.dragging : ''}`}>
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                onChange={handleFileSelect}
                className={styles.hiddenInput}
                aria-label="Выберите видеофайл"
              />
              <button
                className={styles.upload_btn}
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                aria-busy={uploading}
              >
                {uploading ? (
                  <>
                    <span className={styles.spinner}></span>
                    Обработка...
                  </>
                ) : (
                  '+ Добавить видео'
                )}
              </button>
              <small style={{ color: '#94a3b8', fontSize: '12px' }}>
                или перетащите файл сюда
              </small>
            </section>
            {message && (
                <p className={styles.message} role="status" aria-live="polite">
                  {message}
                </p>
              )}

            {/* 🎞️ Video List */}
            {selectedChat.videos.length > 0 && (
              <section aria-label="Список видео">
                <h3 style={{ 
                  fontSize: '14px', 
                  fontWeight: 600, 
                  color: '#64748b', 
                  marginBottom: '12px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  Загруженные видео ({selectedChat.videos.length})
                </h3>
                <div className={styles.video_list}>
                  {selectedChat.videos.map((video) => (
                    <article key={video.id || video.name} className={styles.video_item}>
                      <span className={styles.video_icon} aria-hidden="true">▶</span>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <strong style={{ 
                          display: 'block', 
                          whiteSpace: 'nowrap', 
                          overflow: 'hidden', 
                          textOverflow: 'ellipsis' 
                        }}>
                          {video.name}
                        </strong>
                        {video.uploadedAt && (
                          <small style={{ color: '#94a3b8', fontSize: '11px' }}>
                            {new Date(video.uploadedAt).toLocaleTimeString('ru-RU', { 
                              hour: '2-digit', 
                              minute: '2-digit' 
                            })}
                          </small>
                        )}
                      </div>
                      {/* 🔘 Опционально: кнопка удаления */}
                      {/* <button 
                        className={styles.delete_btn}
                        onClick={() => {/* логика удаления */}

                    </article>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default VideoUpload;