import json
from pymavlink import mavutil

# IMPORTANT! You need to have prepared a python library, using mavgen, see:
# https://mavlink.io/en/getting_started/generate_libraries.html
#
# For example, if you have prepared an xml file called custom.xml, create lib custom.py using a command like:
# mavgen.py --lang=Python --wire-protocol=2.0 --output=custom custom.xml
#
# Once you have created custom.py you can import it:
import custom

################################################################
# Change these as required
################################################################
connection_string = 'udpin:localhost:14550'     # where the incoming mavlink stream is coming from
my_sys_id = 100                                 # any system id (1-255) other than that of the connected autopilot (in Ardupilot, param SYSID_THISMAV)
my_comp_id = 191                                # see: https://mavlink.io/en/messages/common.html#MAV_COMPONENT

# This is the message type we will be listening for, change as required
message_type = 'HEARTBEAT'

output_file = 'mavlink_log.json'
################################################################
# End of change as required, do not touch below
################################################################

# Create a connection object
connection = mavutil.mavlink_connection(connection_string, source_system=my_sys_id, source_component=my_comp_id)


# IMPORTANT! To use our own message definitions (in custom), we need to create a new MAVLink object and
# substitute it for the object that got created by mavutil.mavlink_connection
# This new object is the one that's capable of encoding/decoding our custom messages
custom_MAVLink_object = custom.MAVLink(connection, srcSystem=my_sys_id, srcComponent=my_comp_id)    # create the object passing it the existing connection
connection.mav = custom_MAVLink_object

# Wait for the first heartbeat and then let the user know that wonderful things are happening
connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))

with open(output_file, "w") as outfile:
    while True:
        # we call blocking recv_match() with a timeout so that it doesn't hang the process.
        # It will return None if no matching message received within timeout
        m = connection.recv_match(type=message_type, blocking=True, timeout=1)

        if m is None:   # no big deal, we didn't get a message in this timeout period
            continue    # just loop around and wait again
        else:
            d = {}                                      # make empty dict to store the fields of our message
            for field_name in m.fieldnames:             # loop over all message fields
                field_value =getattr(m, field_name)     # get the value of this field
                d[field_name] = field_value             # put the name/value pair in the dict

            json_string = json.dumps(d)                 # format the dict as json string
            outfile.write(json_string + '\n')           # write it to the file
            outfile.flush()                             # flush the file so that things like tail -f work properly
            print(json_string)                          # show something to the user





