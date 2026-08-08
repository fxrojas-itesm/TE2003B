#include <stdio.h>
#include <math.h>

// ── Data only ───────────────────────────────
typedef struct {
    double x;
    double y;
} Point;

// ── Functions are separate, take a pointer ──
Point point_create(double x, double y)
{
    Point p;
    p.x = x;
    p.y = y;
    return p;
}

double point_distance(const Point* a, const Point* b)
{
    double dx = a->x - b->x;
    double dy = a->y - b->y;
    return sqrt(dx * dx + dy * dy);
}

void point_print(const Point* p)
{
    printf("(%0.2f, %0.2f)\n", p->x, p->y);
}

// ── Usage ───────────────────────────────────
int main()
{
    Point a = point_create(3.0, 4.0);
    Point b = point_create(6.0, 8.0);

    point_print(&a);
    point_print(&b);
    printf("Distance: %0.2f\n", point_distance(&a, &b));

    return 0;
}
