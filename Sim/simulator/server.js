let express = require('express');
let app = express();
let server = app.listen(3000);

app.use(express.static('public'));

console.log('My server is running');

let socket = require('socket.io');
let io = socket(server);

io.sockets.on('connection', newConnection);

let base_dir = './data/'

function newConnection(socket) {
  console.log('new connection: ' + socket.id);

  socket.on('airplane1', get_A1_data);
  socket.on('airplane2', get_A2_data);
  socket.on('config', get_config)

  function get_A1_data(data) {
    write_to_json(base_dir + 'airplane1', data);
  }

  function get_A2_data(data) {
    write_to_json(base_dir + 'airplane2', data);
  }

  function get_config(data) {
    write_to_json(base_dir + 'config', data);
  }
}

function write_to_json(name, data) {
  let fs = require("fs");
  fs.writeFile(name + ".json", JSON.stringify(data), (err) => {
    if (err) {
        console.error(err);
        return;
    };
    console.log("File has been created");
  });
}
