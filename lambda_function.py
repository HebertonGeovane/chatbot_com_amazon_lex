import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message, response_card):
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': slot_to_elicit
            },
            'intent': {
                'name': intent_name,
                'slots': slots,
                'state': 'InProgress'
            }
        },
        'messages': [message] if message else [],
        'responseCard': response_card if response_card else None
    }

def confirm_intent(session_attributes, intent_name, slots, message, response_card):
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'ConfirmIntent'
            },
            'intent': {
                'name': intent_name,
                'slots': slots,
                'state': 'InProgress'
            }
        },
        'messages': [message] if message else [],
        'responseCard': response_card if response_card else None
    }

def close(session_attributes, fulfillment_state, message):
    # Log the fulfillment state to help diagnose issues
    logger.debug(f"Closing with fulfillment state: {fulfillment_state}")
    
    response = {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': {
                'name': 'MakeAppointment',
                'state': fulfillment_state
            },
            'messages': [message] if message else []
        }
    }

    return response

def delegate(session_attributes, slots):
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Delegate'
            },
            'intent': {
                'name': 'MakeAppointment',
                'slots': slots,
                'state': 'InProgress'
            }
        }
    }

def build_response_card(title, subtitle, options):
    """
    Build a responseCard with a title, subtitle, and an optional set of options which should be displayed as buttons.
    """
    buttons = None
    if options is not None:
        buttons = []
        for i in range(min(5, len(options))):
            buttons.append(options[i])

    return {
        'version': 1,
        'contentType': 'application/vnd.amazonaws.card.generic',
        'genericAttachments': [{
            'title': title,
            'subTitle': subtitle,
            'buttons': buttons
        }]
    }

