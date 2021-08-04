const axios = require('axios').default;

axios.defaults.baseURL = 'http://localhost:8080/';

// Optionally the request above could also be done as
axios.get('/api/v1/customer-wallets')
  .then(function (response) {
    console.log(response);
  })
  .catch(function (error) {
    console.log(error);
  })
  .then(function () {
    // always executed
  });  
