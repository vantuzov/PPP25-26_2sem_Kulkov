import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MatplotPolygon
import itertools
import functools
import math


def visualize(polygons_iter, ax=None, color='blue', alpha=0.5, title=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_aspect('equal')
    polygons = list(polygons_iter)
    if not polygons:
        if title:
            ax.set_title(title)
        return ax
    for poly in polygons:
        patch = MatplotPolygon(poly, closed=True, facecolor=color, edgecolor='black', alpha=alpha)
        ax.add_patch(patch)
    all_x = [x for poly in polygons for x, y in poly]
    all_y = [y for poly in polygons for x, y in poly]
    if all_x and all_y:
        margin_x = max(1, (max(all_x) - min(all_x)) * 0.1)
        margin_y = max(1, (max(all_y) - min(all_y)) * 0.1)
        ax.set_xlim(min(all_x) - margin_x, max(all_x) + margin_x)
        ax.set_ylim(min(all_y) - margin_y, max(all_y) + margin_y)
    if title:
        ax.set_title(title)
    return ax


def gen_rectangle(w, h, step, count=None):
    gen = map(lambda i: ((i * step, 0), (i * step, h), (i * step + w, h), (i * step + w, 0)),
              itertools.count())
    return itertools.islice(gen, count) if count is not None else gen


def gen_triangle(side, step, count=None):
    h = side * math.sqrt(3) / 2
    gen = map(lambda i: ((i * step, 0), (i * step + side / 2, h), (i * step + side, 0)),
              itertools.count())
    return itertools.islice(gen, count) if count is not None else gen


def gen_hexagon(side, step, count=None):
    h = side * math.sqrt(3) / 2
    gen = map(lambda i: ((i * step - side / 2, h), (i * step + side / 2, h),
                         (i * step + side, 0), (i * step + side / 2, -h),
                         (i * step - side / 2, -h), (i * step - side, 0)),
              itertools.count())
    return itertools.islice(gen, count) if count is not None else gen


def tr_translate(poly, dx, dy):
    return tuple((x + dx, y + dy) for x, y in poly)


def tr_rotate(poly, angle):
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return tuple((x * cos_a - y * sin_a, x * sin_a + y * cos_a) for x, y in poly)


def tr_symmetry(poly, axis='y'):
    if axis == 'y':
        return tuple((-x, y) for x, y in poly)
    elif axis == 'x':
        return tuple((x, -y) for x, y in poly)
    return tuple((-x, -y) for x, y in poly)


def tr_homothety(poly, k):
    return tuple((x * k, y * k) for x, y in poly)


def poly_area(poly):
    n = len(poly)
    return 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % n][1] -
                         poly[(i + 1) % n][0] * poly[i][1] for i in range(n)))


def poly_perimeter(poly):
    n = len(poly)
    return sum(math.hypot(poly[i][0] - poly[(i + 1) % n][0],
                          poly[i][1] - poly[(i + 1) % n][1]) for i in range(n))


def min_side(poly):
    n = len(poly)
    return min(math.hypot(poly[i][0] - poly[(i + 1) % n][0],
                          poly[i][1] - poly[(i + 1) % n][1]) for i in range(n))


def max_side(poly):
    n = len(poly)
    return max(math.hypot(poly[i][0] - poly[(i + 1) % n][0],
                          poly[i][1] - poly[(i + 1) % n][1]) for i in range(n))


def min_dist_origin(poly):
    return min(math.hypot(x, y) for x, y in poly)


