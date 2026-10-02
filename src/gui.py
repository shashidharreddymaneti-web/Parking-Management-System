import csv
import json
import math
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from parking_management import ParkingManagement

# ---------- colors and settings ----------
BG = "#eef2f7"
HEADER = "#1e3a5f"
FREE = "#2ecc71"
TAKEN = "#e74c3c"
COLS = 4            # slots per row in the grid
CURRENCY = "₹"      # change to "$" or anything you like

lot = None          # becomes a ParkingManagement object after "Create" is clicked
entry_times = {}    # registration number -> datetime when the car was parked
revenue = 0         # total money collected since the lot was created
vehicle_types = {}  # registration number -> "Bike", "Car" or "Truck"
history = []        # one entry for every payment
RATES = {"Bike": 10, "Car": 20, "Truck": 40}   # rate per hour for each type
DATA_FILE = "parking_data.json"

root = tk.Tk()
root.title("Parking Management System")
root.geometry("1100x900")
root.configure(bg=BG)


# ---------- helpers ----------
def show(message, kind="info"):
    log.config(state="normal")
    log.insert(tk.END, message + "\n", kind)
    log.see(tk.END)
    log.config(state="disabled")


def need_lot():
    if lot is None:
        messagebox.showwarning("No parking lot", "Create a parking lot first.")
        return False
    return True


def read_int(entry, name):
    text = entry.get().strip()
    if not text.isdigit():
        messagebox.showerror("Invalid input", f"{name} must be a whole number.")
        return None
    return int(text)


def section(parent, title, color):
    frame = tk.LabelFrame(parent, text=title, bg=BG, fg=color,
                          font=("Helvetica", 11, "bold"), padx=10, pady=6)
    frame.pack(fill="x", pady=5)
    return frame


def labeled_entry(parent, label, on_enter=None, default=None):
    row = tk.Frame(parent, bg=BG)
    row.pack(pady=2)
    tk.Label(row, text=label, width=18, anchor="w", bg=BG).pack(side="left")
    entry = tk.Entry(row, width=18)
    entry.pack(side="left")
    if default is not None:
        entry.insert(0, str(default))
    if on_enter:
        entry.bind("<Return>", lambda event: on_enter())
    return entry


def button(parent, text, color, command):
    return tk.Button(parent, text=text, command=command, bg=color, fg="white",
                     activebackground=color, activeforeground="white",
                     font=("Helvetica", 10, "bold"), relief="flat", padx=10, pady=3)


def calculate_fee(seconds, rate):
    """Partial hours are rounded up. Minimum charge is 1 hour."""
    hours_billed = max(1, math.ceil(seconds / 3600))
    return hours_billed, hours_billed * rate


