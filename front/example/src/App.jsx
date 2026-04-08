import { useState } from 'react'
import styles from './App.module.scss'
import Strawberry from './components/Strawberry/Strawberry'

function App() {

  return (
    <>
      <header>
        <div class={styles.logo}><h1>ЛОГО</h1></div>
        <nav class={styles.nav_header}>
          <div class={`${styles.nav_link}`}><h1>О нас</h1></div>
          <div class={`${styles.nav_link}`}><h1>Контакты</h1></div>
          <div class={`${styles.nav_link}`}><h1>Каталог</h1></div>
          <div class={`${styles.nav_link}`}><h1>Заказать</h1></div>
        </nav>
        <div class={styles.header_btn_order}> <h1>Заказать</h1></div>
      </header>
      <div class={styles.main}>
      <main > 
       <div class={styles.main_describtion} >
          <div class={styles.main_header}><h1>ЭТО НАША КОМПАНИЯ</h1></div>
          <div class={styles.main_text}><p>Добро пожаловать в [Название компании] – место, где свежесть природы встречается с роскошью шоколада. Мы создаем изысканные десерты, превращая сочную отборную клубнику в настоящее произведение кулинарного искусства.</p></div>
          <div class={styles.button}><h1>Заказать</h1></div>
       </div>
      <img src="src\images\1.png"></img>
      </main>
      <div class={styles.catalagy_name}>       
        <h1 class={styles.h1_catalogy}>КАТАЛОГ</h1>
      </div>

      <div class={styles.frame_catalogy}>
        <div class={styles.catalogy}>
          <div class={styles.card}></div>
          <div class={styles.card}></div>
          <div class={styles.card}></div>
          <div class={styles.card}></div>
          <div class={styles.card}></div>
          <div class={styles.card}></div>
          <div class={styles.card}></div>
          <div class={styles.card}></div>
          <div class={styles.card}></div>

        </div>
      </div>
      </div>
      <div class={styles.straw_img}>
      </div>
      
    </>
  )
}

export default App
