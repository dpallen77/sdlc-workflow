# Requirements

## Assumptions
- The human chose a desktop window as the UX. It has one number entry box, a "from" drop-down, a "to" drop-down, a "Convert" button, and one area that shows the result or an error message. The business statement says what the user does but not what starts the conversion, so the "Convert" button is an assumed minor UI detail.
- The application is written in Python 3 using only the standard library (for example, tkinter for the window), as the project constraints require.
- The supported units are exactly these 8, and both drop-downs list them in this order: millimeters, centimeters, meters, kilometers, inches, feet, yards, miles.
- Each drop-down always has a unit selected, and the first unit is preselected when the window opens. So there is never a "no unit selected" state.
- The built-in conversion factors use the exact international definitions: 1 inch = 25.4 mm, 1 foot = 12 inches = 0.3048 m, 1 yard = 3 feet = 0.9144 m, 1 mile = 5280 feet = 1609.344 m, 1 cm = 10 mm, 1 m = 100 cm, 1 km = 1000 m.
- Decimal input such as "2.5" counts as a valid number. Surrounding spaces are ignored.
- The result shows the number only, with exactly 2 digits after the decimal point, including trailing zeros (for example "5.00"). It has no thousands separators and no unit label.
- Rounding to 2 decimal places rounds half up. Because all valid values are positive, this is the same as rounding half away from zero. The acceptance criteria avoid exact tie values.
- A result smaller than 0.005 is shown as "0.00".
- Converting a unit to itself is allowed, and the result is the entered value rounded to 2 decimal places.
- Invalid input is reported in the result area with a fixed message, and no converted value is shown. For zero or negative numbers the message is "Please enter a number greater than zero." For empty or non-numeric input the message is "Please enter a valid number."
- The conversion logic can be called separately from the window (a function that takes a value, a from unit, and a to unit), so the acceptance criteria can be tested without a live GUI.

## Requirements

### REQ-001: Desktop window
Statement: The system shall open a desktop window that has a number entry box, a "from" unit drop-down, a "to" unit drop-down, a "Convert" button, and a result display area.
Acceptance criteria:
- AC-1: Given the application is started, when the window is built, then it has exactly one number entry box, one "from" drop-down, one "to" drop-down, one "Convert" button, and one result display area.
- AC-2: Given the window has just opened, when no conversion has been run yet, then the result display area shows no converted value and no error message.

### REQ-002: "From" unit options
Statement: The system shall offer exactly the 8 supported distance units in the "from" drop-down.
Acceptance criteria:
- AC-1: Given the window is open, when the "from" drop-down options are read, then they are exactly, in order: millimeters, centimeters, meters, kilometers, inches, feet, yards, miles.

### REQ-003: "To" unit options
Statement: The system shall offer the same 8 supported distance units in the "to" drop-down as in the "from" drop-down.
Acceptance criteria:
- AC-1: Given the window is open, when the "to" drop-down options are read, then they are exactly, in order: millimeters, centimeters, meters, kilometers, inches, feet, yards, miles.

### REQ-004: Convert between any two different units
Statement: The system shall convert a valid entered value from any supported unit to any other supported unit using the built-in conversion factors.
Acceptance criteria:
- AC-1: Given 1 inches to millimeters, when converted, then the result is 25.40.
- AC-2: Given 1 miles to kilometers, when converted, then the result is 1.61.
- AC-3: Given 1 meters to feet, when converted, then the result is 3.28.
- AC-4: Given 1 yards to meters, when converted, then the result is 0.91.
- AC-5: Given 1 kilometers to miles, when converted, then the result is 0.62.
- AC-6: Given 1 inches to centimeters, when converted, then the result is 2.54.
- AC-7: Given 1 kilometers to meters (metric to metric), when converted, then the result is 1000.00.
- AC-8: Given 10 centimeters to millimeters (metric to metric), when converted, then the result is 100.00.
- AC-9: Given 1 feet to inches (US to US), when converted, then the result is 12.00.
- AC-10: Given 1 miles to yards (US to US), when converted, then the result is 1760.00.
- AC-11: Given 1 miles to feet (US to US), when converted, then the result is 5280.00.
- AC-12: Given 1 kilometers to feet, when converted, then the result is 3280.84.
- AC-13: Given 2.5 feet to inches (decimal input), when converted, then the result is 30.00.
- AC-14: Given each of the 56 ordered pairs of different units and an input of 1, when converted, then each result equals (1 x meters-per-unit of the from unit / meters-per-unit of the to unit) rounded half up to 2 decimal places, using the factors listed in the Assumptions.

