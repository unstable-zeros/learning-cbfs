let valid_modes = ['manual', 'follow']

class Controller {
  constructor(mode) {

    if (valid_modes.includes(mode)) {
      this._mode = mode;
    } else{
      throw "Input " + mode + " is not a valid mode."
    }

    this._leader = null;
    this._keys = null;
  }

  get keys() {
    return this._keys;
  }

  set keys(key_dict) {
    /* key_dict: Map instance - keys used to control airplane. */
    this._keys = key_dict;
  }

  get leader() {
    return this._leader;
  }

  set leader(airplane) {
    this._leader = airplane;
  }

  get mode() {
    return this._mode;
  }
}
