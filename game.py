import streamlit as st
import random

# =====================
# DATA MODELS
# =====================

class Stage:
    def __init__(self, name, length_km, surface, roughness, speed, description):
        self.name = name
        self.length_km = length_km
        self.surface = surface
        self.roughness = roughness
        self.speed = speed
        self.description = description


class Car:
    def __init__(self, name, power, weight, drivetrain, reliability):
        self.name = name
        self.power = power
        self.weight = weight
        self.drivetrain = drivetrain
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
# UTILS
# =====================

def format_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    seconds_left = seconds % 60
    secs = int(seconds_left)
    hundredths = int((seconds_left - secs) * 100)
    return f"{minutes:02d}:{secs:02d}:{hundredths:02d}"


# =====================
# SIMULATION ENGINE
# =====================

class SimulationEngine:

    def calculate_time(self, stage: Stage, car: Car, setup: Setup, add_random=True) -> SimulationResult:
        base_time = stage.length_km * 60 / (0.6 + stage.speed)

        penalty = 0.0
        risk = 0.0
        notes = []

        # --- Power / Weight (TIME)
        ptw = car.power / car.weight
        baseline = 0.22
        ptw_effect = -(ptw - baseline) * stage.speed * 0.6
        penalty += ptw_effect

        if ptw_effect < -0.03:
            notes.append("Strong power-to-weight advantage")
        elif ptw_effect > 0.03:
            notes.append("Low power for this stage")

        # --- Suspension
        if stage.roughness > 0.6:
            if setup.suspension == "stiff":
                penalty += 0.15
                risk += 0.05
                notes.append("Suspension too stiff for rough terrain")
            elif setup.suspension == "soft":
                penalty += 0.05
        elif stage.speed > 0.7 and setup.suspension == "soft":
            penalty += 0.1
            notes.append("Soft suspension unstable at high speed")

        # --- Ride height
        if stage.roughness > 0.6 and setup.ride_height == "low":
            penalty += 0.2
            risk += 0.05
            notes.append("Ride height too low")

        # --- Tires
        if setup.tire_type != stage.surface:
            penalty += 0.15
            risk += 0.05
            notes.append("Incorrect tire choice")

        # --- Drivetrain
        if stage.surface in ["gravel", "snow"] and car.drivetrain != "AWD":
            penalty += 0.1
            risk += 0.05
            notes.append("Non-AWD disadvantage")

        # --- Gearing
        if stage.speed > 0.7 and setup.gearing == "short":
            penalty += 0.08
            notes.append("Short gearing limits top speed")
        elif stage.speed < 0.5 and setup.gearing == "long":
            penalty += 0.08
            notes.append("Long gearing hurts acceleration")

        # --- High power = RISK
        if ptw > 0.30:
            risk += 0.1
            notes.append("Very powerful car – harder to control")
            if stage.roughness > 0.6:
                risk += 0.05

        # --- Reliability (RISK only)
        risk += (1 - car.reliability) * 0.25

        # --- Random factor
        if add_random:
            penalty += random.uniform(0, 0.05)
            risk += random.uniform(0, 0.05)

        risk = min(round(risk, 2), 1.0)

        if risk > 0.85:
            return SimulationResult(False, None, risk, notes + ["Crash / mechanical failure"])

        final_time = base_time * (1 + penalty)

        return SimulationResult(True, round(final_time, 2), risk, notes)

    def run(self, stage, car, setup):
        return self.calculate_time(stage, car, setup, add_random=True)

    def predict_optimal_time(self, stage):
        optimal_setup = Setup("medium", "medium", "medium", stage.surface)
        optimal_car = Car("Ideal AWD", 300, 1300, "AWD", 0.95)
        result = self.calculate_time(stage, optimal_car, optimal_setup, add_random=False)
        return result.time_sec


# =====================
# STREAMLIT UI
# =====================

st.title("🏁 Rally Setup Simulator")

# --- Stages
stages = {
    "Rally Finland": Stage("Finland", 10.5, "gravel", 0.4, 0.9, "Very fast gravel"),
    "Monte Carlo": Stage("Monte Carlo", 8.2, "asphalt", 0.3, 0.6, "Mixed asphalt"),
    "Rally Sardinia": Stage("Sardinia", 11.3, "gravel", 0.75, 0.55, "Very rough gravel"),
    "Rally Sweden": Stage("Sweden", 12.0, "snow", 0.3, 0.75, "Fast snow stage"),
    "Tour de Corse": Stage("Corsica", 7.6, "asphalt", 0.2, 0.65, "Tight asphalt")
}

stage_name = st.selectbox("Stage", stages.keys())
stage = stages[stage_name]

st.write(stage.description)

# --- Cars
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
    "Audi Quattro S1": Car("Audi Quattro S1", 450, 1350, "AWD", 0.9),
    "Lancia Delta Integrale": Car("Lancia Delta Integrale", 300, 1280, "AWD", 0.88),
    "Lancia 037": Car("Lancia 037", 280, 1250, "RWD", 0.85),
}

car_name = st.selectbox("Car", cars.keys())
car = cars[car_name]

# --- Setup
setup = Setup(
    st.selectbox("Suspension", ["soft", "medium", "stiff"]),
    st.selectbox("Ride Height", ["low", "medium", "high"]),
    st.selectbox("Gearing", ["short", "medium", "long"]),
    st.selectbox("Tires", ["gravel", "asphalt", "snow"]),
)

engine = SimulationEngine()
ideal_time = engine.predict_optimal_time(stage)
st.info(f"Ideal reference time: {format_time(ideal_time)}")

if st.button("▶ Run Stage"):
    result = engine.run(stage, car, setup)

    if result.finished:
        st.success(f"Finished in {format_time(result.time_sec)}")
    else:
        st.error("❌ DNF")

    st.write(f"Risk: {result.risk}")

    for note in result.notes:
        st.write(f"- {note}")