### REQ-005: Convert a unit to itself
Statement: The system shall return the entered value, rounded to 2 decimal places, when the "from" and "to" units are the same.
Acceptance criteria:
- AC-1: Given 7 meters to meters, when converted, then the result is 7.00.
- AC-2: Given 3.14159 inches to inches, when converted, then the result is 3.14.
- AC-3: Given each of the 8 units converted to itself with an input of 1, when converted, then each result is 1.00.

### REQ-006: Display the result to 2 decimal places
Statement: The system shall show the converted value in the result display area with exactly 2 digits after the decimal point.
Acceptance criteria:
- AC-1: Given 1 meters to inches entered in the window, when "Convert" is pressed, then the result display area shows "39.37".
- AC-2: Given 5 meters to meters entered in the window, when "Convert" is pressed, then the result display area shows "5.00".
- AC-3: Given 100 feet to meters entered in the window, when "Convert" is pressed, then the result display area shows "30.48".
- AC-4: Given 1 millimeters to miles entered in the window, when "Convert" is pressed, then the result display area shows "0.00".

### REQ-007: Reject zero
Statement: The system shall reject an entered value of zero and show no converted value.
Acceptance criteria:
- AC-1: Given "0" is entered with any from and to units, when "Convert" is pressed, then the result display area shows "Please enter a number greater than zero." and no number.
- AC-2: Given "0.0" is entered, when "Convert" is pressed, then the result display area shows "Please enter a number greater than zero." and no number.
- AC-3: Given the conversion function is called with value 0, when it runs, then it signals an error and returns no converted value.

### REQ-008: Reject negative numbers
Statement: The system shall reject a negative entered value and show no converted value.
Acceptance criteria:
- AC-1: Given "-5" is entered with any from and to units, when "Convert" is pressed, then the result display area shows "Please enter a number greater than zero." and no number.
- AC-2: Given "-0.01" is entered, when "Convert" is pressed, then the result display area shows "Please enter a number greater than zero." and no number.
- AC-3: Given the conversion function is called with value -1, when it runs, then it signals an error and returns no converted value.

### REQ-009: Reject empty or non-numeric input
Statement: The system shall reject entry box contents that are empty or not a number and show no converted value.
Acceptance criteria:
- AC-1: Given the entry box is empty, when "Convert" is pressed, then the result display area shows "Please enter a valid number." and no number.
- AC-2: Given "abc" is entered, when "Convert" is pressed, then the result display area shows "Please enter a valid number." and no number.
- AC-3: Given "12ft" is entered, when "Convert" is pressed, then the result display area shows "Please enter a valid number." and no number.
- AC-4: Given an invalid entry has produced an error message, when the entry is changed to "1" with inches to millimeters and "Convert" is pressed, then the result display area shows "25.40" and the error message is gone.

### REQ-010: Built-in conversion factors only
Statement: The system shall do every conversion with conversion factors built into the application, without any network access.
Acceptance criteria:
- AC-1: Given the machine has no network connection, when 1 inches to millimeters is converted, then the result is 25.40.
- AC-2: Given the application source code, when it is inspected, then it imports no networking modules (such as socket, urllib, http, or requests) and makes no network calls.

## Out of scope
- Weight, volume, temperature, or any other non-distance conversion.
- Units other than the 8 listed (for example nautical miles, micrometers, or decimeters).
- Live internet lookups of conversion factors.
- A command-line interface.
- Any number of decimal places other than 2, or a user setting to change the precision.
- Showing unit labels, thousands separators, or scientific notation in the result.
- Saving conversion history or user preferences.
