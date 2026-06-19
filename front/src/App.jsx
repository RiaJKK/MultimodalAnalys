import { useState } from 'react'
import styles from './App.module.scss'
import VideoUpload from './components/VideoUpload/VideoUpload'
import Header from './components/Header'

function App() {

  return (
    <>
      <Header />
      <VideoUpload />
    </>

  )
}
export default App
