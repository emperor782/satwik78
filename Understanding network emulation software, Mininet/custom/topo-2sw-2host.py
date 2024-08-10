"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        firstleftHost = self.addHost( 'h1' )
        firstrightHost = self.addHost( 'h2' )
        secondleftHost = self.addHost( 'h3' )
        secondmiddleHost = self.addHost( 'h4' )
        secondrightHost = self.addHost( 'h5' )
        thirdleftHost = self.addHost( 'h6' )
        thirdmiddleHost = self.addHost( 'h7' )
        thirdrightHost = self.addHost( 'h8' )
        firstSwitch = self.addSwitch( 's1' )
        secondSwitch = self.addSwitch( 's2' )
        thirdSwitch = self.addSwitch( 's3' )

        # Add links
        self.addLink( firstleftHost, firstSwitch )
        self.addLink( firstrightHost, firstSwitch )
        self.addLink( secondleftHost, secondSwitch )
        self.addLink( secondmiddleHost, secondSwitch )
        self.addLink( secondrightHost, secondSwitch )
        self.addLink( thirdleftHost, thirdSwitch )
        self.addLink( thirdmiddleHost, thirdSwitch )
        self.addLink( thirdrightHost, thirdSwitch )
        self.addLink( firstSwitch, secondSwitch )
        self.addLink( secondSwitch, thirdSwitch )


topos = { 'mytopo': ( lambda: MyTopo() ) }
