<template>
  <h1> Ride Together! </h1>
  <LoginMenu/>
  
</template>

<script>
import LoginMenu from './components/LoginMenu.vue'

export default {
  name: 'App',
  components: {
    LoginMenu
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

html {
  background: darkgray;
}
</style>
