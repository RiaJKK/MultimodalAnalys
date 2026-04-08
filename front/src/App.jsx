import { useState } from 'react'
import styles from './App.module.scss'
import VideoUpload from './components/VideoUpload/VideoUpload'

function App() {

  return (
    <>
      <div className={styles.header}>
        <div>
        <h1> MAVIS </h1>

        </div>
      </div>
      <VideoUpload/>
    </>
  )
}
export default App
