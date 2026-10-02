# Parking Management System
A desktop parking lot manager built with Python and Tkinter.

## Dependencies
You just need Python and code editor. The code is compatible with Python 3.8 or newer (Tkinter is included with Python). Visit the link https://www.python.org/downloads/ to install the correct version for your operating system (Windows, Mac, or Linux).

## Description
This repository gives an overview of designing an Automated Parking Ticketing based Parking Management System using Python. The Parking Management System can create n number of parking slots in a parking lot. It will issue a parking ticket on entrance terminal and receive back the parking ticket on the exit terminal. The parking ticket will contain vehicle registration number of car, age of the driver driving the car and parking slot allocated to the car and which type of vehicle is driver is driving . The parking slot allocated to a car will always be the nearest to the entrance terminal. On returning the parking ticket the parking slot will be vacated and deallocated from the car. The Parking Management System can calculate the fee based on how much time vehicle is parked based on real world time and date . The Parking Management System will load previous data and saves data of the vehicle and report of the fees collected by Parking Management System  

## Features
- Create a parking lot with up to 40 slots
- Park cars and bikes/trucks with different hourly rates
- Leave and pay, with a receipt (partial hours rounded up)
- Search by registration number, driver age, or partial number
- Load cars from a CSV file
- Save and load data between runs
- Payment history and CSV report export

  ## 📸 Application Screenshot
<img width="1102" height="946" alt="Screenshot From 2026-10-02 22-52-31" src="https://github.com/user-attachments/assets/6d6dde47-bbbf-4424-abda-73097d3be28a" />
<img width="1102" height="946" alt="Screenshot From 2026-10-02 22-52-11" src="https://github.com/user-attachments/assets/5cd51fbd-b322-4727-bb63-179eab30b0f1" />
<img width="1102" height="946" alt="Screenshot From 2026-10-02 22-51-59" src="https://github.com/user-attachments/assets/278b442e-ffbd-4ac1-a04e-994bfd1bec4d" />
<img width="1102" height="946" alt="Screenshot From 2026-10-02 22-51-45" src="https://github.com/user-attachments/assets/d2c49e45-51be-4716-a9be-dfc39be5ce17" />
<img width="1102" height="946" alt="Screenshot From 2026-10-02 22-51-39" src="https://github.com/user-attachments/assets/c02247e4-ce27-439b-9b2e-4f09bcc4b315" />
<img width="1102" height="946" alt="Screenshot From 2026-10-02 22-51-20" src="https://github.com/user-attachments/assets/93387b2e-8188-45f7-a4e4-5c2455dfe99d" />
<img width="1102" height="946" alt="Screenshot From 2026-10-02 22-51-08" src="https://github.com/user-attachments/assets/c35d5e9d-fc5e-4f6e-889f-33865a05f741" />
<img width="1102" height="946" alt="Screenshot From 2026-10-02 22-50-50" src="https://github.com/user-attachments/assets/bb26a9c9-b06f-4b19-bc76-d0847b0deb1d" />
<img width="1102" height="946" alt="Screenshot From 2026-10-02 22-50-05" src="https://github.com/user-attachments/assets/1059888d-efa2-49d9-8cb2-0490df14e0cd" />
<img width="1102" height="946" alt="Screenshot From 2026-10-02 22-49-56" src="https://github.com/user-attachments/assets/f22ebce7-8abd-457c-8467-83354156e6af" />

## How to run
```bash
git clone https://github.com/shashidharreddymaneti-web/Parking-Management-System.git
cd Parking-Management-System
python3 src/gui.py
```

## Sample data
`cars.csv` has sample cars. Create a lot, then click **Load cars.csv**.

## Project structure
- `src/gui.py`: the Tkinter interface
- `src/parking_management.py`: parking logic
- `src/Models/`: Car, Driver, Vehicle and ParkingTicket classes
