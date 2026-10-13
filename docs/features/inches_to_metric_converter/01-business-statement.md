# Business statement

I need a simple UX that can convert between metric and US measurement standards. I should have drop-down values for the unit being converted from (millimeters, meters, kilometers, inches, feet, etc.) and the same options to choose the unit being converted to.

## Problem
I am traveling in Europe and need to convert measurements to what I know.

## Users
I will be the user of this simple UX.

## Desired outcome
I should be able to type in a number, pick a "from" unit and a "to" unit, and have it display the converted value. Any unit can be converted to any other unit: metric to US, US to metric, metric to metric, and US to US.

The UX is a desktop window.
The units are: millimeters, centimeters, meters, kilometers, inches, feet, yards, miles.

## Constraints
- The number entered must be greater than zero. Zero and negative numbers are not allowed.
- Results are shown rounded to 2 decimal places.

## Out of scope
- Only distance conversions for now. No weight, volume, or temperature.
- No live internet lookups; the conversion factors are built in.

## Success measures
I am able to see the converted value displayed correctly, to 2 decimal places, for every pair of units.
