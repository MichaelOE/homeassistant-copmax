# homeassistant-copmax

Work in progress... expect bugs/missing stuff/changes

Integration for Home Assistant to connect to Copmax Heat pumps.
Tested towards Copmax AW 10KW (approx. year 2009).

The heat pump is controlled by a Siemens RWR470.10 controller.
Also a remote display is connected to controllers 'RS 485' connector.

I removed the display and added a [TCP-RTU modbus adapter](https://www.pusr.com/products/modbus-serial-to-ethernet-converters-usr-tcp232-410s.html) instead.
This adapter allows for connecting to the heat pump over ethernet.
