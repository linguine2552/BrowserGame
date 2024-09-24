// Constants
const GRAVITY = 0.5;
const JUMP_FORCE = -10;
const MOVE_SPEED = 5;
const GROUND_FRICTION = 0.8;
const AIR_RESISTANCE = 0.95;

class Physics {
  constructor(canvasWidth, canvasHeight, groundHeight) {
    this.canvasWidth = canvasWidth;
    this.canvasHeight = canvasHeight;
    this.groundY = canvasHeight - groundHeight;
  }

  update(player) {
    // Apply gravity
    player.velocityY += GRAVITY;

    // Apply air resistance
    player.velocityX *= AIR_RESISTANCE;

    // Update position
    player.x += player.velocityX;
    player.y += player.velocityY;

    // Ground collision
    if (player.y + player.height > this.groundY) {
      player.y = this.groundY - player.height;
      player.velocityY = 0;
      player.isJumping = false;

      // Apply ground friction
      player.velocityX *= GROUND_FRICTION;
    }

    // Wall collisions
    if (player.x < 0) {
      player.x = 0;
      player.velocityX = 0;
    } else if (player.x + player.width > this.canvasWidth) {
      player.x = this.canvasWidth - player.width;
      player.velocityX = 0;
    }
  }

  jump(player) {
    if (!player.isJumping) {
      player.velocityY = this.JUMP_FORCE;
      player.isJumping = true;
    }
  }

  moveLeft(player) {
    player.velocityX = -this.MOVE_SPEED;
  }

  moveRight(player) {
    player.velocityX = this.MOVE_SPEED;
  }

  stopMoving(player) {
    player.velocityX = 0;
  }
}

export default Physics;