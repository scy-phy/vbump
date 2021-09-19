from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()


class Tutorial (object):
    """
    A Tutorial object is created for each switch that connects.
    A Connection object for that switch is passed to the __init__ function.
    """
    def __init__ (self, connection):
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)

        # Use this table to keep track of which ethernet address is on
        # which switch port (keys are MACs, values are ports).
        self.mac_to_port = {}


    def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)
    
    # Send message to switch
    self.connection.send(msg)

    
    def switch_VLAN (self, packet, packet_in):
    """
    Implement switch-like behavior with support for VLANs.
    """
    # We use the VLAN ID to identify the original source switch port.
    # We need a rule to which destination should be forwarded. If
    # target MAC is given, we should verify access, set VLAN tag
    # correctly, and forward to the outgoing trunk port (which might
    # be connected to transparent firewall? Or should the firewall
    # come first? Or both).

    # Lets assume the policing/limitations in terms of MACs is done by firewall
    # Need list of MAC per VLAN_ID List map of source ID
    # to set of target IDs we then need to check in which target ID
    # the target MAC is if target MAC is

    # The SDN will just forward incoming VLAN ID to one or more target VLANs

    # If broadcast MAC, we need to know target VLAN(s)
    # to which we need to copy/duplicate the packets So what kind of
    # datastructures? 
    # match.dl_type = p.eth_type
    # match.dl_vlan = p.id

    # Hard-coded access for now
    access = {1:[1,2,3]}

    # we also 
    if isinstance(packet, vlan):
        if not p.id in access:
            print("Source VLAN ID %d not in DB",p.id)
        else:
            msg = of.ofp_flow_mod()
            msg.match.in_port = p.id
            for i in access[p.id]:
                msg.actions.append(of.ofp_action_output(port = packet_in.in_port, id = i))
            msg.match = of.ofp_match.from_packet(packet)
            self.connection.send(msg)    

    else:
        print("No VLAN header found, ignored")

    
    def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
        log.warning("Ignoring incomplete packet")
        return
    
    packet_in = event.ofp # The actual ofp_packet_in message.
    self.switch_VLAN(packet, packet_in)


def launch ():
    def start_switch (event):
        log.debug("Controlling %s" % (event.connection,))
        Tutorial(event.connection)
        core.openflow.addListenerByName("ConnectionUp", start_switch)
            
