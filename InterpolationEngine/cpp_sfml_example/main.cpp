#include "Interpolated.hpp"
#include <SFML/Graphics.hpp>


// Global clock for our time provider
sf::Clock globalClock;
float getElapsedTime() { return globalClock.getElapsedTime().asSeconds(); }

int main() {
  sf::RenderWindow window(sf::VideoMode(800, 600), "Interpolation Example");
  window.setFramerateLimit(60);

  // Setup the time provider for our Interpolated class
  Interpolated<float>::setTimeProvider(getElapsedTime);

  // Create an interpolated position (x coordinate)
  Interpolated<float> posX(100.0f, 1.0f); // start at 100, duration 1s
  posX.setEasing(Easing::EaseOutElastic);

  sf::RectangleShape shape(sf::Vector2f(50.f, 50.f));
  shape.setFillColor(sf::Color::Green);

  while (window.isOpen()) {
    sf::Event event;
    while (window.pollEvent(event)) {
      if (event.type == sf::Event::Closed)
        window.close();

      if (event.type == sf::Event::MouseButtonPressed) {
        if (event.mouseButton.button == sf::Mouse::Left) {
          // Move to mouse X on click
          posX = (float)event.mouseButton.x;
        }
      }
    }

    // Update
    shape.setPosition(posX, 300.f); // Implicitly calls getValue()

    // Render
    window.clear();
    window.draw(shape);
    window.display();
  }

  return 0;
}