def is_convex(poly):
    n = len(poly)
    if n < 3:
        return False

    def cross_product(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    signs = set()
    for i in range(n):
        cp = cross_product(poly[i], poly[(i + 1) % n], poly[(i + 2) % n])
        if cp != 0:
            signs.add(cp > 0)
    return len(signs) <= 1


def point_in_poly(point, poly):
    x, y = point
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x or x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def flt_convex_polygon(poly):
    return is_convex(poly)


def flt_angle_point(poly, point):
    return any(math.isclose(x, point[0], abs_tol=1e-9) and
               math.isclose(y, point[1], abs_tol=1e-9) for x, y in poly)


def flt_square(poly, max_area):
    return poly_area(poly) < max_area


def flt_short_side(poly, min_s):
    return min_side(poly) < min_s


def flt_point_inside(poly, point):
    return is_convex(poly) and point_in_poly(point, poly)


def flt_polygon_angles_inside(poly, other_poly):
    return is_convex(poly) and any(point_in_poly(vertex, poly) for vertex in other_poly)


def flt_convex_polygon_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return filter(flt_convex_polygon, func(*args, **kwargs))

    return wrapper


def flt_angle_point_decorator(point):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return filter(lambda p: flt_angle_point(p, point), func(*args, **kwargs))

        return wrapper

    return decorator


def flt_square_decorator(max_area):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return filter(lambda p: flt_square(p, max_area), func(*args, **kwargs))

        return wrapper

    return decorator


def tr_translate_decorator(dx, dy):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return map(lambda p: tr_translate(p, dx, dy), func(*args, **kwargs))

        return wrapper

    return decorator


def tr_rotate_decorator(angle):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return map(lambda p: tr_rotate(p, angle), func(*args, **kwargs))

        return wrapper

    return decorator


def agr_origin_nearest(polys):
    return functools.reduce(lambda p1, p2: p1 if min_dist_origin(p1) < min_dist_origin(p2) else p2, polys)


def agr_max_side(polys):
    return functools.reduce(lambda p1, p2: p1 if max_side(p1) > max_side(p2) else p2, polys)


def agr_min_area(polys):
    return functools.reduce(lambda p1, p2: p1 if poly_area(p1) < poly_area(p2) else p2, polys)


def agr_perimeter(polys):
    return functools.reduce(lambda acc, p: acc + poly_perimeter(p), polys, 0.0)


def agr_area(polys):
    return functools.reduce(lambda acc, p: acc + poly_area(p), polys, 0.0)


def zip_polygons(*iterators):
    return map(lambda polys: sum(polys, ()), zip(*iterators))


def demonstrate_generators():
    rects = gen_rectangle(2, 1, 3, 7)
    tris = gen_triangle(2, 3, 7)
    hexs = gen_hexagon(2, 4, 7)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    visualize(rects, axes[0], color='lightblue', title="Rectangles")
    visualize(tris, axes[1], color='lightgreen', title="Triangles")
    visualize(hexs, axes[2], color='plum', title="Hexagons")
    plt.tight_layout()
    plt.show()


def demonstrate_transformations():
    ribbon1 = map(lambda p: tr_rotate(p, 30), gen_rectangle(2, 1, 3, 5))
    ribbon2 = map(lambda p: tr_translate(tr_rotate(p, 30), -2, 4), gen_rectangle(2, 1, 3, 5))
    ribbon3 = map(lambda p: tr_translate(tr_rotate(p, 30), -4, 8), gen_rectangle(2, 1, 3, 5))

    fig, ax = plt.subplots(figsize=(10, 8))
    visualize(ribbon1, ax, color='orange', title="Three parallel ribbons")
    visualize(ribbon2, ax, color='orange')
    visualize(ribbon3, ax, color='orange')
    plt.show()

    r1 = map(lambda p: tr_translate(tr_rotate(p, 30), 0, 5), gen_rectangle(2, 1, 3, 7))
    r2 = map(lambda p: tr_translate(tr_rotate(p, -30), 0, 8), gen_rectangle(2, 1, 3, 7))

    fig, ax = plt.subplots(figsize=(10, 8))
    visualize(r1, ax, color='red', title="Two intersecting ribbons")
    visualize(r2, ax, color='blue')
    plt.show()

    t1 = gen_triangle(2, 3, 7)
    t2 = map(lambda p: tr_translate(tr_symmetry(p, 'x'), 0, -2), gen_triangle(2, 3, 7))

    fig, ax = plt.subplots(figsize=(12, 6))
    visualize(t1, ax, color='yellow', title="Symmetric triangle ribbons")
    visualize(t2, ax, color='orange')
    plt.show()

    scales = [0.5, 1, 1.5, 2, 2.5]
    base_quad = ((0, 0), (0, 1), (1, 1), (1, 0))
    quads = map(lambda k: tr_homothety(base_quad, k), scales)
    quads_translated = map(lambda p: tr_translate(p, p[0][0] * 2, p[0][1] * 2), quads)

    fig, ax = plt.subplots(figsize=(10, 8))
    visualize(quads_translated, ax, color='purple', title="Quadrilaterals at different scales")
    plt.show()


def demonstrate_filters():
    scales = [0.3, 0.5, 0.7, 1, 1.2, 1.5, 1.8, 2, 2.2, 2.5, 2.8, 3, 3.2, 3.5, 3.8, 4, 4.2, 4.5, 4.8, 5]
    base_rect = ((0, 0), (0, 1), (1, 1), (1, 0))
    rects = (tr_homothety(base_rect, s) for s in scales)

    filtered = filter(lambda p: flt_short_side(p, 1.5) and flt_square(p, 10), rects)
    filtered_list = list(itertools.islice(filtered, 6))

    fig, ax = plt.subplots(figsize=(10, 8))
    visualize(filtered_list, ax, color='cyan', title=f"Filtered {len(filtered_list)} polygons")
    plt.show()


def demonstrate_zip_polygons():
    tri1 = gen_triangle(2, 3, 3)
    tri2 = map(lambda p: tr_translate(p, 0, -2), gen_triangle(2, 3, 3))

    zipped = zip_polygons(tri1, tri2)
    zipped_list = list(zipped)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    visualize(gen_triangle(2, 3, 3), axes[0], color='green', title="Original triangles")
    visualize(zipped_list, axes[1], color='red', title="Zipped polygons")
    plt.tight_layout()
    plt.show()


def demonstrate_decorators():
    @flt_convex_polygon_decorator
    @tr_rotate_decorator(45)
    def get_rotated_rectangles():
        return gen_rectangle(2, 1, 3, 10)

    @flt_square_decorator(5)
    def get_small_rectangles():
        return gen_rectangle(2, 1, 3, 10)

    rects_rotated = list(get_rotated_rectangles())
    small_rects = list(get_small_rectangles())

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    visualize(rects_rotated, axes[0], color='pink', title="Rotated rectangles")
    visualize(small_rects, axes[1], color='lightblue', title="Small rectangles")
    plt.tight_layout()
    plt.show()


def demonstrate_aggregate_functions():
    rects = list(gen_rectangle(2, 1, 3, 5))

    nearest = agr_origin_nearest(rects)
    max_side_poly = agr_max_side(rects)
    min_area_poly = agr_min_area(rects)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    visualize([nearest], axes[0], color='gold', title="Nearest to origin")
    visualize([max_side_poly], axes[1], color='coral', title="Max side")
    visualize([min_area_poly], axes[2], color='teal', title="Min area")
    plt.tight_layout()
    plt.show()


def run_scenarios():
    demonstrate_generators()
    demonstrate_transformations()
    demonstrate_filters()
    demonstrate_zip_polygons()
    demonstrate_decorators()
    demonstrate_aggregate_functions()


if __name__ == '__main__':
    run_scenarios()
