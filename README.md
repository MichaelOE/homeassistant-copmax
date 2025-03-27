# homeassistant-copmax

Work in progress... expect bugs/missing stuff/changes

## Target
Integration for Home Assistant to connect to Copmax Heat pumps.
Tested towards Copmax AW 10KW (approx. year 2009).

## Connection
The heat pump is controlled by a Siemens RWR470.10 controller.
Also a remote display is connected to controllers 'RS 485' connector.

I removed the display and added a [TCP-RTU modbus adapter](https://www.pusr.com/products/modbus-serial-to-ethernet-converters-usr-tcp232-410s.html) instead.
This adapter allows for connecting to the heat pump over ethernet.

Connector of the controller and adapter:

<img src="https://github.com/user-attachments/assets/da8f5547-809c-43b8-8874-f2c31d6d06e2" width="250" title="Screenshot"/>
<img src="https://github.com/user-attachments/assets/87dea387-ab33-4767-9b4a-06186ca33a18" width="250" title="Screenshot"/>

These just to be connected A<->A, B<->B and GND<->GND

The controller is running 9600,8,N,1

## Method
The controller uses Modbus for communication.

## Credits
Information in [this thread](https://stokerpro.dk/viewtopic.php?style=19&t=26511&start=50) was a **BIG** help in the development.


[HW comm info](https://stokerpro.dk/viewtopic.php?style=19&p=353534#p353534)

[Register list](https://stokerpro.dk/viewtopic.php?style=19&p=362766#p362766)

[Register info](https://stokerpro.dk/viewtopic.php?style=19&p=363554#p363554)
