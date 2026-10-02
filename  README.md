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