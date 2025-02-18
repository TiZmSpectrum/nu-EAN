from Globals import globalServerStartID
from Globals import globalServerGameIDGen
#from Globals import globalServerLobbyIDGen
from Globals import Clients
from Utilities.Packet import Packet
import configparser

def HandleStatus(self, data): # TODO - figure out more of actual status calls
    toSend.set("PacketData", "TXN", "Status")
    Packet(toSend).send(self, "pnow", 0x80000000, self.CONNOBJ.plasmaPacketID)

def HandleStart(self, data): # TODO - Add PlayNow matchmaking handling here... Currently stubbed out with predef. values
    global globalServerGameIDGen 
    global globalServerStartID
    #global globalServerLobbyIDGen
    
    globalServerGameIDGen += 1
    globalServerStartID += 1
    #globalServerLobbyIDGen += 1
    
    # TODO - FIGURE OUT HOW THE WEIGHTS AND TABLE SHENANIGANS WORK
    
 #   # relevant pnow data the game sends in the first request
 #   # PossibleValues = 0,1  //Off, On
 #   filter-matchmaking_state = data.get("PacketData", "players.0.props.{filter-matchmaking_state}")
 #   filter-game_type = data.get("PacketData", "players.0.props.{filter-game_type}") # PossibleValues = 0,1,2 //ranked, unranked, co_op
 #   poolMaxPlayers = data.get("PacketData", "players.0.props.{poolMaxPlayers}")
 #   # preferences provided by the asking player
 #   pref-team_play = data.get("PacketData", "players.0.props.{pref-team_play}") # StringPreference / Labels = 0, 1, ABSTAIN //crew, solo
 #   pref-car_tier = data.get("PacketData", "players.0.props.{pref-car_tier}") # StringPreference / Labels = 1, 2, 3, ABSTAIN
 #   pref-game_mode = data.get("PacketData", "players.0.props.{pref-game_mode}") # StringPreference / Labels = 1, 0, 5, 13, 15, 14, ABSTAIN //Labels = circuit, sprint, speedtrap, canyon duel, pursuit_knockout, pursuit_tag, ABSTAIN
 #   pref-player_dnf = data.get("PacketData", "players.0.props.{pref-player_dnf}") # IntegerPreference
 #   pref-max_online_player = data.get("PacketData", "players.0.props.{pref-max_online_player}") # IntegerPreference 
 #   pref-n2o = data.get("PacketData", "players.0.props.{pref-n2o}") # StringPreference / Labels = 0, 1, ABSTAIN //off, on
 #   pref-collision_detection = data.get("PacketData", "players.0.props.{pref-collision_detection}") # StringPreference / Labels = 0, 1, ABSTAIN //off, on
 #   pref-race_type_sprint = data.get("PacketData", "players.0.props.{pref-race_type_sprint}")
 #   pref-race_type_pursuit_tag = data.get("PacketData", "players.0.props.{pref-race_type_pursuit_tag}")
 #   pref-race_type_speedtrap = data.get("PacketData", "players.0.props.{pref-race_type_speedtrap}")
 #   pref-race_type_canyon_due = data.get("PacketData", "players.0.props.{pref-race_type_canyon_due}")
 #   pref-race_type_circuit = data.get("PacketData", "players.0.props.{pref-race_type_circuit}")
 #   pref-race_type_knockout = data.get("PacketData", "players.0.props.{pref-race_type_knockout}")
 #   pref-length = data.get("PacketData", "players.0.props.{pref-length}") # StringPreference / Labels = 1, 2, 3, 4, ABSTAIN //short, medium, long, verylong
 #   pref-help_type = data.get("PacketData", "players.0.props.{pref-help_type}") # StringPreference / Labels = 0, 1, 2, 3 //Labels = no_help, help_in_career, help_in_challenge, help_either
 #   pref-skill = data.get("PacketData", "players.0.props.{pref-skill}") # IntegerPreference
 #   # StringPreference / Labels = nfs-wc, nfs-ec, nfs-eu
 #   pref-location = data.get("PacketData", "players.0.props.{pref-location}")
    toSend = Packet().create()
    toSend.set("PacketData", "TXN", "Start")
    toSend.set("PacketData", "id.id", str(globalServerStartID))
    toSend.set("PacketData", "id.partition", "/eagames/NFS-2007")
    Packet(toSend).send(self, "pnow", 0x80000000, self.CONNOBJ.plasmaPacketID)
    
    # start Status packet here
    toSend = Packet().create()
    toSend.set("PacketData", "sessionState", "COMPLETE")
    toSend.set("PacketData", "props.{avgFit}", "1.0")
    toSend.set("PacketData", "props.{games}.[]", "1")
    toSend.set("PacketData", "props.{games}.0.gid", str(globalServerGameIDGen))
    
    toSend.set("PacketData", "TXN", "Status")
    toSend.set("PacketData", "props.{}", "3") # total count of props?
    toSend.set("PacketData", "props.{games}.0.lid", "1")   # apparently BFBC2 server supports only 1 lobby?
    toSend.set("PacketData", "props.{resultType}", "JOIN") # resultType can also be NOSERVER if none are found
    toSend.set("PacketData", "id.id", str(globalServerStartID))
    toSend.set("PacketData", "id.partition", "/eagames/NFS-2007")
    
    # setup host client / server
    self.CONNOBJ.serverData = ConfigParser()
    self.CONNOBJ.serverData.optionxform = str
    self.CONNOBJ.serverData.add_section("ServerData")
    
    self.CONNOBJ.serverData.set("ServerData", "LID", "1")
    self.CONNOBJ.serverData.set("ServerData", "GID", str(globalServerGameIDGen))
    self.CONNOBJ.serverData.set("ServerData", "PORT", "19018") # not sure if this is constant...
    self.CONNOBJ.serverData.set("ServerData", "INT-PORT", "19018")
    # PREDEFINED VALUES HERE - this is to be read from the PlayNow packet
    self.CONNOBJ.serverData.set("ServerData", "UGID", "4e26106f-8c56-48bd-8615-824d41051c9a") # TODO GENERATE THIS
    self.CONNOBJ.serverData.set("ServerData", "ACTIVE-PLAYERS", "0")
    self.CONNOBJ.serverData.set("ServerData", "MAX-PLAYERS", "8")
    self.CONNOBJ.serverData.set("ServerData", "JOINING-PLAYERS", "1")
    self.CONNOBJ.serverData.set("ServerData", "NAME", "NA2CarbonPC-02-019")
    self.CONNOBJ.serverData.set("ServerData", "TYPE", "G")
    self.CONNOBJ.serverData.set("ServerData", "JOIN", "O")
    self.CONNOBJ.serverData.set("ServerData", "B-version", "298_prod_server+22012b18")
    self.CONNOBJ.serverData.set("ServerData", "B-U-version", "298_prod_server+22012b18")
    self.CONNOBJ.serverData.set("ServerData", "B-U-matchmaking_state", "1")
    self.CONNOBJ.serverData.set("ServerData", "B-U-team_play", "1")
    self.CONNOBJ.serverData.set("ServerData", "B-U-car_tier", "3")
    self.CONNOBJ.serverData.set("ServerData", "B-U-game_mode", "1")
    self.CONNOBJ.serverData.set("ServerData", "B-U-player_dnf", "12")
    self.CONNOBJ.serverData.set("ServerData", "B-U-max_online_player", "8")
    self.CONNOBJ.serverData.set("ServerData", "B-U-n2o", "1")
    self.CONNOBJ.serverData.set("ServerData", "B-U-track", "")
    self.CONNOBJ.serverData.set("ServerData", "B-U-collision_detection", "1")
    self.CONNOBJ.serverData.set("ServerData", "B-U-race_type_sprint", "ct.4.2")
    self.CONNOBJ.serverData.set("ServerData", "B-U-race_type_pursuit_tag", "qr.6.1")
    self.CONNOBJ.serverData.set("ServerData", "B-U-race_type_speedtrap", "mu.2.2")
    self.CONNOBJ.serverData.set("ServerData", "B-U-skill", "500")
    self.CONNOBJ.serverData.set("ServerData", "B-U-game_type", "1")
    self.CONNOBJ.serverData.set("ServerData", "B-U-race_type_canyon_due", "qr.3.3")
    self.CONNOBJ.serverData.set("ServerData", "B-U-race_type_circuit", "ex.5.1")
    self.CONNOBJ.serverData.set("ServerData", "B-U-race_type_knockout", "qr.5.1")
    self.CONNOBJ.serverData.set("ServerData", "B-U-length", "2")
    self.CONNOBJ.serverData.set("ServerData", "B-U-help_type", "0")

    Packet(toSend).send(self, "pnow", 0x80000000, 0)
    

def ReceivePacket(self, data, txn):
    if txn == 'Start':
        HandleStart(self, data)
    elif txn == 'Status':
        HandleStatus(self)
   # elif txn == 'Ping':
   #     HandlePing(self)
   # elif txn == 'Goodbye':
   #     HandleGoodbye(self, data)
   # elif txn == 'GetPingSites':
   #     HandleGetPingSites(self)
    else:
        self.logger_err.new_message("[" + self.ip + ":" + str(self.port) + ']<-- Got unknown pnow message (' + txn + ")", 2)