def format_duration(seconds):
    minutes = int(seconds // 60)
    return f"{minutes // 60}h {minutes % 60}m"


def pick_slot(number):
    leave_entry.delete(0, tk.END)
    leave_entry.insert(0, str(number))


def refresh():
    """Redraw the stats bar and the slot grid from the real parking data."""
    for widget in grid.winfo_children():
        widget.destroy()
    if lot is None:
        stats.config(text="No parking lot yet")
        return
    taken = {t.get_parking_slot(): t for t in lot.occupied_parking_slots.values()}
    used = len(taken)
    stats.config(text=f"Total: {lot.capacity}    Occupied: {used}    "
                      f"Free: {lot.capacity - used}    "
                      f"Revenue: {CURRENCY}{revenue}")
    for i in range(1, lot.capacity + 1):
        ticket = taken.get(i)
        if ticket:
            reg = ticket.get_vehicle_registration_number()
            since = entry_times.get(reg)
            since_text = since.strftime("%H:%M") if since else "--:--"
            vtype = vehicle_types.get(reg, "Car")
            text = (f"Slot {i}\n{reg}\n{vtype}, age {ticket.get_driver_age()}\n"
                    f"Since {since_text}")
            color = TAKEN
        else:
            text = f"Slot {i}\n\nFREE\n"
            color = FREE
        cell = tk.Label(grid, text=text, bg=color, fg="white", width=15, height=5,
                        relief="raised", bd=2, font=("Helvetica", 9, "bold"))
        cell.grid(row=(i - 1) // COLS, column=(i - 1) % COLS, padx=4, pady=4)
        if ticket:
            cell.bind("<Button-1>", lambda event, n=i: pick_slot(n))


# ---------- actions ----------
def create_lot():
    global lot, revenue
    n = read_int(slots_entry, "Number of slots")
    if n is None:
        return
    if n < 1 or n > 40:
        messagebox.showerror("Invalid input", "Number of slots must be between 1 and 40.")
        return
    lot = ParkingManagement()
    entry_times.clear()
    vehicle_types.clear()
    history.clear()
    revenue = 0
    if lot.create_parking_slots(n):
        show(f"Created parking of {n} slots", "success")
    refresh()


def park_car():
    if not need_lot():
        return
    reg = reg_entry.get().strip().upper()
    if not reg:
        messagebox.showerror("Invalid input", "Enter a registration number.")
        return
    age = read_int(age_entry, "Driver age")
    if age is None:
        return
    if lot.get_parking_slot_number_from_vehicle_registration_number(reg) != -1:
        messagebox.showerror("Already parked", f"{reg} is already parked.")
        return
    vtype = type_box.get()
    slot = lot.issue_parking_ticket(reg, age)
    if slot == -1:
        show("Sorry, Parking Lot is full, No Parking Slots Available.", "error")
    else:
        entry_times[reg] = datetime.now()
        vehicle_types[reg] = vtype
        show(f'{vtype} "{reg}" (driver age {age}) parked at slot {slot} '
             f'at {entry_times[reg].strftime("%H:%M")}', "success")
        reg_entry.delete(0, tk.END)
        age_entry.delete(0, tk.END)
    refresh()


def leave_slot():
    global revenue
    if not need_lot():
        return
    slot = read_int(leave_entry, "Slot number")
    if slot is None:
        return

    test_text = test_entry.get().strip()
    if test_text and not test_text.isdigit():
        messagebox.showerror("Invalid input", "Test hours must be a whole number.")
        return

    ticket = lot.return_parking_ticket(slot)
    if not ticket:
        show(f"Slot number {slot} cannot be vacated.", "error")
        refresh()
        return

    reg = ticket.get_vehicle_registration_number()
    vtype = vehicle_types.pop(reg, "Car")
    rate = RATES[vtype]
    now = datetime.now()
    entered = entry_times.pop(reg, now)
    if test_text:
        seconds = int(test_text) * 3600
    else:
        seconds = (now - entered).total_seconds()

    hours_billed, fee = calculate_fee(seconds, rate)
    revenue += fee
    test_entry.delete(0, tk.END)

    history.append({"reg": reg, "type": vtype, "slot": slot,
                    "entered": entered.strftime("%Y-%m-%d %H:%M"),
                    "left": now.strftime("%Y-%m-%d %H:%M"),
                    "hours_billed": hours_billed, "fee": fee})

    show(f'Slot {slot} vacated, {vtype} "{reg}" left. '
         f'Stayed {format_duration(seconds)}, billed {hours_billed}h, '
         f'fee {CURRENCY}{fee}', "success")
    messagebox.showinfo(
        "Parking receipt",
        f"Vehicle:   {reg} ({vtype})\n"
        f"Slot:      {slot}\n"
        f"Entered:   {entered.strftime('%d %b %Y, %H:%M')}\n"
        f"Duration:  {format_duration(seconds)}\n"
        f"Billed:    {hours_billed} hour(s) x {CURRENCY}{rate}\n\n"
        f"TOTAL:     {CURRENCY}{fee}")
    refresh()

def load_csv():
    if not need_lot():
        return
    try:
        with open("cars.csv", newline="") as f:
            for row in csv.DictReader(f):
                reg = row["registration_no"].strip().upper()
                age = int(row["driver_age"])
                vtype = row.get("vehicle_type", "Car").strip().title()
                if vtype not in RATES:
                    vtype = "Car"
                if lot.get_parking_slot_number_from_vehicle_registration_number(reg) != -1:
                    continue
                slot = lot.issue_parking_ticket(reg, age)
                if slot == -1:
                    show("Parking Lot is full.", "error")
                    break
                entry_times[reg] = datetime.now()
                vehicle_types[reg] = vtype
                show(f'{vtype} "{reg}" (age {age}) parked at slot {slot}', "success")
    except FileNotFoundError:
        messagebox.showerror("File not found", "cars.csv must be in the same folder as this program.")
    refresh()

def find_slot_by_car():
    if not need_lot():
        return
    reg = search_entry.get().strip().upper()
    if not reg:
        messagebox.showerror("Invalid input", "Enter a registration number.")
        return
    slot = lot.get_parking_slot_number_from_vehicle_registration_number(reg)
    if slot == -1:
        show("No parked car matches the query", "error")
    else:
        show(f"{reg} is at slot {slot}", "info")


def find_slots_by_age():
    if not need_lot():
        return
    age = read_int(search_entry, "Driver age")
    if age is None:
        return
    slots = lot.get_parking_slots_from_driver_age(age)
    if slots:
        show("Slots for age " + str(age) + ": " + ",".join(str(s) for s in slots), "info")
    else:
        show("No parked car matches the query", "error")


def find_cars_by_age():
    if not need_lot():
        return
    age = read_int(search_entry, "Driver age")
    if age is None:
        return
    cars = lot.get_vehicle_registration_numbers_from_driver_age(age)
    if cars:
        show("Cars for age " + str(age) + ": " + ",".join(cars), "info")
    else:
        show("No parked car matches the query", "error")


def reset_lot():
    global lot, revenue
    if lot is not None and not messagebox.askyesno("Reset", "Remove the parking lot and all cars?"):
        return
    lot = None
    revenue = 0
    entry_times.clear()
    vehicle_types.clear()
    history.clear()
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    refresh()
    show("Parking lot reset.", "info")


def clear_log():
    log.config(state="normal")
    log.delete("1.0", tk.END)
    log.config(state="disabled")


# ---------- layout ----------
def find_by_partial():
    """Feature: search by part of a registration number, e.g. 'TS'."""
    if not need_lot():
        return
    text = search_entry.get().strip().upper()
    if not text:
        messagebox.showerror("Invalid input", "Type part of a registration number.")
        return
    matches = sorted((t.get_parking_slot(), t.get_vehicle_registration_number())
                     for t in lot.occupied_parking_slots.values()
                     if text in t.get_vehicle_registration_number())
    if matches:
        show(f'Cars containing "{text}": ' +
             ", ".join(f"{reg} (slot {slot})" for slot, reg in matches), "info")
    else:
        show("No parked car matches the query", "error")


def save_data(silent=False):
    """Feature: save the lot, parked cars, revenue and history to a file."""
    if lot is None:
        if not silent:
            messagebox.showwarning("Nothing to save", "Create a parking lot first.")
        return
    cars = []
    for t in lot.occupied_parking_slots.values():
        reg = t.get_vehicle_registration_number()
        since = entry_times.get(reg)
        cars.append({"slot": t.get_parking_slot(), "reg": reg,
                     "age": t.get_driver_age(),
                     "type": vehicle_types.get(reg, "Car"),
                     "since": since.isoformat() if since else None})
    data = {"capacity": lot.capacity, "revenue": revenue,
            "cars": cars, "history": history}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    if not silent:
        show(f"Data saved to {DATA_FILE}", "success")


def load_data(silent=False):
    """Feature: bring back everything that was saved."""
    global lot, revenue
    if not os.path.exists(DATA_FILE):
        if not silent:
            messagebox.showinfo("No saved data", "Nothing has been saved yet.")
        return
    with open(DATA_FILE) as f:
        data = json.load(f)

    lot = ParkingManagement()
    lot.create_parking_slots(data["capacity"])
    entry_times.clear()
    vehicle_types.clear()
    history.clear()
    history.extend(data.get("history", []))
    revenue = data.get("revenue", 0)

    # Park cars in slot order. Empty slots in between are filled with
    # temporary cars and freed again, so every car keeps its old slot.
    by_slot = {c["slot"]: c for c in data["cars"]}
    fillers = []
    for i in range(1, max(by_slot, default=0) + 1):
        car = by_slot.get(i)
        if car:
            lot.issue_parking_ticket(car["reg"], car["age"])
            vehicle_types[car["reg"]] = car["type"]
            if car["since"]:
                entry_times[car["reg"]] = datetime.fromisoformat(car["since"])
        else:
            lot.issue_parking_ticket(f"FILLER{i}", 0)
            fillers.append(i)
    for i in fillers:
        lot.return_parking_ticket(i)

    refresh()
    if not silent:
        show("Saved data loaded.", "success")


def show_history():
    """Feature: list every payment made so far."""
    if not history:
        show("No payments yet.", "info")
        return
    show("--- Payment history ---", "info")
    for h in history:
        show(f'{h["left"]}  {h["reg"]} ({h["type"]})  '
             f'{h["hours_billed"]}h  {CURRENCY}{h["fee"]}', "info")
    show(f"Total revenue: {CURRENCY}{revenue}", "success")


def export_report():
    """Feature: write all payments to a CSV file you can open in Excel."""
    if not history:
        messagebox.showinfo("No data", "No payments to export yet.")
        return
    name = "report_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
    with open(name, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["reg", "type", "slot", "entered",
                                               "left", "hours_billed", "fee"])
        writer.writeheader()
        writer.writerows(history)
    show(f"Report saved to {name} (total {CURRENCY}{revenue})", "success")


def on_close():
    save_data(silent=True)      # auto-save when the window is closed
    root.destroy()

header = tk.Label(root, text="🚗  Parking Management System", bg=HEADER, fg="white",
                  font=("Helvetica", 18, "bold"), pady=10)
header.pack(fill="x")

body = tk.Frame(root, bg=BG)
body.pack(fill="both", expand=True, padx=10, pady=5)

left = tk.Frame(body, bg=BG)
left.pack(side="left", fill="y", padx=(0, 10))

right = tk.Frame(body, bg=BG)
right.pack(side="left", fill="both", expand=True)

# --- left: controls ---
f1 = section(left, "1. Create parking lot", "#2980b9")
slots_entry = labeled_entry(f1, "Number of slots:", create_lot)
tk.Label(f1, bg=BG, text="Per hour: " + ", ".join(
    f"{name} {CURRENCY}{rate}" for name, rate in RATES.items())).pack()
row1 = tk.Frame(f1, bg=BG)
row1.pack(pady=3)
button(row1, "Create", "#3498db", create_lot).pack(side="left", padx=3)
button(row1, "Reset", "#7f8c8d", reset_lot).pack(side="left", padx=3)

f2 = section(left, "2. Park a car", "#27ae60")
reg_entry = labeled_entry(f2, "Registration no.:")
age_entry = labeled_entry(f2, "Driver age:", park_car)
row_type = tk.Frame(f2, bg=BG)
row_type.pack(pady=2)
tk.Label(row_type, text="Vehicle type:", width=18, anchor="w", bg=BG).pack(side="left")
type_box = ttk.Combobox(row_type, values=list(RATES), state="readonly", width=15)
type_box.set("Car")
type_box.pack(side="left")
button(f2, "Park", "#2ecc71", park_car).pack(pady=3)
button(f2, "Load cars.csv", "#16a085", load_csv).pack(pady=3)

f3 = section(left, "3. Leave a slot (or click a red slot)", "#d35400")
leave_entry = labeled_entry(f3, "Slot number:", leave_slot)
test_entry = labeled_entry(f3, "Test hours (optional):", leave_slot)
button(f3, "Leave and pay", "#e67e22", leave_slot).pack(pady=3)

f4 = section(left, "4. Search", "#8e44ad")
search_entry = labeled_entry(f4, "Reg. no. or age:")
row4 = tk.Frame(f4, bg=BG)
row4.pack(pady=3)
button(row4, "Slot of car", "#9b59b6", find_slot_by_car).pack(side="left", padx=3)
button(row4, "Slots by age", "#8e44ad", find_slots_by_age).pack(side="left", padx=3)
button(row4, "Cars by age", "#6c3483", find_cars_by_age).pack(side="left", padx=3)
row4b = tk.Frame(f4, bg=BG)
row4b.pack(pady=3)
button(row4b, "Partial reg. no. (e.g. TS)", "#5b2c6f", find_by_partial).pack(padx=3)

f5 = section(left, "5. Data and reports", "#16a085")
row5a = tk.Frame(f5, bg=BG)
row5a.pack(pady=3)
button(row5a, "Save data", "#1abc9c", save_data).pack(side="left", padx=3)
button(row5a, "Load data", "#16a085", load_data).pack(side="left", padx=3)
row5b = tk.Frame(f5, bg=BG)
row5b.pack(pady=3)
button(row5b, "Show history", "#2980b9", show_history).pack(side="left", padx=3)
button(row5b, "Export report", "#1f618d", export_report).pack(side="left", padx=3)

# --- right: stats, grid, log ---
stats = tk.Label(right, text="No parking lot yet", bg="#d6eaf8", fg=HEADER,
                 font=("Helvetica", 12, "bold"), pady=6)
stats.pack(fill="x")

grid_box = tk.LabelFrame(right, text="Parking slots", bg=BG, fg=HEADER,
                         font=("Helvetica", 11, "bold"), padx=5, pady=5)
grid_box.pack(fill="both", expand=True, pady=5)
grid = tk.Frame(grid_box, bg=BG)
grid.pack(anchor="nw")

log_head = tk.Frame(right, bg=BG)
log_head.pack(fill="x")
tk.Label(log_head, text="Activity log", bg=BG, fg=HEADER,
         font=("Helvetica", 11, "bold")).pack(side="left")
button(log_head, "Clear log", "#7f8c8d", clear_log).pack(side="right")

log = tk.Text(right, height=9, state="disabled", bg="white")
log.pack(fill="x", pady=(2, 0))
log.tag_config("success", foreground="#1e8449")
log.tag_config("error", foreground="#c0392b")
log.tag_config("info", foreground="#2471a3")

root.protocol("WM_DELETE_WINDOW", on_close)   # run on_close when window closes
load_data(silent=True)                        # restore saved data at startup
refresh()
root.mainloop()