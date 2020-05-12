let S_KEY = 83;
let W_KEY = 87;
let Z_KEY = 90;
let socket;

let config = {
  'speed' : {
    'max': 5,
    'min': 0.5,
    'step': 0.2,
    'init': 2
  },
  'ang_speed': {
    'max': 0.1,
    'min': -0.1,
    'step': 0.004,
    'init': 0
  },
  'center_radius': 50,
  'launch_radius': 20,
  'world_size': {
    'x': 961,
    'y': 721
  },
  'freq': 30
}

function setup() {
  createCanvas(config['world_size']['x'], config['world_size']['y']);
  init_pts = get_starting_pts('rand');

  // Create LHS airplane
  let cont1 = new Controller('manual');
  cont1.keys = new Map([
    ['accelerate', RIGHT_ARROW],
    ['decelerate', LEFT_ARROW],
    ['ang_accelerate', DOWN_ARROW],
    ['ang_decelerate', UP_ARROW]
  ]);
  airplane1 = new Airplane(init_pts['airplane1'], cont1, 'airplane1');

  // Create RHS airplane
  let cont2 = new Controller('follow');
  cont2.leader = airplane1;
  airplane2 = new Airplane(init_pts['airplane2'], cont2, 'airplane2');

  rectMode(CENTER);
  socket = io.connect('http://localhost:3000');
  frameRate(config['freq']);
}

function draw() {
  draw_world(init_pts);

  airplane1.update();
  airplane2.update();

  if (keyIsDown(ENTER)) {
    console.log('Manually stopped program.');
    send_results(airplane1, airplane2, socket);
  }

  if (check_if_complete(airplane1) == true) {
    console.log('Airplanes reached their goals safely.');
    send_results(airplane1, airplane2, socket);
  }
}

function draw_world(init_pts) {
  /* Draw world with goal locations, grid, and center point. */

  background(255);
  draw_grid();

  stroke('orange');
  fill('orange');
  circle(width/2, height/2, 2 * config['center_radius']);

  fill('red');
  square(init_pts['airplane1']['pos'].x, init_pts['airplane1']['pos'].y, 2 * config['launch_radius']);
  square(init_pts['airplane2']['pos'].x, init_pts['airplane2']['pos'].y, 2 * config['launch_radius']);
}

function draw_grid() {
  /* Draw background grid in canvase. */

  stroke(87);
  for (let i = 0; i < width; i += 48) {
    line(i, 0, i, height);
  }

  for (let j = 0; j < height; j += 48) {
    line(0, j, width, j);
  }
}

function get_starting_pts(type) {

  if (type == 'default') {
    x1 = 100;
    x2 = width - 100;
    y1 = y2 = height / 2;

    theta = 0;

  } else if (type == 'rand') {
    x1 = Math.random() * width / 3;
    y1 = Math.random() * height;
    x2 = width - x1;
    y2 = height - y1;

    theta = atan2(height/2 - y1, width/2 - x1);
  }

  return {
    'airplane1': {
      'pos': new p5.Vector(x1, y1, theta),
      'theta': theta
    },
    'airplane2': {
      'pos': new p5.Vector(x2, y2, theta),
      'theta': theta + PI
    }
  }
}

function check_if_complete(airplane) {
  /* Check if airplanes have reached goal

  Args:
    airplane: Airplane
  */
  let x1 = airplane1.pos.x;
  let y1 = airplane.pos.y;
  let x2 = init_pts['airplane2']['pos'].x;
  let y2 = init_pts['airplane2']['pos'].y;
  let radius = config['launch_radius'];

  if (x1 >= (x2 - radius) && x1 <= (x2 + radius)) {
    if (y1 >= (y2 - radius) && y1 <= (y2 + radius)) {
      return true;
    }
  }

  return false;
}

function send_results(airplane1, airplane2, socket) {
  airplane1.send_history(socket);
  airplane2.send_history(socket);
  socket.emit('config', config);
  noLoop();
}
