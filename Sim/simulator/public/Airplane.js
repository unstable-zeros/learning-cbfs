class Airplane {
  constructor(init_state, controller, name) {
    /* Constructor for Airplane class.

    Args:
      init_pos: dict          - initial (x, y) position of airplane and init theta.
      controller: Controller  - controller for airplane.
      name: str              - file name to write histories to.
    */

    this._pos = init_state['pos'].copy();
    this._theta = init_state['theta'];
    this._controller = controller;
    this._name = name;

    this._state_history = new Array();
    this._action_history = new Array();

    this._speed = config['speed']['init'];
    this._ang_speed = config['ang_speed']['init'];
  }

  get last_action() {
    return this._action_history.slice(-1).pop();
  }

  get speed() {
    return this._speed;
  }

  get ang_speed() {
    return this._ang_speed;
  }

  get pos() {
    return this._pos;
  }

  show() {
    /* Show airplane in current position */

    fill(255);
    this.draw_plane();
    // this.draw_arrow();

  }


  update() {
    /* Control airplane angle and whether it moves or not. */

    this.show();

    // update state
    let state = [this._pos.x, this._pos.y, this._theta];
    this._state_history.push(state);

    // update action
    let action = this.sense_action();
    this.apply_action(action);
    this._action_history.push(action);
  }

  apply_action(action) {
    /* Apply action to update airplane state

    Args:
      action: array - velocity_x, velocity_y, ang_velocity triple.

    Modifies:
      current state of airplane.
    */

    this._pos.x += action[0] * cos(this._theta);
    this._pos.y += action[0] * sin(this._theta);
    this._theta += action[1];
  }

  sense_action() {
    if (this._controller.mode == 'manual') {

      if (keyIsDown(this._controller.keys.get('accelerate'))) {
        if (this._speed < config['speed']['max']) {
          this._speed += config['speed']['step'];
        }
      }

      if (keyIsDown(this._controller.keys.get('decelerate'))) {
        if (this._speed > config['speed']['min']) {
          this._speed -= config['speed']['step'];
        }
      }

      if (keyIsDown(this._controller.keys.get('ang_accelerate'))) {
        if (this._ang_speed < config['ang_speed']['max']) {
          this._ang_speed += config['ang_speed']['step'];
        }
      }

      if (keyIsDown(this._controller.keys.get('ang_decelerate'))) {
        if (this._ang_speed > config['ang_speed']['min']) {
          this._ang_speed -= config['ang_speed']['step'];
        }
      }
    } else if (this._controller.mode == 'follow') {
      this._speed = this._controller.leader.speed;
      this._ang_speed = this._controller.leader.ang_speed;
    }

    return [this._speed, this._ang_speed]
  }

  send_history(socket) {
    /* Send airplane trajectory data to Node server

    Args:
      socket: Node socket - reference to node server.
    */

    let all_history = [];

    for (let i = 0; i < this._state_history.length; i++) {
      all_history.push({
        time: i,
        data: {
          state: this._state_history[i],
          action: this._action_history[i]
        }
      });
    }

    socket.emit(this._name, all_history);
  }

  draw_plane() {
    /* Draw airplane */

    push();
    translate(this._pos.x, this._pos.y);
    rotate(this._theta);
    stroke('gray');
    fill('gray');
    ellipse(0, 0, 60, 10);
    triangle(0, -20, 10, 0, 0, 20);
    quad(10, 0, -5, 30, -4, 20, 5, 0);
    quad(10, 0, -5, -30, -4, -20, 5, 0);
    quad(-20, 0, -30, 10, -35, 10, -25, 0);
    quad(-20, 0, -30, -10, -35, -10, -25, 0);
    ellipse(5, -10, 10, 5);
    ellipse(5, 10, 10, 5);
    pop();

    this.draw_plane_num();
  }

  draw_arrow() {
    /* Draw arrow in direction of airplane. */

    let arrow_size = 50;

    push();
    fill('green');
    translate(this._pos.x, this._pos.y);
    rotate(this._theta);
    stroke('green');
    strokeWeight(3);
    line(0, 0, arrow_size, 0);
    translate(arrow_size * 5 / 6, 0);
    triangle(0, 3, 0, -3, 6, 0);
    pop();
  }

  draw_plane_num() {
    textSize(10);
    fill(0);
    stroke(0);
    if (this._name == 'airplane1') {
      text('1', this._pos.x, this._pos.y);
    } else if (this._name == 'airplane2') {
      text('2', this._pos.x, this._pos.y);
    }
  }

}
