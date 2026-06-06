def find_direction(x1, y1, x2, y2):
    distance_x = x2-x1
    distance_y = y2-y1

    if distance_x < 0:
        x = -1
    elif distance_x == 0:
        x = 0
    elif distance_x > 0:
        x = 1

    if distance_y < 0:
        y = -1
    elif distance_y == 0:
        y = 0
    elif distance_y > 0:
        y = 1
    
    return x, y

def avg(x,y):
    return (x+y)/2

def distance(x1,y1, x2,y2):
    dx = x2 - x1
    dy = y2 - y1

    return (dx**2 + dy**2)

def is_valid_food(food):
        if food is None:
            return False

        if food.type == 'plant':
            return not food.eaten

        if food.type == 'object':
            return not food.eaten

        if food.type == 'animal':
            return not food.dead

def print_info(world):

        def stats(group):
            if len(group) == 0:
                return {
                    "count": 0,
                    "speed": 0,
                    "vision": 0,
                    "size": 0,
                    "energy": 0
                }

            return {
                "count": len(group),
                "speed": round(sum(a.speed for a in group) / len(group), 2),
                "vision": round(sum(a.vision for a in group) / len(group), 2),
                "size": round(sum(a.size for a in group) / len(group), 2),
                "energy": round(sum(a.energy for a in group) / len(group), 2)
            }

        mieso = stats(world.miesozerni)
        rosli = stats(world.roslinozerni)
        padli = stats(world.padlinozerni)

        print("\n" + "=" * 90)
        print(f"ITERACJA: {world.settings.iterator}")
        print("=" * 90)

        print(
            f"{'STAT':<15}"
            f"{'MIESOZERNE':<20}"
            f"{'ROSLINOZERNE':<20}"
            f"{'PADLINOZERNE':<20}"
        )

        print("-" * 90)

        print(
            f"{'LICZBA':<15}"
            f"{mieso['count']:<20}"
            f"{rosli['count']:<20}"
            f"{padli['count']:<20}"
        )

        print(
            f"{'SPEED':<15}"
            f"{mieso['speed']:<20}"
            f"{rosli['speed']:<20}"
            f"{padli['speed']:<20}"
        )

        print(
            f"{'VISION':<15}"
            f"{mieso['vision']:<20}"
            f"{rosli['vision']:<20}"
            f"{padli['vision']:<20}"
        )

        print(
            f"{'SIZE':<15}"
            f"{mieso['size']:<20}"
            f"{rosli['size']:<20}"
            f"{padli['size']:<20}"
        )

        print(
            f"{'ENERGY':<15}"
            f"{mieso['energy']:<20}"
            f"{rosli['energy']:<20}"
            f"{padli['energy']:<20}"
        )

        print("=" * 90)