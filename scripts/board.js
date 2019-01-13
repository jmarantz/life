class Board {
  constructor(width, height) {
    /** @private {number} */
    this.width_ = width;
    /** @private {height} */
    this.height_ = height;
    /** @private {!Array<!Array<number>>} */
    this.rows_ = [];
    for (let i = 0; i < height; ++i) {
      this.rows_.push([]);
    }
    /** @private {!HTMLElement} */
    this.canvas_ = document.getElementById('board');
    /** @private {!CanvasRenderingContext2D} */
    this.context_ = this.canvas_.getContext('2d');
    /** @private {string} */
    this.liveFillStyle_ = 'rgb(200, 0, 0)';
    /** @private {string} */
    this.deadFillStyle_ = 'rgb(220, 220, 220)';
    /** @private {number} */
    this.intervalMs_ = 20;
  }

  /**
   * Draws a new state for the board, which is expressed as an array of
   * arrays of true column-indices. We draw using deltas, as usually
   * in Life most cells don't change, so this is faster and less
   * flickery than redrawing the entire board.
   *
   * @param {{!Array<!Array<number>>} rows
   * @return {void}
   */
  draw(rows) {
    if (rows.length != this.height_) {
      console.log("incoming rows has wrong height " + rows.length + " should be " + this.height_);
      return;
    }

    const x_factor = Math.floor(this.canvas_.clientWidth / this.width_);
    const y_factor = Math.floor(this.canvas_.clientHeight / this.height_);

    for (let r = 0; r < this.height_; ++r) {
      const y = r * y_factor;
      const oldRow = this.rows_[r];
      let oldIndex = 0;
      const newRow = rows[r];
      let newIndex = 0;

      while (true) {
        const oldColumn = (oldIndex < oldRow.length) ? oldRow[oldIndex] : this.width_;
        const newColumn = (newIndex < newRow.length) ? newRow[newIndex] : this.width_;
        if (oldColumn == newColumn) {
          if (oldColumn == this.width_) {
            break;
          }
          ++oldIndex;
          ++newIndex;
        } else if (newColumn < oldColumn) {
          this.context_.fillStyle = this.liveFillStyle_;
          this.context_.fillRect(newColumn * x_factor, y, x_factor, y_factor);
          ++newIndex;
        } else if (oldColumn < newColumn) {
          this.context_.fillStyle = this.deadFillStyle_;
          this.context_.fillRect(oldColumn * x_factor, y, x_factor, y_factor);
          ++oldIndex;
        }
      }
    }
    this.rows_ = rows;
  }

  step() {
    const step_api = window.location.origin + '/step';
    window.fetch(step_api).then(response => response.json())
      .then(jsonResponse => {
        this.draw(jsonResponse);
        window.setTimeout(() => this.step(), this.intervalMs_);
      });
  }

  load() {
    const load_api = window.location.origin + '/board?width=' + 
          this.width_ + '&height=' + this.height_ + '&density=0.35';
    window.fetch(load_api).then(response => response.json())
      .then(jsonResponse => {
        this.draw(jsonResponse);
        window.setTimeout(() => this.step(), this.intervalMs_);
      });
  }
};
