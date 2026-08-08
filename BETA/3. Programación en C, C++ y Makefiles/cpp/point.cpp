#include <iostream>
#include <cmath>

class Point {
private:                          // ← Access control (hidden from outside)
    double x;
    double y;

public:
    // ── Constructor (replaces point_create) ──
    Point(double x, double y)
    {
        this->x = x;
        this->y = y;
    }

    // ── Methods live inside the class ────────
    double distance(const Point& other) const
    {
        double dx = this->x - other.x;
        double dy = this->y - other.y;
        return std::sqrt(dx * dx + dy * dy);
    }

    void print() const
    {
        std::cout << "(" << x << ", " << y << ")" << std::endl;
    }

    // ── Getters (controlled access to private data) ──
    double getX() const { return x; }
    double getY() const { return y; }
};

// ── Usage ───────────────────────────────────
int main()
{
    Point a(3.0, 4.0);           // Constructor called automatically
    Point b(6.0, 8.0);

    a.print();                   // Method called ON the object
    b.print();
    std::cout << "Distance: " << a.distance(b) << std::endl;

    return 0;
}
