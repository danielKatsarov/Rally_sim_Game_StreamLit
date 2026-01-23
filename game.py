import streamlit as st
import random


class Stage:
    def __init__(self, name, length_km, roughness, speed, description):
        self.name = name
        self.length_km = length_km
        self.roughness = roughness
        self.speed = speed
        self.description = description
        self.surface = "Generic"

    def surface_penalty(self, car):
        return 0.0


class GravelStage(Stage):
    def __init__(self, name, length_km, roughness, speed, description):
        super().__init__(name, length_km, roughness, speed, description)
        self.surface = "gravel"

    def surface_penalty(self, car):
        return car.control_risk(self.surface)


class AsphaltStage(Stage):
    def __init__(self, name, length_km, roughness, speed, description):
        super().__init__(name, length_km, roughness, speed, description)
        self.surface = "asphalt"

    def surface_penalty(self, car):
        return car.control_risk(self.surface)


class SnowStage(Stage):
    def __init__(self, name, length_km, roughness, speed, description):
        super().__init__(name, length_km, roughness, speed, description)
        self.surface = "snow"

    def surface_penalty(self, car):
        return car.control_risk(self.surface)


class Car:
    def __init__(self, name, power, weight, reliability):
        self.name = name
        self.power = power
        self.weight = weight
        self.reliability = reliability
        self.drivetrain = "Generic"

    def control_risk(self, stage_type):
        return 0.0


class FWDCar(Car):
    def __init__(self, name, power, weight, reliability):
        super().__init__(name, power, weight, reliability)
        self.drivetrain = "FWD"

    def control_risk(self, stage_type):
        if stage_type in ["gravel", "snow"]:
            return 0.1
        return 0.0


class RWDCar(Car):
    def __init__(self, name, power, weight, reliability):
        super().__init__(name, power, weight, reliability)
        self.drivetrain = "RWD"

    def control_risk(self, stage_type):
        if stage_type in ["gravel", "snow"]:
            return 0.15
        return 0.0


class AWDCar(Car):
    def __init__(self, name, power, weight, reliability):
        super().__init__(name, power, weight, reliability)
        self.drivetrain = "AWD"

    def control_risk(self, stage_type):
        return 0.0  


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


def format_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    secs = int(remaining_seconds)
    hundredths = int((remaining_seconds - secs) * 100)
    return f"{minutes:02d}:{secs:02d}:{hundredths:02d}"


class SimulationEngine:

    def calculate_time(self, stage: Stage, car: Car, setup: Setup, add_random: bool = True) -> SimulationResult:
        base_time = stage.length_km * 60 / (0.6 + stage.speed)
        penalty = 0.0
        setup_risk = 0.0
        notes = []

     
        power_to_weight = car.power / car.weight
        baseline_ptw = 0.22
        ptw_diff = power_to_weight - baseline_ptw
        ptw_bonus = -ptw_diff * stage.speed * 0.6
        penalty += ptw_bonus
        if ptw_bonus < -0.03:
            notes.append("Power-to-weight advantage")
        elif ptw_bonus > 0.03:
            notes.append("Car lacks power for this stage")

     
        if stage.roughness > 0.6:
            if setup.suspension == "stiff":
                penalty += 0.15
                setup_risk += 0.2
                notes.append("Suspension too stiff for rough terrain")
            elif setup.suspension == "soft":
                if stage.speed > 0.7:
                    penalty += 0.1
                    setup_risk += 0.2
                    notes.append("Suspension too soft for high-speed rough stage")
                else:
                    penalty += 0.0
                    setup_risk += 0.0


        if stage.roughness > 0.6:
            if setup.ride_height == "low":
                penalty += 0.2
                setup_risk += 0.25
                notes.append("Ride height too low")
            elif setup.ride_height == "medium":
                penalty += 0.05
                setup_risk += 0.02

        if setup.tire_type != stage.surface:
            penalty += 0.15
            setup_risk += 0.2
            notes.append("Wrong tire choice")

        if stage.speed > 0.7 and setup.gearing == "short":
            penalty += 0.08
            notes.append("Short gearing slows down on high-speed stage")
        elif stage.speed < 0.5 and setup.gearing == "long":
            penalty += 0.08
            notes.append("Long gearing hurts acceleration on tight/slow stage")

        if add_random:
            penalty += random.uniform(0, 0.05)

        
        risk = (
            (1 - car.reliability) * 0.25 +
            stage.surface_penalty(car) +
            setup_risk
        )
        risk = min(risk, 1.0)
        
        if power_to_weight > 0.30:
            risk += 0.1
            notes.append("Car is very powerful and hard to control")
        if stage.roughness > 0.6 and power_to_weight > 0.25:
            risk += 0.05
            notes.append("High power on rough terrain increases risk")

        if risk > 0.85:
            return SimulationResult(False, None, round(risk,2), notes + ["Crash / DNF due to reliability or setup"])

        final_time = base_time * (1 + penalty)
        return SimulationResult(True, round(final_time,2), round(risk,2), notes)

    def run(self, stage: Stage, car: Car, setup: Setup) -> SimulationResult:
        return self.calculate_time(stage, car, setup, add_random=True)

    def predict_optimal_time(self, stage: Stage) -> float:
        optimal_setup = Setup("medium", "medium", "medium", stage.surface)
        optimal_car = AWDCar("Optimal AWD", 300, 1300, 0.95)
        result = self.calculate_time(stage, optimal_car, optimal_setup, add_random=False)
        return result.time_sec if result.finished else None


