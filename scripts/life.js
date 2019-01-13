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
    this.liveContext_ = this.canvas_.getContext('2d');
    this.liveContext_.fillStyle = 'rgb(200, 0, 0)';
    /** @private {!CanvasRenderingContext2D} */
    this.deadContext_ = this.canvas_.getContext('2d');
    this.deadContext_.fillStyle = 'rgb(220, 220, 220)';
  }

  /**
   * Draws a new state for the board, which is expressed as an array of
   * arrays of true column-indices. We don't redraw all the pixels on
   * each call to draw() -- we insead draw only the changes.
   *
   * @param {{!Array<!Array<number>>} rows
   * @return {void}
   */
  draw(rows) {
    if (rows.length != this.height_) {
      console.log("incoming rows has wrong height " + rows.length + " should be " + this.height);
      return;
    }

    const x_factor = Math.floor(this.canvas.clientWidth / this.width_);
    const y_factor = Math.floor(this.canvas.clientHeight / this.height_);

    for (let r = 0; r < this.height_; ++r) {
      const y = r * y_factor;
      const oldRow = this.rows_[r];
      let oldIndex = 0;
      const newRow = rows[r];
      let newIndex = 0;

      while (true) {
        const oldColumn = (oldIndex < oldRow.length) ? oldRow[oldIndex] : null;
        const newColumn = (newIndex < newRow.length) ? newRow[newIndex] : null;
        if ((oldColumn == null) && (newColumn == null)) {
          break;
        }
        if ((oldColumn == null) || (newColumn < oldColumn)) {
          this.liveContext_.fillRect(newColumn * x_factor, y, xfactor, y_factor);
          ++newIndex;
        } else if ((newColumn == null) || (oldColumn < newColumn)) {
          this.deadContext_.fillRect(oldColumn * x_factor, y, xfactor, y_factor);
          ++oldIndex;
        }
      }
    }
  }
};