""" --- Helper Functions --- """

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.
    """
    try:
        return func()
    except KeyError:
        return None

def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']

def get_slot(intent_request, slotName):
    print(intent_request)
    print(slotName)
    slots = get_slots(intent_request)
    print(slots)
    
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]['value']['interpretedValue']
    return None

def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']
    return {}

def increment_time_by_thirty_mins(appointment_time):
    hour, minute = list(map(int, appointment_time.split(':')))
    return '{}:00'.format(hour + 1) if minute == 30 else '{}:30'.format(hour)

def get_random_int(minimum, maximum):
    """
    Returns a random integer between min (included) and max (excluded)
    """
    min_int = math.ceil(minimum)
    max_int = math.floor(maximum)
    return random.randint(min_int, max_int - 1)

def get_availabilities(date):
    """
    Helper function which in a full implementation would feed into a backend API to provide query schedule availability.
    """
    try:
        parsed_date = dateutil.parser.parse(date)
        day_of_week = parsed_date.weekday()
        logger.debug(f"Getting availabilities for date {date}, day of week: {day_of_week}")
        
        availabilities = []
        
        # Generate some standard availability slots for all weekdays
        if day_of_week < 5:  # Monday to Friday
            # Morning slots
            availabilities.extend(['10:00', '10:30', '11:00', '11:30'])
            # Afternoon slots
            availabilities.extend(['14:00', '14:30', '15:00', '15:30', '16:00', '16:30'])
            
            logger.debug(f"Generated availabilities for {date}: {availabilities}")
            return availabilities
        else:
            logger.debug(f"No availabilities for weekend date {date}")
            return []
            
    except Exception as e:
        logger.error(f"Error generating availabilities for date {date}: {e}")
        return []

def isvalid_date(date):
    try:
        # First try parsing as ISO format
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
            return True
        except ValueError:
            # If ISO format fails, try other common formats
            return bool(dateutil.parser.parse(date))
    except (ValueError, TypeError):
        return False

def is_available(appointment_time, duration, availabilities):
    """
    Helper function to check if the given time and duration fits within a known set of availability windows.
    """
    if duration == 30:
        return appointment_time in availabilities
    elif duration == 60:
        second_half_hour_time = increment_time_by_thirty_mins(appointment_time)
        return appointment_time in availabilities and second_half_hour_time in availabilities

    raise Exception('Was not able to understand duration {}'.format(duration))

def get_duration(appointment_type):
    appointment_duration_map = {'cleaning': 30, 'root canal': 60, 'whitening': 30}
    return try_ex(lambda: appointment_duration_map[appointment_type.lower()])

def get_availabilities_for_duration(duration, availabilities):
    """
    Helper function to return the windows of availability of the given duration.
    """
    duration_availabilities = []
    start_time = '10:00'
    while start_time != '17:00':
        if start_time in availabilities:
            if duration == 30:
                duration_availabilities.append(start_time)
            elif increment_time_by_thirty_mins(start_time) in availabilities:
                duration_availabilities.append(start_time)

        start_time = increment_time_by_thirty_mins(start_time)

    return duration_availabilities

def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def validate_book_appointment(intent_request):
    appointment_type = get_slot(intent_request, 'AppointmentType')
    date = get_slot(intent_request, 'Date')
    appointment_time = get_slot(intent_request, 'Time')

    if appointment_type and not get_duration(appointment_type):
        return build_validation_result(False, 'AppointmentType', 'I did not recognize that, can I book you a root canal, cleaning, or whitening?')

    if appointment_time:
        try:
            if len(appointment_time) != 5:
                return build_validation_result(False, 'Time', 'Please provide time in HH:MM format (e.g., 10:30)')

            hour, minute = appointment_time.split(':')
            hour = parse_int(hour)
            minute = parse_int(minute)
            
            if math.isnan(hour) or math.isnan(minute):
                return build_validation_result(False, 'Time', 'Please provide a valid time in HH:MM format (e.g., 10:30)')

            if hour < 10 or hour > 16:
                return build_validation_result(False, 'Time', 'Our business hours are from 10:00 AM to 5:00 PM. What time works best for you?')

            if minute not in [30, 0]:
                return build_validation_result(False, 'Time', 'We schedule appointments every half hour (XX:00 or XX:30). What time works best for you?')
                
            # Ensure the time is properly formatted
            appointment_time = f"{hour:02d}:{minute:02d}"
            
        except Exception as e:
            logger.error(f"Error validating time {appointment_time}: {e}")
            return build_validation_result(False, 'Time', 'Please provide time in HH:MM format (e.g., 10:30)')

    if date:
        logger.debug(f"Validating date: {date}")
        if not isvalid_date(date):
            return build_validation_result(False, 'Date', 'I did not understand that, what date works best for you?')
        
        try:
            # Try to parse the date in multiple formats
            parsed_date = None
            try:
                parsed_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                parsed_date = dateutil.parser.parse(date).date()
            
            if parsed_date <= datetime.date.today():
                return build_validation_result(False, 'Date', 'Appointments must be scheduled a day in advance. Can you try a different date?')
            elif parsed_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                return build_validation_result(False, 'Date', 'Our office is not open on the weekends, can you provide a work day?')
            
            logger.debug(f"Date validation successful for: {parsed_date}")
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing date: {e}")
            return build_validation_result(False, 'Date', 'I did not understand that date format. Please provide a date like YYYY-MM-DD.')

    return build_validation_result(True, None, None)

def build_time_output_string(appointment_time):
    hour, minute = appointment_time.split(':')
    hour = int(hour)
    minute = minute.zfill(2)  # Ensure minutes are always 2 digits
    
    if hour > 12:
        return '{}:{} p.m.'.format(hour - 12, minute)
    elif hour == 12:
        return '12:{} p.m.'.format(minute)
    elif hour == 0:
        return '12:{} a.m.'.format(minute)
    else:
        return '{}:{} a.m.'.format(hour, minute)

def build_available_time_string(availabilities):
    """
    Build a string eliciting for a possible time slot among at least two availabilities.
    """
    prefix = 'We have availabilities at '
    if len(availabilities) > 3:
        prefix = 'We have plenty of availability, including '

    prefix += build_time_output_string(availabilities[0])
    if len(availabilities) == 2:
        return '{} and {}'.format(prefix, build_time_output_string(availabilities[1]))

    return '{}, {} and {}'.format(prefix, build_time_output_string(availabilities[1]), build_time_output_string(availabilities[2]))

def build_options(slot, appointment_type, date, booking_map):
    """
    Build a list of potential options for a given slot, to be used in responseCard generation.
    """
    day_strings = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    if slot == 'AppointmentType':
        return [
            {'text': 'cleaning (30 min)', 'value': 'cleaning'},
            {'text': 'root canal (60 min)', 'value': 'root canal'},
            {'text': 'whitening (30 min)', 'value': 'whitening'}
        ]
    elif slot == 'Date':
        options = []
        potential_date = datetime.date.today()
        while len(options) < 5:
            potential_date = potential_date + datetime.timedelta(days=1)
            if potential_date.weekday() < 5:
                options.append({
                    'text': '{}-{} ({})'.format((potential_date.month), potential_date.day, day_strings[potential_date.weekday()]),
                    'value': potential_date.strftime('%Y-%m-%d')
                })
        return options
    elif slot == 'Time':
        if not appointment_type or not date:
            return None

        availabilities = try_ex(lambda: booking_map[date])
        if not availabilities:
            return None

        availabilities = get_availabilities_for_duration(get_duration(appointment_type), availabilities)
        if len(availabilities) == 0:
            return None

        options = []
        for i in range(min(len(availabilities), 5)):
            options.append({'text': build_time_output_string(availabilities[i]), 'value': availabilities[i]})

        return options

def make_appointment(intent_request):
    """
    Performs dialog management and fulfillment for booking a dentist appointment.
    """
    # Debug the entire intent request to see what's happening
    logger.debug(f"FULL INTENT REQUEST: {json.dumps(intent_request)}")
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    
    appointment_type = get_slot(intent_request, 'AppointmentType')
    date = get_slot(intent_request, 'Date')
    appointment_time = get_slot(intent_request, 'Time')
    
    logger.debug(f"Processing appointment request - Type: {appointment_type}, Date: {date}, Time: {appointment_time}")
    
    # Convert date to standard format if needed
    if date:
        try:
            parsed_date = dateutil.parser.parse(date)
            date = parsed_date.strftime('%Y-%m-%d')
            logger.debug(f"Standardized date format: {date}")
        except Exception as e:
            logger.error(f"Error parsing date {date}: {e}")
    
    source = intent_request.get('invocationSource')
    logger.debug(f"Invocation source in make_appointment: {source}")
    booking_map = json.loads(session_attributes.get('bookingMap', '{}'))

    if source == 'DialogCodeHook':
        validation_result = validate_book_appointment(intent_request)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                session_attributes,
                'MakeAppointment',
                slots,
                validation_result['violatedSlot'],
                validation_result['message'],
                build_response_card(
                    'Specify {}'.format(validation_result['violatedSlot']),
                    validation_result['message']['content'],
                    build_options(validation_result['violatedSlot'], appointment_type, date, booking_map)
                )
            )

        if not appointment_type:
            return elicit_slot(
                session_attributes,
                'MakeAppointment',
                slots,
                'AppointmentType',
                {'contentType': 'PlainText', 'content': 'What type of appointment would you like to schedule?'},
                build_response_card(
                    'Specify Appointment Type',
                    'What type of appointment would you like to schedule?',
                    build_options('AppointmentType', appointment_type, date, None)
                )
            )

        if appointment_type and not date:
            return elicit_slot(
                session_attributes,
                'MakeAppointment',
                slots,
                'Date',
                {'contentType': 'PlainText', 'content': 'When would you like to schedule your {}?'.format(appointment_type)},
                build_response_card(
                    'Specify Date',
                    'When would you like to schedule your {}?'.format(appointment_type),
                    build_options('Date', appointment_type, date, None)
                )
            )

        if appointment_type and date:
            # Ensure we have a consistent date format for the booking map
            try:
                parsed_date = dateutil.parser.parse(date).strftime('%Y-%m-%d')
                logger.debug(f"Parsed date for availability check: {parsed_date}")
                
                # Get or generate availabilities
                booking_availabilities = booking_map.get(parsed_date)
                if booking_availabilities is None:
                    booking_availabilities = get_availabilities(date)  # Use original date string
                    if booking_availabilities:  # Only store if we got availabilities
                        booking_map[parsed_date] = booking_availabilities
                        session_attributes['bookingMap'] = json.dumps(booking_map)
                    
                logger.debug(f"Retrieved availabilities for date {parsed_date}: {booking_availabilities}")
                
            except (ValueError, TypeError) as e:
                logger.error(f"Error processing date {date}: {e}")
                return elicit_slot(
                    session_attributes,
                    'MakeAppointment',
                    slots,
                    'Date',
                    {'contentType': 'PlainText', 'content': 'I had trouble understanding that date. Please provide a date in YYYY-MM-DD format.'},
                    build_options('Date', appointment_type, None, None)
                )

            appointment_type_availabilities = get_availabilities_for_duration(get_duration(appointment_type), booking_availabilities)
            if len(appointment_type_availabilities) == 0:
                slots['Date'] = None
                slots['Time'] = None
                return elicit_slot(
                    session_attributes,
                    'MakeAppointment',
                    slots,
                    'Date',
                    {'contentType': 'PlainText', 'content': 'We do not have any availability on that date, is there another day which works for you?'},
                    build_response_card(
                        'Specify Date',
                        'What day works best for you?',
                        build_options('Date', appointment_type, date, booking_map)
                    )
                )

            message_content = 'What time on {} works for you? '.format(date)
            if appointment_time:
                session_attributes['formattedTime'] = build_time_output_string(appointment_time)
                if is_available(appointment_time, get_duration(appointment_type), booking_availabilities):
                    return delegate(session_attributes, slots)
                message_content = 'The time you requested is not available. '

            if len(appointment_type_availabilities) == 1:
                slots['Time'] = appointment_type_availabilities[0]
                return confirm_intent(
                    session_attributes,
                    'MakeAppointment',
                    slots,
                    {
                        'contentType': 'PlainText',
                        'content': '{}{} is our only availability, does that work for you?'.format(
                            message_content, build_time_output_string(appointment_type_availabilities[0]))
                    },
                    build_response_card(
                        'Confirm Appointment',
                        'Is {} on {} okay?'.format(build_time_output_string(appointment_type_availabilities[0]), date),
                        [{'text': 'yes', 'value': 'yes'}, {'text': 'no', 'value': 'no'}]
                    )
                )

            available_time_string = build_available_time_string(appointment_type_availabilities)
            return elicit_slot(
                session_attributes,
                'MakeAppointment',
                slots,
                'Time',
                {'contentType': 'PlainText', 'content': '{}{}'.format(message_content, available_time_string)},
                build_response_card(
                    'Specify Time',
                    'What time works best for you?',
                    build_options('Time', appointment_type, date, booking_map)
                )
            )

        return delegate(session_attributes, slots)

    # Only proceed with booking if this is a fulfillment request
    if source != 'FulfillmentCodeHook':
        logger.debug("Not a fulfillment request, returning delegate response")
        return delegate(session_attributes, slots)
        
    # Book the appointment
    if not appointment_type or not date or not appointment_time:
        return close(
            session_attributes,
            'Failed',
            {
                'contentType': 'PlainText',
                'content': 'Please provide all required information: appointment type, date, and time.'
            }
        )
        
    duration = get_duration(appointment_type)
    try:
        # Ensure we have valid time format
        hour, minute = appointment_time.split(':')
        appointment_time = f"{int(hour):02d}:{int(minute):02d}"
        
        parsed_date = dateutil.parser.parse(date).strftime('%Y-%m-%d')
        booking_availabilities = booking_map.get(parsed_date, [])
        logger.debug(f"Retrieved booking availabilities for date {parsed_date}: {booking_availabilities}")
    except (ValueError, TypeError) as e:
        logger.error(f"Error processing date/time for booking: {e}")
        return close(
            session_attributes,
            'Failed',
            {
                'contentType': 'PlainText',
                'content': 'I encountered an error while trying to book your appointment. Please try again with a valid date and time.'
            }
        )

    if booking_availabilities:
        booking_availabilities.remove(appointment_time)
        if duration == 60:
            second_half_hour_time = increment_time_by_thirty_mins(appointment_time)
            booking_availabilities.remove(second_half_hour_time)

        booking_map[date] = booking_availabilities
        session_attributes['bookingMap'] = json.dumps(booking_map)
    else:
        logger.debug('Availabilities for {} were null at fulfillment time.'.format(date))

    # Only return Fulfilled for FulfillmentCodeHook
    if source == 'FulfillmentCodeHook':
        return close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'Okay, I have booked your {} appointment. We will see you at {} on {}'.format(
                    appointment_type.lower(), build_time_output_string(appointment_time), date)
            }
        )
    else:
        # For any other source, return InProgress
        return close(
            session_attributes,
            'InProgress',
            {
                'contentType': 'PlainText',
                'content': 'Processing your appointment request for {} at {} on {}.'.format(
                    appointment_type.lower(), build_time_output_string(appointment_time), date)
            }
        )

def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    import time
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    
    logger.debug('event={}'.format(json.dumps(event)))

    # Check if this is a dialog code hook or fulfillment
    source = event.get('invocationSource')
    logger.debug(f"Invocation source: {source}")
    
    response = make_appointment(event)
    
    # Debug the response type
    logger.debug(f"Response type: {response.get('sessionState', {}).get('dialogAction', {}).get('type')}")
    logger.debug(f"Intent state: {response.get('sessionState', {}).get('intent', {}).get('state')}")
    
    # If the intent is fulfilled or failed, ensure we return a detailed message
    if ('sessionState' in response and 
        'intent' in response['sessionState']):
        
        intent_state = response['sessionState']['intent'].get('state')
        
        if intent_state == 'Failed':
            response['sessionState']['messages'] = [{
                'contentType': 'PlainText',
                'content': 'I apologize, but I was unable to book your appointment. Please try again with a different time or date, or contact our office directly at (555) 123-4567 for assistance.'
            }]
        elif intent_state == 'ReadyForFulfillment':
            # Only add the confirmation message if this is a fulfillment request
            if event.get('invocationSource') == 'FulfillmentCodeHook':
                
                # Get the appointment details from the slots
                slots = event['sessionState']['intent']['slots']
                appointment_type = slots['AppointmentType']['value']['interpretedValue']
                date = slots['Date']['value']['interpretedValue']
                time = slots['Time']['value']['interpretedValue']
                
                # Format the time nicely
                formatted_time = build_time_output_string(time)
                
                # Return a more detailed confirmation message
                response['sessionState']['messages'] = [{
                    'contentType': 'PlainText',
                    'content': f'Perfect! Your {appointment_type} appointment has been confirmed for {formatted_time} on {date}. We look forward to seeing you! Please arrive 10 minutes before your appointment time.'
                }]
    
    return response