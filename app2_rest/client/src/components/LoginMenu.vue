<template>
  <div v-if="!isUserLogged">    
    <div class="form">
    <form v-if="registerStep" class="register-form">
      <input v-model="name" type="text" placeholder="name"/>
      <input v-model="email" type="text" placeholder="email address"/>
      <input v-model="password" type="password" placeholder="password"/>
      <button @click="registerClient">create</button>
      <p class="message">Already registered? 
        <a @click="registerStep = false" href="#">Sign In </a>
      </p>
    </form>

    <form v-else class="login-form">
      <input v-model="login_name" type="text" placeholder="username"/>
      <input type="password" placeholder="password"/>
      <button @click="loginClient">login</button>
      <p class="message">Not registered? 
        <a @click="registerStep = true" href="#">Create an account</a>
      </p>
    </form>
    </div>
  </div>
  <div v-else>
    <h1> Hello {{ login_name }}</h1>
    
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'LoginMenu',
  props: {
    msg: String,
  },
  setup(){
    // Consts
    const name = ref("")
    const email = ref("")
    const password = ref("")
    const registerStep = ref(true)
    const login_name = ref("")
    const isUserLogged = ref(false)
    // Axios
    const axios = require('axios').default;
    axios.defaults.baseURL = 'http://localhost:5000/';


    const registerClient = (() => {
      const registerData = { 
        name: name.value,
        contact: email.value
        };
      
      axios.post('/clients',{
        data: registerData,
        headers: {
            'Content-Type': 'application/json',
        }
      })
      .then(function (response) {
          console.log(response);
      })
      .catch(function (response) {
          console.log(response);
      });
      })

    const loginClient = (() => {
      console.log("teste", login_name.value);

      axios.get('/clients', { params: { name: login_name.value } })
      .then(function (response) {
        console.log(response);
        isUserLogged.value = true
        console.log(isUserLogged.value)
      })
      .catch(function (error) {
        console.log(error);
        isUserLogged.value = false
      })
    })

    const listClients = (() => {
      axios.get('/clients', { params: { name: name.value } })
      .then(function (response) {
        console.log(response);
      })
      .catch(function (error) {
        console.log(error);
      })
      .then(function () {
        // always executed
      });  
    })

    return{
      name,
      email,
      password,
      login_name,
      registerStep,
      isUserLogged,
      registerClient,
      listClients,
      loginClient
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #0004f8;
}



</style>
