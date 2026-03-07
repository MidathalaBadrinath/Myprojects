# recommendation.py

def generate_recommendation(failure_type, flight_type, flight_number, remaining_hours):
    recommendations = {
        'Turbine Overheat': {
            'cause': 'Excessive temperature causing the turbine blade to overheat.',
            'commercial': 'This could cause a delay in commercial flights, which affects operational schedules.',
            'cargo': 'For cargo flights, overheating may lead to costly downtime. Immediate repair is required.',
            'private': 'Turbine overheat could be risky for private flights; repair should be done quickly.',
            'long-haul': 'Long-haul flights are particularly sensitive to turbine overheat; prioritize cooling and inspection.',
            'short-haul': 'Immediate attention is needed to avoid delays in frequent short-haul flights.'
        },
        'Pressure Loss': {
            'cause': 'Possible leakage or malfunction in the hydraulic system causing a drop in pressure.',
            'commercial': 'Pressure loss in a commercial flight could lead to an emergency, causing delays or cancellations.',
            'cargo': 'For cargo flights, pressure loss may compromise operational safety. Immediate repairs are needed.',
            'private': 'For private flights, pressure loss can affect safety, and quick repairs should be made.',
            'long-haul': 'Long-haul flights require constant pressure levels. Any pressure loss should be dealt with urgently.',
            'short-haul': 'Pressure loss on short-haul flights can impact quick turnaround times, repair immediately.'
        },
        'Valve Stuck': {
            'cause': 'Accumulation of debris or wear in the control valve causing it to become stuck.',
            'commercial': 'A stuck valve in a commercial flight could cause operational delays and needs immediate attention.',
            'cargo': 'For cargo flights, valve issues still require prompt attention for safety.',
            'private': 'A stuck valve in private flights can be a major safety issue, repair it before the next flight.',
            'long-haul': 'For long-haul flights, any malfunction should be prioritized to prevent failures during critical phases.',
            'short-haul': 'A stuck valve can severely impact short-haul flight operations; repair before the next flight.'
        },
        'Fuel Leakage': {
            'cause': 'Leakage in the fuel system due to a crack or defect in the fuel line.',
            'commercial': 'Fuel leakage in commercial flights is a high priority and should be repaired immediately to avoid fuel wastage.',
            'cargo': 'For cargo flights, fuel leakage impacts operational efficiency and can cause safety issues.',
            'private': 'Fuel leakage in private flights can be dangerous, and quick repair is critical for safe operation.',
            'long-haul': 'Long-haul flights require more fuel, making leakage highly disruptive and dangerous.',
            'short-haul': 'Fuel leakage in short-haul flights impacts efficiency and safety, repair it immediately.'
        },
        'Seal Failure': {
            'cause': 'Worn-out seals allowing fluid or air leakage.',
            'commercial': 'Seal failure can affect commercial flight systems, and urgent maintenance is recommended.',
            'cargo': 'For cargo flights, seal failure may reduce safety and needs fixing before further operation.',
            'private': 'Private flights with seal failure should be grounded for immediate repairs to ensure safety.',
            'long-haul': 'Long-haul flights should not operate with seal failures due to potential system failures over extended hours.',
            'short-haul': 'For short-haul flights, sealing issues should be handled swiftly to avoid recurrent problems.'
        },
        'Oil Leakage': {
            'cause': 'Wear or damage in the oil pump leading to oil leakage.',
            'commercial': 'Oil leakage in commercial aircraft could lead to operational failure; immediate action is necessary.',
            'cargo': 'Cargo flights with oil leakage should be grounded for immediate repair to ensure safety.',
            'private': 'Private flights are more susceptible to oil leakage. Immediate repair is necessary to avoid engine damage.',
            'long-haul': 'Long-haul flights require stable oil levels. Repair oil leakage immediately to prevent engine failure.',
            'short-haul': 'Oil leakage in short-haul flights can delay operations; repair the issue before the next departure.'
        },
        'None': {
            'cause': 'No issues detected with the part.',
            'commercial': 'All systems functioning, no issues. Continue regular maintenance checks.',
            'cargo': 'No issues detected, safe for cargo flights.',
            'private': 'No issues, safe for private flights.',
            'long-haul': 'Everything functioning as expected for long-haul flights.',
            'short-haul': 'Systems are operational for short-haul flights.'
        }
    }


    cause = recommendations.get(failure_type, {}).get('cause', 'Unknown cause')
    flight_recommendation = recommendations.get(failure_type, {}).get(flight_type, 'No specific recommendation for this flight type.')

    return f"Flight {flight_number}: {cause}\nRecommendation for {flight_type.capitalize()} flight: {flight_recommendation}\nPredicted Remaining Operational Hours: {remaining_hours} hours"
