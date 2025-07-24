import time
import connect_python
import math


@connect_python.main
def stream_data(client: connect_python.Client):
    print("Starting orbit replay stream", flush=True)

    client.clear_stream("sat1")
    client.clear_stream("sat2")
    client.clear_stream("sat3")

    last_tick = time.time()
    timestamp = 0.0

    while True:
        now = time.time()
        delta = now - last_tick
        last_tick = now
        timestamp += delta

        movement_speed = 0.1

        # Fake an orbit
        lat = math.sin(timestamp * movement_speed * 0.9) * 20.0
        lon = math.degrees(timestamp * movement_speed) % 360
        altitude = 5_900_000 + math.sin(timestamp * movement_speed * 100.0) * 12.7

        client.stream(
            "sat1",
            timestamp,
            names=["latitude", "longitude", "altitude", "pitch", "roll", "heading"],
            values=[lat, lon, altitude, 0, 0, 0],
        )

        # Fake another orbit
        lat = -math.sin(timestamp * movement_speed * 0.9) * 24.0
        lon = 180 - (math.degrees(timestamp * movement_speed) * 0.7) % 360
        altitude = 5_900_000 + math.sin(timestamp * movement_speed * 100.0) * 12.7

        client.stream(
            "sat2",
            timestamp,
            names=["latitude", "longitude", "altitude", "pitch", "roll", "heading"],
            values=[lat, lon, altitude, 0, 0, 0],
        )

        # Fake another orbit
        lat = 8.0 - math.sin(timestamp * movement_speed * 1.7) * 12.0
        lon = 230 - (math.degrees(timestamp * movement_speed) * 1.2) % 360
        altitude = 5_900_000 + math.sin(timestamp * movement_speed * 100.0) * 12.7

        client.stream(
            "sat3",
            timestamp,
            names=["latitude", "longitude", "altitude", "pitch", "roll", "heading"],
            values=[lat, lon, altitude, 0, 0, 0],
        )

        time.sleep(0.01)  # Add a small delay


if __name__ == "__main__":
    stream_data()