st.title("🏁 Rally Setup Simulation")


st.header("1️⃣ Stage Selection")
stages = {
    "Rally Finland": GravelStage("Rally Finland", 10.5, 0.4, 0.9, "Very fast gravel stage with big jumps"),
    "Monte Carlo": AsphaltStage("Monte Carlo", 8.2, 0.3, 0.6, "Twisty mountain roads with variable grip"),
    "Rally Sardinia": GravelStage("Rally Sardinia", 11.3, 0.75, 0.55, "Rough gravel, high tire wear"),
    "Rally Wales": GravelStage("Rally Wales", 9.8, 0.7, 0.5, "Narrow, wet forest roads"),
    "Rally Sweden": SnowStage("Rally Sweden", 12.0, 0.3, 0.75, "Snow and ice, very high speeds"),
    "Tour de Corse": AsphaltStage("Tour de Corse", 7.6, 0.2, 0.65, "Very technical asphalt stage with tight corners"),
    "Rally Mexico": GravelStage("Rally Mexico", 9.5, 0.55, 0.7, "High altitude, fast gravel roads"),
    "Rally Argentina": GravelStage("Rally Argentina", 10.8, 0.65, 0.6, "Mixed gravel with water crossings")
}
stage_name = st.selectbox("Stage", stages.keys())
stage = stages[stage_name]

st.subheader("📍 Stage Characteristics")
st.write(f"**Surface:** {stage.surface}")
st.write(f"**Length:** {stage.length_km} km")
st.write(f"**Roughness:** {stage.roughness}")
st.write(f"**Average Speed:** {stage.speed}")
st.write(f"**Description:** {stage.description}")


st.header("2️⃣ Car Selection")
cars = {
    "Subaru Impreza GC8": AWDCar("Subaru Impreza GC8", 280, 1250, 0.9),
    "Mitsubishi Lancer Evo IV": AWDCar("Mitsubishi Lancer Evo IV", 280, 1260, 0.88),
    "Ford Focus RS": AWDCar("Ford Focus RS", 300, 1350, 0.85),
    "Ford Fiesta": FWDCar("Ford Fiesta", 200, 1180, 0.9),
    "Honda Civic EG6": FWDCar("Honda Civic EG6", 170, 1050, 0.92),
    "Honda Civic EK9": FWDCar("Honda Civic EK9", 185, 1070, 0.9),
    "Toyota Celica GT-Four": AWDCar("Toyota Celica GT-Four", 300, 1350, 0.87),
    "Toyota Yaris GR": AWDCar("Toyota Yaris GR", 261, 1280, 0.9),
    "Toyota Corolla GR": AWDCar("Toyota Corolla GR", 300, 1470, 0.88),
    "Citroen C3": AWDCar("Citroen C3", 280, 1230, 0.9),
    "Hyundai i20": AWDCar("Hyundai i20", 280, 1210, 0.9),
    "BMW E30": RWDCar("BMW E30", 220, 1200, 0.85),
    "BMW E36": RWDCar("BMW E36", 240, 1300, 0.84),
    "BMW E46": RWDCar("BMW E46", 260, 1400, 0.83),
    "Mercedes-Benz 190E EVO II": RWDCar("Mercedes-Benz 190E EVO II", 235, 1340, 0.82),
    "Audi Quattro S1": AWDCar("Audi Quattro S1", 450, 1350, 0.9),
    "Lancia Delta Integrale": AWDCar("Lancia Delta Integrale", 300, 1280, 0.88),
    "Lancia 037": RWDCar("Lancia 037", 280, 1250, 0.85)
}
car_name = st.selectbox("Car", cars.keys())
car = cars[car_name]

st.subheader("🚗 Vehicle Characteristics")
st.write(f"**Power:** {car.power} HP")
st.write(f"**Weight:** {car.weight} kg")
st.write(f"**Drivetrain:** {car.drivetrain}")
st.write(f"**Reliability:** {car.reliability}")


st.header("3️⃣ Car Setup")
setup = Setup(
    suspension=st.selectbox("Suspension", ["soft", "medium", "stiff"]),
    ride_height=st.selectbox("Ride Height", ["low", "medium", "high"]),
    gearing=st.selectbox("Gearing", ["short", "medium", "long"]),
    tire_type=st.selectbox("Tires", ["gravel", "asphalt", "snow"]),
)

engine = SimulationEngine()
predicted_time_sec = engine.predict_optimal_time(stage)
if predicted_time_sec:
    st.info(f"Predicted optimal time: {format_time(predicted_time_sec)}")

if st.button("▶️ Run Stage"):
    result = engine.run(stage, car, setup)
    st.subheader("📊 Result")
    if result.finished:
        st.success(f"Stage completed in {format_time(result.time_sec)}")
    else:
        st.error("❌ DNF – Stage not finished")
    st.write(f"Risk level: {result.risk}")
    if result.notes:
        st.write("🔎 Analysis")
        for note in result.notes:
            st.write(f"- {note}")



