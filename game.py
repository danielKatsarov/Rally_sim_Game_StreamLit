import streamlit as st
import random

# =====================
# MODELS
# =====================

class Stage:
    def __init__(self, name, length_km, surface, roughness, speed):
        self.name = name
        self.length_km = length_km
        self.surface = surface            # gravel / asphalt / snow
        self.roughness = roughness        # 0–1
        self.speed = speed                # 0–1


class Car:
    def __init__(self, name, power, weight, drivetrain, reliability):
        self.name = name
        self.power = power
        self.weight = weight
        self.drivetrain = drivetrain      # AWD / FWD / RWD
        self.reliability = reliability    # 0–1


class Setup:
    def __init__(self, suspension, ride_height, gearing, tire_type):
        self.suspension = suspension      # soft / medium / stiff
        self.ride_height = ride_height    # low / medium / high
        self.gearing = gearing            # short / medium / long
        self.tire_type = tire_type        # gravel / asphalt / snow


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
        if stage.roughness > 0.6 and setup.suspension == "stiff":
            time_modifier += 0.1
            risk += 0.25
            notes.append("Suspension too stiff for a rough stage")

        if stage.speed > 0.7 and setup.suspension == "soft":
            time_modifier += 0.08
            risk += 0.2
            notes.append("Suspension too soft for a high-speed stage")

        # Ride height
        if stage.roughness > 0.6 and setup.ride_height == "low":
            risk += 0.3
            notes.append("Ride height too low for rough terrain")

        # Random factor
        risk += random.uniform(0, 0.1)

        # DNF check
        if risk > 0.8:
            return SimulationResult(
                finished=False,
                time_sec=None,
                risk=risk,
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

# Stage selection
st.header("1️⃣ Stage Selection")

stages = {
    "Rally Finland": Stage("Rally Finland", 10.5, "gravel", 0.4, 0.9),
    "Monte Carlo": Stage("Monte Carlo", 8.2, "asphalt", 0.3, 0.6),
    "Wales Rally": Stage("Wales Rally", 9.8, "gravel", 0.7, 0.5),
}

stage_name = st.selectbox("Stage", stages.keys())
stage = stages[stage_name]

# Car selection
st.header("2️⃣ Car Selection")

cars = {
    "Rally1 AWD": Car("Rally1 AWD", 380, 1250, "AWD", 0.9),
    "Rally2 AWD": Car("Rally2 AWD", 290, 1350, "AWD", 0.85),
}

car_name = st.selectbox("Car", cars.keys())
car = cars[car_name]

# Setup
st.header("3️⃣ Car Setup")

setup = Setup(
    suspension=st.selectbox("Suspension", ["soft", "medium", "stiff"]),
    ride_height=st.selectbox("Ride Height", ["low", "medium", "high"]),
    gearing=st.selectbox("Gearing", ["short", "medium", "long"]),
    tire_type=st.selectbox("Tires", ["gravel", "asphalt", "snow"]),
)

# Run simulation
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
        st.write("🔎 Analysis:")
        for note in result.notes:
            st.write(f"- {note}")
