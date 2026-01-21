import streamlit as st
import random

# =====================
# MODELS
# =====================

class Stage:
    def __init__(self, name, length_km, surface, roughness, speed, description):
        self.name = name
        self.length_km = length_km
        self.surface = surface
        self.roughness = roughness    # 0–1
        self.speed = speed            # 0–1
        self.description = description


class Car:
    def __init__(self, name, power, weight, drivetrain, reliability):
        self.name = name
        self.power = power
        self.weight = weight
        self.drivetrain = drivetrain  # AWD / FWD / RWD
        self.reliability = reliability


class Setup:
    def __init__(self, suspension, ride_height, gearing, tire_type):
        self.suspension = suspension
        self.ride_height = ride_height
        self.gearing = gearing
        self.tire_type = tire_type


class SimulationResult:
    def __init__(self, finished, time_sec, risk, notes):
        self.finished = finished
        self.time_sec = time_sec
        self.risk = risk
        self.notes = notes


# =====================
# SIMULATION ENGINE
# =====================

class SimulationEngine:

    def run(self, stage: Stage, car: Car, setup: Setup) -> SimulationResult:
        base_time = stage.length_km * 60 / (0.6 + stage.speed)

        time_modifier = 1.0
        risk = 0.0
        notes = []

        # Tires vs surface
        if setup.tire_type != stage.surface:
            time_modifier += 0.15
            risk += 0.3
            notes.append("Wrong tire choice for this surface")

        # Suspension vs roughness
        if stage.roughness > 0.65 and setup.suspension == "stiff":
            time_modifier += 0.1
            risk += 0.25
            notes.append("Suspension too stiff for rough terrain")

        if stage.speed > 0.7 and setup.suspension == "soft":
            time_modifier += 0.08
            risk += 0.2
            notes.append("Suspension too soft for high-speed sections")

        # Ride height
        if stage.roughness > 0.6 and setup.ride_height == "low":
            risk += 0.3
            notes.append("Ride height too low for this stage")

        # Drivetrain influence
        if stage.surface in ["gravel", "snow"] and car.drivetrain != "AWD":
            time_modifier += 0.1
            risk += 0.2
            notes.append("Non-AWD disadvantage on loose surface")

        # Random factor
        risk += random.uniform(0, 0.1)

        # DNF logic
        if risk > 0.85:
            return SimulationResult(
                finished=False,
                time_sec=None,
                risk=round(risk, 2),
                notes=notes + ["Crash / DNF"]
            )

        final_time = base_time * time_modifier
        return SimulationResult(
            finished=True,
            time_sec=round(final_time, 2),
            risk=round(risk, 2),
            notes=notes
        )


# =====================
# STREAMLIT UI
# =====================

st.title("🏁 Rally Setup Challenge")

# ---------------------
# STAGES
# ---------------------

st.header("1️⃣ Stage Selection")

stages = {
    "Rally Finland": Stage(
        "Rally Finland", 10.5, "gravel", 0.4, 0.9,
        "Very fast gravel stage with big jumps"
    ),
    "Monte Carlo": Stage(
        "Monte Carlo", 8.2, "asphalt", 0.3, 0.6,
        "Twisty mountain roads, changing grip"
    ),
    "Rally Sardinia": Stage(
        "Rally Sardinia", 11.3, "gravel", 0.75, 0.55,
        "Rough gravel, high tire wear"
    ),
    "Rally Wales": Stage(
        "Rally Wales", 9.8, "gravel", 0.7, 0.5,
        "Narrow, wet forest roads"
    ),
    "Rally Sweden": Stage(
        "Rally Sweden", 12.0, "snow", 0.3, 0.75,
        "Snow and ice, very high speeds"
    ),
    "Tour de Corse": Stage(
        "Tour de Corse", 7.6, "asphalt", 0.2, 0.65,
        "Very technical asphalt stage"
    )
}

stage_name = st.selectbox("Stage", stages.keys())
stage = stages[stage_name]

st.subheader("📍 Stage Characteristics")
st.write(f"**Surface:** {stage.surface}")
st.write(f"**Length:** {stage.length_km} km")
st.write(f"**Roughness:** {stage.roughness}")
st.write(f"**Average Speed:** {stage.speed}")
st.write(f"**Description:** {stage.description}")

# ---------------------
# CARS
# ---------------------

st.header("2️⃣ Car Selection")

cars = {
    "Subaru Impreza GC8": Car("Subaru Impreza GC8", 280, 1250, "AWD", 0.9),
    "Mitsubishi Lancer Evo IV": Car("Mitsubishi Lancer Evo IV", 280, 1260, "AWD", 0.88),
    "Ford Focus RS": Car("Ford Focus RS", 300, 1350, "AWD", 0.85),
    "Ford Fiesta": Car("Ford Fiesta", 200, 1180, "FWD", 0.9),
    "Honda Civic EG6": Car("Honda Civic EG6", 170, 1050, "FWD", 0.92),
    "Honda Civic EK9": Car("Honda Civic EK9", 185, 1070, "FWD", 0.9),
    "Toyota Celica GT-Four": Car("Toyota Celica GT-Four", 300, 1350, "AWD", 0.87),
    "Toyota Yaris GR": Car("Toyota Yaris GR", 261, 1280, "AWD", 0.9),
    "Toyota Corolla GR": Car("Toyota Corolla GR", 300, 1470, "AWD", 0.88),
    "Citroen C3": Car("Citroen C3", 280, 1230, "AWD", 0.9),
    "Hyundai i20": Car("Hyundai i20", 280, 1210, "AWD", 0.9),
    "BMW E30": Car("BMW E30", 220, 1200, "RWD", 0.85),
    "BMW E36": Car("BMW E36", 240, 1300, "RWD", 0.84),
    "BMW E46": Car("BMW E46", 260, 1400, "RWD", 0.83),
    "Mercedes-Benz 190E EVO II": Car("Mercedes-Benz 190E EVO II", 235, 1340, "RWD", 0.82),
}

car_name = st.selectbox("Car", cars.keys())
car = cars[car_name]

st.subheader("🚗 Car Characteristics")
st.write(f"**Power:** {car.power} HP")
st.write(f"**Weight:** {car.weight} kg")
st.write(f"**Drivetrain:** {car.drivetrain}")
st.write(f"**Reliability:** {car.reliability}")

# ---------------------
# SETUP
# ---------------------

st.header("3️⃣ Car Setup")

setup = Setup(
    suspension=st.selectbox("Suspension", ["soft", "medium", "stiff"]),
    ride_height=st.selectbox("Ride Height", ["low", "medium", "high"]),
    gearing=st.selectbox("Gearing", ["short", "medium", "long"]),
    tire_type=st.selectbox("Tires", ["gravel", "asphalt", "snow"]),
)



if st.button("▶️ Run Stage"):
    engine = SimulationEngine()
    result = engine.run(stage, car, setup)

    st.subheader("📊 Result")

    if result.finished:
        st.success(f"Stage completed in {result.time_sec} seconds")
    else:
        st.error("❌ DNF – Stage not finished")

    st.write(f"Risk level: {result.risk}")

    if result.notes:
        st.write("🔎 Analysis")
        for note in result.notes:
            st.write(f"- {note}")
