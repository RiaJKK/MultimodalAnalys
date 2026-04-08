import styles from "./Strawberry.module.scss"
// 
const Strawberry = () => {

    function onHover() {

    }

    return ( <>
    <div class={styles.straw_box}>
        <div class={styles.strawberry}>
            <div class={styles.lists}>
                <div class={styles.petal_left}></div>
                <div class={styles.petal_right}></div>
            </div>
            <div class={styles.straw}>
                <div class={`${styles.dot}`} id={styles.first_dot}></div>
                <div class={`${styles.dot}`} id={styles.second_dot}></div>
                <div class={`${styles.dot}`} id={styles.third_dot}></div>
                <div class={`${styles.dot}`} id={styles.four_dot}></div>

            </div>  
            <div class={styles.straw_in_chocolate}></div>  

            </div>
        <div class={styles.box_chocolate}>
            <div class={styles.for_you}>  
                <h1 class={styles.for}>FOR </h1>
                <h1 class={styles.for}>YOU </h1>
            </div>
        </div>
    </div>

    
    </> );
}
 
export default Strawberry;