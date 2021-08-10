<template>

  <div v-if="!isUserLogged">    
    <div class="form">
    <form v-if="registerStep" class="register-form">
      <input v-model="name" type="text" placeholder="name"/>
      <input v-model="email" type="text" placeholder="email address"/>
      <input v-model="password" type="password" placeholder="password"/>
      <button @click="registerClient">create</button>
      <p class="message">Already registered? 
        <a @click="(registerStep = false)" href="#">Sign In </a>
      </p>
    </form>

    <form v-else class="login-form">
      <input v-model="login_name" type="text" placeholder="username"/>
      <input type="password" placeholder="password"/>
      <button @click="loginClient();clientSubscriptions();setupStream()">login</button>
      <p class="message">Not registered? 
        <a @click="(registerStep = true)" href="#">Create an account</a>
      </p>
    </form>
    </div>
  </div>
  <div v-else>

    <h1> Hello {{ login_name }}</h1>
    <h2> These are your active subscriptions: </h2>
    <h3> - As a driver: </h3>
    <div class="tables">
      <table border >
          <thead>
            <tr>
              <th> ID </th>
              <th> Date </th>
              <th> Origin </th>
              <th> Destination </th>
              <th> Passengers </th>
            </tr>
          </thead>
            <tr v-for="(subs, i) in clientSubscriptionsList['rides']" :key="i">
              <td> {{ subs.id }} </td>
              <td> {{ subs.date }} </td>
              <td> {{ subs.origin }} </td>
              <td> {{ subs.destination }} </td>
              <td> {{ subs.passengers }} </td>
            </tr>
        </table>
    </div>
    <h3> - As a passenger: </h3>
    <div class="tables">
      <table border>
          <thead>
            <tr>
              <th> ID </th>
              <th> Date </th>
              <th> Origin </th>
              <th> Destination </th>
            </tr>
          </thead>
            <tr v-for="(subs, i) in clientSubscriptionsList['requests']" :key="i">
              <td> {{ subs.id }} </td>
              <td> {{ subs.date }} </td>
              <td> {{ subs.origin }} </td>
              <td> {{ subs.destination }} </td>
            </tr>
        </table>
    </div>
    
    <h4> Add subscriptions </h4>
      <h5> Driver </h5>
      <form class="register-form">
        <input v-model="d_origin" placeholder="Origin"/>
        <input v-model="d_destination" placeholder="Destination"/>
        <input v-model="d_date" placeholder="Date"/>
        <input v-model="passengers" placeholder="Number of passengers"/>
        <button @click="(isPassenger = false);addSubscription()"> Submit </button>
      </form>
      <h5> Passenger </h5>
      <form class="register-form">
        <input v-model="p_origin" placeholder="Origin"/>
        <input v-model="p_destination" placeholder="Destination"/>
        <input v-model="p_date" placeholder="Date"/>
        <button @click="(isPassenger = true);addSubscription()"> Submit </button>
      </form>

    <h4> Search Available Rides </h4>
    <form class="register-form">
      <input v-model="s_origin" placeholder="Origin"/>
      <input v-model="s_destination" placeholder="Destination"/>
      <input v-model="s_date" placeholder="Date"/>
      <button @click="availableRides"> Submit </button>
    </form>
    <br>
    <div class="tables">
      <table border>
          <thead>
            <tr>
              <th> ID </th>
              <th> Date </th>
              <th> Origin </th>
              <th> Destination </th>
            </tr>
          </thead>
            <tr v-for="(subs, i) in availableRidesList" :key="i">
              <td> {{ subs.id }} </td>
              <td> {{ subs.date }} </td>
              <td> {{ subs.origin }} </td>
              <td> {{ subs.destination }} </td>
            </tr>
        </table>
    </div>

    <h4> Delete subscriptions </h4>
    <form class="register-form">
      <input v-model="subToBeDeleted" placeholder="ID to be deleted"/>
      <button @click="delSubscription();clientSubscriptions()"> Delete </button>
    </form>
    
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
    //// Driver
    const d_date = ref("")
    const d_origin = ref("")
    const passengers = ref("")
    const d_destination = ref("")

    //// Passenger
    const p_date = ref("")
    const p_origin = ref("")
    const p_destination = ref("")

    //// Search
    const s_date = ref("")
    const s_origin = ref("")
    const s_destination = ref("")

    //// Code
    const name = ref("")
    const date = ref("")
    const email = ref("")
    const password = ref("")
    const login_name = ref("")
    const subToBeDeleted = ref(0)
    const notification = ref(false)
    const registerStep = ref(true)
    const isUserLogged = ref(false)
    const isPassenger = ref(true)
    const availableRidesList = ref("")
    const clientSubscriptionsList = ref("")

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
      })
      .finally(function () {
          registerStep.value = false
          name.value = ""
          email.value = ""
          password.value = ""
      })
    })

    const loginClient = (() => {

      axios.get('/clients/'+login_name.value)
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

    const delSubscription = (() => {
     
      axios.delete('/subscriptions/'+subToBeDeleted.value)
      .then(function (response) {
          console.log(response);
      })
      .catch(function (response) {
          console.log(response);
      })
      .finally(function (){
        clientSubscriptions()
      });
    })

    const addSubscription = (() => {
      const subData = {}

      if (isPassenger.value){
        subData.value = {
          name: login_name.value, 
          date: p_date.value,
          origin: p_origin.value,
          destination: p_destination.value,
        };
      }
      else{
        subData.value = {
          name: login_name.value, 
          date: d_date.value,
          origin: d_origin.value,
          destination: d_destination.value,
          passengers: passengers.value,
        };
      }
      
      axios.post('/subscriptions',{
        data: subData.value,
        headers: {
            'Content-Type': 'application/json',
        }
      })
      .then(function (response) {
          console.log(response);
      })
      .catch(function (response) {
          console.log(response);
      })
      .finally(function (){
        clientSubscriptions()
      });
    })

    const availableRides = (() => {

      const params = {
        origin: s_origin.value,
        destination: s_destination.value,
        date: s_date.value
      };

      axios.get('/subscriptions/rides', {params} )
      .then(function (response) {
        availableRidesList.value = response.data
        console.log(response);
      })
      .catch(function (error) {
        console.log(error);
      })
    }) 

    const clientSubscriptions = (() => {

      axios.get('/subscriptions/'+login_name.value)
      .then(function (response) {
        clientSubscriptionsList.value = response.data
        console.log(response);
      })
      .catch(function (error) {
        console.log(error);
      })
    }) 

    const setupStream = (() => {
      var source = new EventSource("http://localhost:5000/stream?channel="+login_name.value);
      source.addEventListener('publish', function(event) {
          var data = JSON.parse(event.data);
          console.log("data:",data["id"])
          // If ID is even, then new passenger available. Odd means new ride available.
          if(!(data["id"] % 2)){
            alert("New passenger available for ride"+data["id"]+": "+ data["name"]+" - "+data["contact"] );
          }
          else{
           alert("New ride available for subscription"+data["id"]+": "+ data["name"]+" - "+data["contact"] );
          }
      
      }, false);
    })

    return{
      d_date,
      d_destination,
      d_origin,
      p_date,
      p_destination,
      p_origin,
      s_date,
      s_destination,
      s_origin,
      name,
      notification,
      date,
      email,
      origin,
      password,
      passengers,
      login_name,
      loginClient,
      isPassenger,
      setupStream,
      registerStep,
      isUserLogged,
      subToBeDeleted,
      availableRides,
      registerClient,
      delSubscription,
      addSubscription,
      availableRidesList,
      clientSubscriptions,
      clientSubscriptionsList
    }
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.tables {
  display: grid;
}

.alert-message {
    padding: 15px;
    width: 50%;
    align-content: center;
    background: red;
    display: inline-table;
    color: white;
}

a {
  color: #0004f8;
}

</style>
